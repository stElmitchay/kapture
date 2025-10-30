"""
Kapture Oracle Service - Independent API

This is a standalone service that verifies work and submits hours to blockchain.
Acts as neutral third party between employers and employees.

Run with: python3 oracle_service/app.py
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
from datetime import datetime

# Add parent directory to path to import loggerheads modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loggerheads.blockchain import submit_hours, get_vault_info, derive_vault_pda
from loggerheads.oracle_secure import get_oracle_keypair
from solders.pubkey import Pubkey

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests

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
        except:
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

        # TODO: Verify work proof (screenshots, timestamps, etc.)
        # For now, we trust the client (appropriate for devnet testing)
        # Production would verify:
        # - Screenshot authenticity
        # - Timestamp consistency
        # - OCR text validity
        # - Activity patterns

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

    print("\n" + "="*70)
    print("🔮 KAPTURE ORACLE SERVICE")
    print("="*70)
    print(f"\n✅ Oracle Public Key: {ORACLE_PUBKEY}")
    print(f"\n📡 Starting API server on port {port}...")
    print(f"   Employers: Use this oracle pubkey when creating vaults")
    print(f"   Employees: Submit hours to this service")
    print(f"\n   URL: http://localhost:{port}")
    print("\n" + "="*70 + "\n")

    # Run Flask app
    app.run(host='0.0.0.0', port=port, debug=True)
