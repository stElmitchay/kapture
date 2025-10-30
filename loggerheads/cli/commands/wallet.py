"""
Wallet commands - balance, setup.
"""

from ...blockchain import load_keypair, get_vault_info, derive_vault_pda, format_usdc
from ...vault_config import VaultConfig
from ...token_utils import get_token_balance, get_sol_balance
from solders.pubkey import Pubkey
from ..display import print_header, print_info


def show_balance():
    """Show wallet balances in user-friendly format."""
    try:
        keypair = load_keypair()  # Uses saved default
        pubkey = keypair.pubkey()
        my_wallet = str(pubkey)

        print_header("💰 Your Balance")

        sol_balance = get_sol_balance(pubkey)
        usdc_balance = get_token_balance(pubkey)

        # Show balances in simple format
        print(f"\n💵 Your Wallet: ${usdc_balance:.2f}")

        # Check vault balance and determine role
        config = VaultConfig()
        if config.has_vault():
            vault = config.get_vault()
            vault_pda, _ = derive_vault_pda(
                Pubkey.from_string(vault['employee_pubkey']),
                Pubkey.from_string(vault['admin_pubkey'])
            )
            vault_info = get_vault_info(vault_pda)

            if vault_info:
                unlocked = format_usdc(vault_info['unlocked_amount'])
                locked = format_usdc(vault_info['locked_amount'] - vault_info['unlocked_amount'])
                total = format_usdc(vault_info['locked_amount'])

                # Determine if user is employee or employer
                is_employee = (my_wallet == vault['employee_pubkey'])
                is_employer = (my_wallet == vault['admin_pubkey'])

                if is_employee:
                    # Employee view - show what they can withdraw
                    print(f"\n📊 Your Work Contract:")
                    print(f"💼 Available to withdraw: ${unlocked}")
                    print(f"🔒 Still earning: ${locked}")
                    print(f"📋 Total contract: ${total}")
                elif is_employer:
                    # Employer view - show what you've funded and employee has earned
                    print(f"\n📊 Employee Vault Status:")
                    print(f"💰 Total funded: ${total}")
                    print(f"✅ Employee earned: ${unlocked}")
                    print(f"🔒 Remaining: ${locked}")
                    print(f"\n👤 Employee: {vault['employee_pubkey'][:16]}...{vault['employee_pubkey'][-8:]}")
                else:
                    # Viewing someone else's vault
                    print(f"\n📊 Vault Info (viewing only):")
                    print(f"💼 Unlocked: ${unlocked}")
                    print(f"🔒 Locked: ${locked}")

        # Warnings (only if critical)
        if sol_balance < 0.001:
            print("\n⚠️  Low transaction balance!")
            print("   Get devnet SOL: solana airdrop 2")

        print()

    except Exception as e:
        print(f"\n❌ Could not load balance")
        print_info("Make sure you've set up your wallet:")
        print("   loggerheads setup-vault")
