"""
Automated submission script.
Runs at end of day to automatically submit hours to blockchain.
"""

import sys
from datetime import datetime
from .database import calculate_hours_worked_today
from .blockchain import submit_hours, get_vault_info, derive_vault_pda, format_usdc
from .vault_config import VaultConfig
from solders.pubkey import Pubkey


def auto_submit():
    """
    Automatically submit today's hours to blockchain.
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

    # Submit to blockchain
    try:
        print(f"\n📤 Submitting {hours} hours to blockchain...")

        signature = submit_hours(
            hours,
            vault['employee_pubkey'],
            vault['admin_pubkey'],
            None  # Uses default oracle keypair
        )

        print(f"✅ Success!")
        print(f"📝 Transaction: {signature}")
        print(f"🔍 Explorer: https://explorer.solana.com/tx/{signature}?cluster=devnet")

        # Show vault status
        vault_pda, _ = derive_vault_pda(
            Pubkey.from_string(vault['employee_pubkey']),
            Pubkey.from_string(vault['admin_pubkey'])
        )

        vault_info = get_vault_info(vault_pda)

        if vault_info:
            print(f"\n💰 Vault Status:")
            print(f"   Unlocked: {format_usdc(vault_info['unlocked_amount'])} USDC")
            print(f"   Locked:   {format_usdc(vault_info['locked_amount'] - vault_info['unlocked_amount'])} USDC")

            if vault_info['unlocked_amount'] > 0:
                print(f"\n💡 You can withdraw: loggerheads withdraw")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

    print("\n" + "="*60)
    print("✅ Auto-submit completed successfully")
    print("="*60 + "\n")


if __name__ == "__main__":
    auto_submit()
