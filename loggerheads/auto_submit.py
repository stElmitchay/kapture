"""
Automated submission script.
Runs at end of day to automatically submit hours to blockchain via oracle API.
"""

import sys
from datetime import datetime
from .database import calculate_hours_worked_today, get_screenshots
from .vault_config import VaultConfig
from .oracle_client import get_oracle_client


def auto_submit():
    """
    Automatically submit today's hours to oracle API.
    Designed to run as a cron job or systemd timer.
    """
    print(f"\n⏰ Auto-Submit Running at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    # Load vault config
    config = VaultConfig()

    if not config.has_vault():
        print("❌ Error: No vault configured")
        print("Run: loggerheads setup-vault")
        sys.exit(1)

    vault = config.get_vault()

    # Calculate hours worked today
    hours = calculate_hours_worked_today()

    print(f"\n📊 Hours worked today: {hours}")

    if hours == 0:
        print("⚠️  No work detected today - skipping submission")
        print("   (This is normal for weekends or days off)")
        return

    # Get work proof (screenshots from today)
    # IMPORTANT: Get ALL screenshots from today to get accurate count and timestamps
    all_screenshots = get_screenshots(today_only=True)  # Get all screenshots from today only

    # Build proof summary
    proof = {
        'screenshot_count': len(all_screenshots),
        'work_summary': f'{hours} hours tracked'
    }

    if all_screenshots:
        # Note: get_screenshots() returns ordered by timestamp DESC (newest first)
        proof['first_screenshot_time'] = all_screenshots[-1][2]  # oldest (last in list)
        proof['last_screenshot_time'] = all_screenshots[0][2]    # newest (first in list)

    print(f"   Screenshots: {proof['screenshot_count']}")
    print(f"   First screenshot: {proof.get('first_screenshot_time', 'N/A')}")
    print(f"   Last screenshot: {proof.get('last_screenshot_time', 'N/A')}")
    print(f"   Submitting as: {hours} hours")

    # Submit to oracle API
    try:
        print(f"\n📤 Submitting to oracle service...")

        oracle = get_oracle_client()

        # Check oracle is reachable
        try:
            health = oracle.health_check()
            print(f"   ✓ Oracle online: {health['oracle_pubkey'][:16]}...")
        except ConnectionError as e:
            print(f"\n❌ Cannot reach oracle service!")
            print(f"   Error: {e}")
            print(f"\n   Make sure oracle is running:")
            print(f"   python3 oracle_service/app.py")
            sys.exit(1)

        # Submit hours
        result = oracle.submit_hours(
            employee_wallet=vault['employee_pubkey'],
            admin_wallet=vault['admin_pubkey'],
            hours=hours,
            proof=proof
        )

        print(f"✅ Success!")
        print(f"📝 Transaction: {result['transaction_signature']}")
        print(f"🔍 Explorer: {result['explorer_url']}")

        # Show vault status
        vault_status = result['vault_status']
        print(f"\n💰 Vault Status:")
        print(f"   Unlocked: ${vault_status['unlocked_amount']:.2f} USDC")

        remaining = vault_status['locked_amount'] - vault_status['unlocked_amount']
        print(f"   Remaining: ${remaining:.2f} USDC")

        if vault_status['unlocked_amount'] > 0:
            print(f"\n💡 You can withdraw: loggerheads withdraw")

    except ConnectionError as e:
        print(f"❌ Connection Error: {e}")
        print(f"\n   Make sure oracle service is running:")
        print(f"   python3 oracle_service/app.py")
        sys.exit(1)
    except ValueError as e:
        print(f"❌ Submission Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    print("\n" + "="*60)
    print("✅ Auto-submit completed successfully")
    print("="*60 + "\n")


if __name__ == "__main__":
    auto_submit()
