"""
Command-line interface for loggerheads.
"""

import sys
import os
from .scheduler import run_scheduled_tracker
from .user_context import UserContext
from .autostart import install_autostart, uninstall_autostart, check_autostart_status
from .database import calculate_hours_worked_today
from .blockchain import submit_hours, withdraw, get_vault_info, derive_vault_pda, format_usdc
from solders.pubkey import Pubkey


def main():
    """
    Main CLI entry point.
    """
    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "start":
            run_scheduled_tracker()
        elif command == "setup":
            # Run interactive setup for user context
            context = UserContext()
            context.setup_interactive()
        elif command == "config":
            # Show current configuration
            context = UserContext()
            print(f"\n📄 Configuration file: {context.config_path}")
            print(f"👤 Role: {context.config.get('user_role', 'Not set')}")
            print(f"🏢 Industry: {context.config.get('industry', 'Not set')}")
            print(f"\nTo edit configuration, run: loggerheads setup")
        elif command == "install":
            # Install auto-start on boot
            install_autostart()
        elif command == "uninstall":
            # Uninstall auto-start
            uninstall_autostart()
        elif command == "status":
            # Check auto-start status
            check_autostart_status()
        elif command == "version":
            from . import __version__
            print(f"loggerheads v{__version__}")
        elif command == "submit":
            # Submit hours to blockchain
            if len(sys.argv) < 4:
                print("Usage: loggerheads submit <owner_pubkey> <admin_pubkey> [oracle_keypair_path]")
                print("\nExample:")
                print("  loggerheads submit EMP123... ADM456... ~/.config/solana/oracle.json")
                sys.exit(1)

            owner_pubkey = sys.argv[2]
            admin_pubkey = sys.argv[3]
            oracle_keypair_path = sys.argv[4] if len(sys.argv) > 4 else None

            # Calculate hours from database
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

                # Show vault status
                vault_pda, _ = derive_vault_pda(Pubkey.from_string(owner_pubkey), Pubkey.from_string(admin_pubkey))
                vault_info = get_vault_info(vault_pda)
                if vault_info:
                    print(f"\n💰 Vault Status:")
                    print(f"   Unlocked: {format_usdc(vault_info['unlocked_amount'])} USDC")
                    print(f"   Locked: {format_usdc(vault_info['locked_amount'] - vault_info['unlocked_amount'])} USDC")

            except Exception as e:
                print(f"❌ Error: {e}")
                sys.exit(1)

        elif command == "withdraw":
            # Withdraw unlocked funds
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

        elif command == "vault-info":
            # Check vault status
            if len(sys.argv) < 4:
                print("Usage: loggerheads vault-info <owner_pubkey> <admin_pubkey>")
                sys.exit(1)

            owner_pubkey = sys.argv[2]
            admin_pubkey = sys.argv[3]

            try:
                vault_pda, _ = derive_vault_pda(Pubkey.from_string(owner_pubkey), Pubkey.from_string(admin_pubkey))
                print(f"\n🔐 Vault PDA: {vault_pda}")

                vault_info = get_vault_info(vault_pda)
                if vault_info:
                    print(f"\n💰 Vault Information:")
                    print(f"   Owner: {vault_info['owner']}")
                    print(f"   Admin: {vault_info['admin']}")
                    print(f"   Oracle: {vault_info['oracle']}")
                    print(f"   Total Locked: {format_usdc(vault_info['locked_amount'])} USDC")
                    print(f"   Unlocked: {format_usdc(vault_info['unlocked_amount'])} USDC")
                    print(f"   Still Locked: {format_usdc(vault_info['locked_amount'] - vault_info['unlocked_amount'])} USDC")
                    print(f"   Daily Target: {vault_info['daily_target_hours']} hours")
                    print(f"   Daily Unlock: {format_usdc(vault_info['daily_unlock'])} USDC")
                else:
                    print("❌ Vault not found or not yet initialized")
            except Exception as e:
                print(f"❌ Error: {e}")
                sys.exit(1)

        elif command == "help":
            print_help()
        else:
            print(f"Unknown command: {command}")
            print_help()
    else:
        # Default: start tracker
        run_scheduled_tracker()


def print_help():
    """Print help message."""
    print("""
Loggerheads - Automated work tracking with AI summaries + Blockchain integration

Usage:
  loggerheads              Start the tracker
  loggerheads start        Start the tracker
  loggerheads setup        Configure work context (role, industry, apps)
  loggerheads config       Show current configuration
  loggerheads install      Install auto-start on system boot
  loggerheads uninstall    Remove auto-start
  loggerheads status       Check auto-start status
  loggerheads version      Show version
  loggerheads help         Show this help

Blockchain Commands:
  loggerheads submit <owner_pubkey> <admin_pubkey> [oracle_keypair]
    Submit today's work hours to Solana blockchain
    Automatically unlocks funds if target met

  loggerheads withdraw <amount> <admin_pubkey> <vault_token_account> <owner_token_account> [owner_keypair]
    Withdraw unlocked USDC from vault

  loggerheads vault-info <owner_pubkey> <admin_pubkey>
    Check vault status and balances

First Time Setup:
  1. Run 'loggerheads setup' to configure what counts as "work"
  2. Run 'loggerheads install' to enable auto-start on boot

  This helps the AI understand your role and filter out personal activities.

Configuration:
  Edit loggerheads/config.py to customize tracking settings
  Edit ~/.loggerheads_context.json to customize work categorization

Auto-start:
  Once installed, loggerheads will start automatically on system boot
  and run during configured work hours (9:30 AM - 4:30 PM, Mon-Fri)

Requirements:
  - Ollama (with llama3.2 model)
  - Tesseract OCR
  - Discord webhook configured
  - Solana wallet for blockchain features
    """)


if __name__ == "__main__":
    main()
