"""
Kapture Oracle Service - Independent API

This is a standalone service that verifies work and submits hours to blockchain.
Acts as neutral third party between employers and employees.

Run with: python3 oracle_service/app.py
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
import sys
from datetime import datetime, timedelta

# Add parent directory to path to import loggerheads modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loggerheads.blockchain import submit_hours, get_vault_info, derive_vault_pda
from loggerheads.oracle_secure import get_oracle_keypair
from solders.pubkey import Pubkey

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests

# Initialize rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per hour"],  # Global rate limit
    storage_uri="memory://"
)


def verify_work_proof(proof: dict, hours: float) -> None:
    """
    Verify work proof is legitimate.

    The oracle verifies the employee's proof (screenshots) matches their claimed hours.
    This is separate from the employer's target hours (checked by smart contract).

    Screenshots are taken every 10 seconds during active work.
    Theoretical max: 360 screenshots/hour (no breaks)
    Practical with breaks: 200-300 screenshots/hour

    Checks:
    1. Screenshot count is reasonable for claimed hours
    2. Timestamps are consistent with time span
    3. Submission is recent (within 48 hours)

    Args:
        proof: Work proof dict with screenshot_count, first/last timestamps
        hours: Claimed hours worked (calculated from screenshots)

    Raises:
        ValueError: If proof is invalid
    """
    # Check screenshot count
    screenshot_count = proof.get('screenshot_count', 0)
    if screenshot_count == 0:
        raise ValueError("No screenshots provided")

    # Lenient check: At least 60 screenshots per hour
    # (allows for significant idle time while catching obvious fraud)
    expected_min_screenshots = max(int(hours * 250), 1)
    if screenshot_count < expected_min_screenshots:
        raise ValueError(
            f"Too few screenshots: {screenshot_count} for {hours} hours "
            f"(expected at least {expected_min_screenshots})"
        )

    # Check timestamps if provided
    first_time_str = proof.get('first_screenshot_time')
    last_time_str = proof.get('last_screenshot_time')

    if first_time_str and last_time_str:
        try:
            first_time = datetime.fromisoformat(first_time_str)
            last_time = datetime.fromisoformat(last_time_str)

            # Calculate time span
            time_span = (last_time - first_time).total_seconds() / 3600  # hours

            # Time span should be reasonable (allow 50% variance for breaks/idle time)
            # Example: 8 hours worked might span 10-12 hours of calendar time
            if abs(time_span - hours) > (hours * 0.5):
                raise ValueError(
                    f"Time span ({time_span:.1f}h) doesn't match claimed hours ({hours}h)"
                )

            # Check submission is recent (within 48 hours)
            now = datetime.now()
            age = (now - last_time).total_seconds() / 3600  # hours
            if age > 48:
                raise ValueError(f"Submission too old: {age:.1f} hours")

        except (ValueError, TypeError) as e:
            if "Submission too old" in str(e) or "doesn't match" in str(e):
                raise
            # If timestamp parsing fails, just skip timestamp validation
            pass

    # Check work quality (if provided)
    work_percentage = proof.get('work_percentage')
    if work_percentage is not None:
        # Require at least 50% work-related activity
        if work_percentage < 50:
            raise ValueError(
                f"Work quality too low: {work_percentage}% work-related activity "
                f"(minimum 50% required)"
            )

        # Warn if suspiciously high non-work activity
        non_work_screenshots = proof.get('non_work_screenshots', 0)
        total_screenshots = proof.get('screenshot_count', 1)
        if non_work_screenshots > total_screenshots * 0.6:  # More than 60% non-work
            raise ValueError(
                f"Too much non-work activity: {non_work_screenshots}/{total_screenshots} screenshots "
                f"({100 - work_percentage}% non-work)"
            )

    # Check liveness checks (if provided)
    liveness_checks = proof.get('liveness_checks', [])
    if liveness_checks:
        failed_checks = [c for c in liveness_checks if not c.get('face_detected', False)]
        total_checks = len(liveness_checks)

        # Allow up to 40% failures (bathroom breaks, etc)
        if len(failed_checks) > total_checks * 0.4:
            raise ValueError(
                f"Too many liveness check failures: {len(failed_checks)}/{total_checks} "
                f"({int(len(failed_checks)/total_checks*100)}% failed, maximum 40% allowed)"
            )

        # Calculate average confidence for passed checks
        passed_checks = [c for c in liveness_checks if c.get('face_detected', False)]
        if passed_checks:
            avg_confidence = sum(c.get('confidence', 0) for c in passed_checks) / len(passed_checks)
            # Require reasonable confidence
            if avg_confidence < 0.5:
                raise ValueError(
                    f"Liveness confidence too low: {avg_confidence:.2f} "
                    f"(minimum 0.5 required)"
                )

# Load oracle keypair on startup
try:
    ORACLE = get_oracle_keypair()
    ORACLE_PUBKEY = str(ORACLE.pubkey())
    print(f"✅ Oracle loaded: {ORACLE_PUBKEY}")
except Exception as e:
    print(f"❌ Failed to load oracle keypair: {e}")
    print("\nGenerate oracle keypair:")
    print("  python3 -m loggerheads.oracle_secure --generate")
    sys.exit(1)


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'oracle_pubkey': ORACLE_PUBKEY,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/oracle-pubkey', methods=['GET'])
def get_oracle_pubkey():
    """
    Get oracle public key.

    Employers use this when creating vaults to specify which oracle they trust.
    """
    return jsonify({
        'oracle_pubkey': ORACLE_PUBKEY
    })


@app.route('/submit-hours', methods=['POST'])
@limiter.limit("2 per day")  # One submission per day + one retry if needed
def submit_hours_endpoint():
    """
    Submit work hours to blockchain.

    Expected JSON body:
    {
        "employee_wallet": "...",
        "admin_wallet": "...",
        "hours": 8,
        "proof": {
            "screenshot_count": 24,
            "first_screenshot_time": "...",
            "last_screenshot_time": "...",
            "work_summary": "..."
        }
    }

    Returns:
    {
        "success": true,
        "transaction_signature": "...",
        "vault_status": {
            "unlocked_amount": ...,
            "locked_amount": ...
        }
    }
    """
    try:
        data = request.get_json()

        # Validate required fields
        required = ['employee_wallet', 'admin_wallet', 'hours']
        for field in required:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400

        employee_wallet = data['employee_wallet']
        admin_wallet = data['admin_wallet']
        hours = data['hours']
        proof = data.get('proof', {})

        # Validate wallet addresses
        try:
            Pubkey.from_string(employee_wallet)
            Pubkey.from_string(admin_wallet)
        except (ValueError, Exception) as e:
            # Log the exception for debugging
            print(f"⚠️  Invalid wallet address: {e}")
            return jsonify({
                'success': False,
                'error': 'Invalid wallet address format'
            }), 400

        # Validate hours
        if not isinstance(hours, (int, float)) or hours < 0 or hours > 24:
            return jsonify({
                'success': False,
                'error': 'Hours must be between 0 and 24'
            }), 400

        # Verify work proof
        try:
            verify_work_proof(proof, hours)
            print(f"   ✓ Work proof verified")
        except ValueError as e:
            print(f"   ❌ Work proof verification failed: {e}")
            return jsonify({
                'success': False,
                'error': f'Work proof verification failed: {str(e)}'
            }), 400

        print(f"\n📥 Submission received:")
        print(f"   Employee: {employee_wallet[:16]}...{employee_wallet[-8:]}")
        print(f"   Admin: {admin_wallet[:16]}...{admin_wallet[-8:]}")
        print(f"   Hours: {hours}")
        print(f"   Proof: {proof}")

        # Check if vault exists
        vault_pda, _ = derive_vault_pda(
            Pubkey.from_string(employee_wallet),
            Pubkey.from_string(admin_wallet)
        )

        vault_info = get_vault_info(vault_pda)
        if not vault_info:
            return jsonify({
                'success': False,
                'error': 'Vault not found. Employer must create vault first.'
            }), 404

        # Verify this oracle is trusted by the vault
        if vault_info['oracle'] != ORACLE_PUBKEY:
            return jsonify({
                'success': False,
                'error': f'Vault trusts different oracle: {vault_info["oracle"]}'
            }), 403

        print(f"   ✓ Vault verified")
        print(f"   ✓ Oracle authorized")

        # Round hours for blockchain (expects integer)
        hours_rounded = int(round(hours))

        print(f"\n📤 Submitting {hours_rounded} hours to blockchain...")

        # Submit to blockchain (oracle signs transaction)
        signature = submit_hours(
            hours_rounded,
            employee_wallet,
            admin_wallet,
            None  # Uses loaded oracle keypair
        )

        print(f"   ✅ Transaction confirmed: {signature}")

        # Get updated vault status
        vault_info_after = get_vault_info(vault_pda)

        response = {
            'success': True,
            'transaction_signature': signature,
            'hours_submitted': hours_rounded,
            'vault_status': {
                'unlocked_amount': vault_info_after['unlocked_amount'] / 1_000_000,
                'locked_amount': vault_info_after['locked_amount'] / 1_000_000,
                'daily_target_hours': vault_info_after['daily_target_hours'],
                'daily_unlock': vault_info_after['daily_unlock'] / 1_000_000
            },
            'explorer_url': f"https://explorer.solana.com/tx/{signature}?cluster=devnet"
        }

        print(f"   💰 Unlocked: ${response['vault_status']['unlocked_amount']}")

        return jsonify(response), 200

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/vault-status', methods=['POST'])
def vault_status():
    """
    Get vault status.

    Expected JSON body:
    {
        "employee_wallet": "...",
        "admin_wallet": "..."
    }
    """
    try:
        data = request.get_json()

        employee_wallet = data.get('employee_wallet')
        admin_wallet = data.get('admin_wallet')

        if not employee_wallet or not admin_wallet:
            return jsonify({
                'success': False,
                'error': 'Missing employee_wallet or admin_wallet'
            }), 400

        vault_pda, _ = derive_vault_pda(
            Pubkey.from_string(employee_wallet),
            Pubkey.from_string(admin_wallet)
        )

        vault_info = get_vault_info(vault_pda)

        if not vault_info:
            return jsonify({
                'success': False,
                'error': 'Vault not found'
            }), 404

        return jsonify({
            'success': True,
            'vault': {
                'employee': vault_info['owner'],
                'admin': vault_info['admin'],
                'oracle': vault_info['oracle'],
                'unlocked_amount': vault_info['unlocked_amount'] / 1_000_000,
                'locked_amount': vault_info['locked_amount'] / 1_000_000,
                'daily_target_hours': vault_info['daily_target_hours'],
                'daily_unlock': vault_info['daily_unlock'] / 1_000_000
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    import os

    # Use PORT env var or default to 5001 (5000 conflicts with macOS AirPlay)
    port = int(os.getenv('PORT', 5001))

    # Configure debug mode via environment variable (defaults to False for production)
    # Set FLASK_DEBUG=1 or FLASK_DEBUG=true for debug mode
    debug_env = os.getenv('FLASK_DEBUG', 'false').lower()
    debug_mode = debug_env in ('1', 'true', 'yes')

    print("\n" + "="*70)
    print("🔮 KAPTURE ORACLE SERVICE")
    print("="*70)
    print(f"\n✅ Oracle Public Key: {ORACLE_PUBKEY}")
    print(f"\n📡 Starting API server on port {port}...")
    print(f"   Debug Mode: {'ON' if debug_mode else 'OFF'}")
    print(f"   Employers: Use this oracle pubkey when creating vaults")
    print(f"   Employees: Submit hours to this service")
    print(f"\n   URL: http://localhost:{port}")
    print("\n" + "="*70 + "\n")

    # Run Flask app
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
