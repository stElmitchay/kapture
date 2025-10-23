"""
Work commands - submit hours, withdraw funds.
"""

import sys
from ...blockchain import (
    submit_hours, withdraw, get_vault_info, 
    derive_vault_pda, format_usdc, load_keypair
)
from ...vault_config import VaultConfig
from ...database import calculate_hours_worked_today
from solders.pubkey import Pubkey
from ..display import print_header, print_info


def submit_simplified():
    """Submit hours using stored vault config."""
    config = VaultConfig()

    if not config.has_vault():
        print("\n❌ No work account set up")
        print_info("Get started: loggerheads setup-vault")
        sys.exit(1)

    vault = config.get_vault()

    # Warn if employer is submitting
    try:
        keypair = load_keypair()
        my_wallet = str(keypair.pubkey())

        if my_wallet == vault['admin_pubkey'] and my_wallet != vault['employee_pubkey']:
            print_header("⚠️  EMPLOYER SUBMITTING FOR EMPLOYEE")
            print(f"\nYou are the EMPLOYER")
            print(f"Employee: {vault['employee_pubkey'][:16]}...{vault['employee_pubkey'][-8:]}")
            print()
            print("This will submit hours ON BEHALF OF the employee.")
            print("(OK for testing, but in production the employee should submit)")
            print()
    except:
        pass

    # Calculate hours
    hours = calculate_hours_worked_today()
    print(f"\n⏰ Today's work: {hours:.1f} hours")

    if hours == 0:
        print("\n⚠️  No work detected today")
        print_info("Make sure the tracker is running: loggerheads start")
        sys.exit(1)

    # Round hours for blockchain submission (blockchain expects integer)
    hours_rounded = int(round(hours))
    print(f"   Submitting as: {hours_rounded} hours (blockchain requires whole numbers)")

    try:
        print(f"\n📤 Submitting {hours_rounded} hours...")
        signature = submit_hours(
            hours_rounded,
            vault['employee_pubkey'],
            vault['admin_pubkey'],
            None  # Uses default oracle keypair
        )

        print(f"✅ Hours submitted successfully!")

        # Show vault status
        vault_pda, _ = derive_vault_pda(
            Pubkey.from_string(vault['employee_pubkey']),
            Pubkey.from_string(vault['admin_pubkey'])
        )
        vault_info = get_vault_info(vault_pda)

        if vault_info:
            unlocked = format_usdc(vault_info['unlocked_amount'])
            target = vault_info['daily_target_hours']
            daily_pay = format_usdc(vault_info['daily_unlock'])

            print(f"\n💰 Your Balance:")
            print(f"   Available to withdraw: ${unlocked}")

            if hours >= target:
                print(f"\n🎉 You hit your {target}h target! +${daily_pay} unlocked")
            else:
                print(f"\n⚠️  Below {target}h target today. No payment unlocked.")
                print(f"   Keep working to earn ${daily_pay} for today!")

        print(f"\n🔗 View transaction: https://explorer.solana.com/tx/{signature}?cluster=devnet")

    except Exception as e:
        print(f"\n❌ Could not submit hours")
        print(f"\n💡 Error: {str(e)}")
        sys.exit(1)


def submit_manual():
    """Submit hours with manual addresses (backwards compatible)."""
    if len(sys.argv) < 4:
        print("Usage: loggerheads submit <owner_pubkey> <admin_pubkey> [oracle_keypair_path]")
        print("\nExample:")
        print("  loggerheads submit EMP123... ADM456... ~/.config/solana/oracle.json")
        sys.exit(1)

    owner_pubkey = sys.argv[2]
    admin_pubkey = sys.argv[3]
    oracle_keypair_path = sys.argv[4] if len(sys.argv) > 4 else None

    hours = calculate_hours_worked_today()
    print(f"\n📊 Calculated hours worked today: {hours}")

    if hours == 0:
        print("⚠️  No work hours detected. Make sure the tracker has been running.")
        sys.exit(1)

    try:
        print(f"📤 Submitting {hours} hours to blockchain...")
        signature = submit_hours(hours, owner_pubkey, admin_pubkey, oracle_keypair_path)
        print(f"✅ Success!")
        print(f"📝 Transaction: {signature}")
        print(f"🔍 Explorer: https://explorer.solana.com/tx/{signature}?cluster=devnet")

        vault_pda, _ = derive_vault_pda(Pubkey.from_string(owner_pubkey), Pubkey.from_string(admin_pubkey))
        vault_info = get_vault_info(vault_pda)
        if vault_info:
            print(f"\n💰 Vault Status:")
            print(f"   Unlocked: {format_usdc(vault_info['unlocked_amount'])} USDC")
            print(f"   Locked: {format_usdc(vault_info['locked_amount'] - vault_info['unlocked_amount'])} USDC")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def withdraw_simplified():
    """Withdraw funds using stored vault config."""
    config = VaultConfig()

    if not config.has_vault():
        print("\n❌ No work account set up")
        print_info("Get started: loggerheads setup-vault")
        sys.exit(1)

    vault = config.get_vault()

    # Check how much is unlocked
    vault_pda, _ = derive_vault_pda(
        Pubkey.from_string(vault['employee_pubkey']),
        Pubkey.from_string(vault['admin_pubkey'])
    )
    vault_info = get_vault_info(vault_pda)

    if not vault_info:
        print("\n❌ Could not find your work contract")
        print_info("Contact your employer")
        sys.exit(1)

    unlocked = vault_info['unlocked_amount'] / 1_000_000

    if unlocked == 0:
        print("\n❌ No money available yet")
        target = vault_info['daily_target_hours']
        daily_pay = format_usdc(vault_info['daily_unlock'])
        print(f"\n💡 Work {target}h and submit to earn ${daily_pay}")
        print("   Then come back here to withdraw!")
        sys.exit(1)

    print(f"\n💰 Available: ${unlocked:.2f}")

    # Get amount from user or command line
    if len(sys.argv) > 2:
        amount = float(sys.argv[2])
    else:
        amount_input = input(f"\nHow much to withdraw? (press Enter for all): $").strip()
        amount = float(amount_input) if amount_input else unlocked

    if amount > unlocked:
        print(f"\n❌ You only have ${unlocked:.2f} available")
        sys.exit(1)

    try:
        print(f"\n💸 Withdrawing ${amount:.2f}...")
        signature = withdraw(
            amount,
            None,  # Uses default employee keypair
            vault['admin_pubkey'],
            vault['vault_token_account'],
            vault['employee_token_account']
        )

        print(f"\n✅ Money sent to your wallet!")
        print(f"   Check your wallet balance: loggerheads balance")
        print(f"\n🔗 View transaction: https://explorer.solana.com/tx/{signature}?cluster=devnet")

    except Exception as e:
        print(f"\n❌ Withdrawal failed")
        print(f"\n💡 Error: {str(e)}")
        sys.exit(1)


def withdraw_manual():
    """Withdraw with manual addresses (backwards compatible)."""
    if len(sys.argv) < 6:
        print("Usage: loggerheads withdraw <amount> <admin_pubkey> <vault_token_account> <owner_token_account> [owner_keypair_path]")
        print("\nExample:")
        print("  loggerheads withdraw 150 ADM456... VAULT_TOKEN... OWNER_TOKEN...")
        sys.exit(1)

    amount = float(sys.argv[2])
    admin_pubkey = sys.argv[3]
    vault_token_account = sys.argv[4]
    owner_token_account = sys.argv[5]
    owner_keypair_path = sys.argv[6] if len(sys.argv) > 6 else None

    try:
        print(f"\n💸 Withdrawing {amount} USDC...")
        signature = withdraw(amount, owner_keypair_path, admin_pubkey, vault_token_account, owner_token_account)
        print(f"✅ Success!")
        print(f"📝 Transaction: {signature}")
        print(f"🔍 Explorer: https://explorer.solana.com/tx/{signature}?cluster=devnet")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
