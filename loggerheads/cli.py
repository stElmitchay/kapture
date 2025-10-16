"""
Command-line interface for loggerheads with improved UX.
"""

import sys
import os
from .scheduler import run_scheduled_tracker
from .user_context import UserContext
from .autostart import install_autostart, uninstall_autostart, check_autostart_status
from .database import calculate_hours_worked_today
from .blockchain import submit_hours, withdraw, get_vault_info, derive_vault_pda, format_usdc
from .vault_config import VaultConfig
from .auto_submit import auto_submit
from solders.pubkey import Pubkey


def main():
    """Main CLI entry point with improved UX."""

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "start":
            run_scheduled_tracker()

        elif command == "setup":
            # Run interactive setup for user context
            context = UserContext()
            context.setup_interactive()

        elif command == "onboard":
            # NEW: Simple onboarding for everyone
            simple_onboarding()

        elif command == "setup-vault":
            # Interactive vault setup - stores addresses for future use (EMPLOYEES)
            setup_vault_interactive()

        elif command == "employer-setup":
            # Show employers how to create vaults and onboard employees
            show_employer_setup()

        elif command == "config":
            # Show ALL configuration (user context + vault)
            show_all_config()

        elif command == "install":
            install_autostart()

        elif command == "uninstall":
            uninstall_autostart()

        elif command == "status":
            check_autostart_status()

        elif command == "version":
            from . import __version__
            print(f"loggerheads v{__version__}")

        elif command == "submit":
            # IMPROVED: Can use stored config OR manual addresses
            if len(sys.argv) >= 4:
                # Manual mode (backwards compatible)
                submit_manual()
            else:
                # Simplified mode (uses config)
                submit_simplified()

        elif command == "withdraw":
            # IMPROVED: Can use stored config OR manual addresses
            if len(sys.argv) >= 6:
                # Manual mode (backwards compatible)
                withdraw_manual()
            else:
                # Simplified mode (uses config)
                withdraw_simplified()

        elif command == "vault-info":
            # IMPROVED: Can use stored config OR manual addresses
            if len(sys.argv) >= 4:
                # Manual mode (backwards compatible)
                vault_info_manual()
            else:
                # Simplified mode (uses config)
                vault_info_simplified()

        elif command == "auto-submit":
            # Run auto-submission manually (for testing)
            auto_submit()

        elif command == "menu":
            # Interactive menu
            interactive_menu()

        elif command == "help":
            print_help()

        else:
            print(f"Unknown command: {command}")
            print_help()
    else:
        # Default: Show welcome and check if configured
        show_welcome_and_launch()


def show_welcome_and_launch():
    """Welcome screen - check if configured, otherwise run onboarding."""
    config = VaultConfig()

    if config.has_vault():
        # Already configured - show menu
        interactive_menu()
    else:
        # Not configured - run onboarding
        print("\n" + "="*70)
        print("👋 WELCOME TO WORKCHAIN!")
        print("="*70)
        print("\nBlockchain-powered work tracking that pays you automatically.")
        print("\nLet's get you set up in 2 minutes...")
        print("")

        input("Press Enter to start setup...")
        simple_onboarding()


def simple_onboarding():
    """Super simple onboarding - detects role and guides through setup."""
    print("\n" + "="*70)
    print("🚀 WORKCHAIN SETUP")
    print("="*70)

    print("\n❓ Are you an employer or an employee?")
    print("")
    print("  [1] 👔 Employer - I want to create vaults and track my team")
    print("  [2] 👤 Employee - My employer sent me here to get set up")
    print("")

    try:
        choice = input("Enter 1 or 2: ").strip()

        if choice == "1":
            # Employer flow
            employer_onboarding()
        elif choice == "2":
            # Employee flow
            employee_onboarding()
        else:
            print("\n❌ Invalid choice. Please run 'loggerheads' again and enter 1 or 2.")
            sys.exit(0)

    except KeyboardInterrupt:
        print("\n\n👋 Setup cancelled. Run 'loggerheads' again when ready!")
        sys.exit(0)


def employer_onboarding():
    """Employer onboarding - guide through vault creation."""
    print("\n" + "="*70)
    print("👔 EMPLOYER SETUP")
    print("="*70)

    print("\n📋 As an employer, you will:")
    print("  • Create vaults for your employees")
    print("  • Fund vaults with USDC (payment they'll earn)")
    print("  • Set work targets (e.g., 8 hours/day unlocks $100)")
    print("  • Employees earn automatically when they work")

    print("\n" + "-"*70)
    print("\n⚠️  IMPORTANT: You'll need:")
    print("  • A Solana wallet with some SOL (for transaction fees)")
    print("  • USDC to fund the vault (the payment amount)")
    print("  • Your employee's wallet address (they can send it to you)")

    print("\n" + "-"*70)
    ready = input("\n✅ Ready to create a vault? (y/n): ").strip().lower()

    if ready != 'y':
        print("\n👋 No problem! When you're ready, run:")
        print("   loggerheads onboard")
        print("\nOr see the full guide:")
        print("   loggerheads employer-setup")
        sys.exit(0)

    print("\n❌ VAULT CREATION COMING SOON!")
    print("\n🔧 For now, use the TypeScript script:")
    print("   cd workchain-program")
    print("   npx ts-node scripts/create-vault.ts")
    print("\n💡 We're building a simpler Python-based flow.")
    print("   Stay tuned!")


def employee_onboarding():
    """Employee onboarding - super simple setup."""
    print("\n" + "="*70)
    print("👤 EMPLOYEE SETUP")
    print("="*70)

    print("\n🎉 Great! Let's get you earning.")
    print("\nYour employer should have sent you their admin wallet address.")
    print("That's the ONLY thing you need from them.")

    print("\n" + "-"*70)
    print("\n📝 STEP 1: Your Wallet")
    print("-"*70)

    print("\nDo you already have a Solana wallet set up?")
    has_wallet = input("(y/n): ").strip().lower()

    if has_wallet != 'y':
        print("\n⚠️  You'll need to create a Solana wallet first.")
        print("\nRun these commands:")
        print("  solana-keygen new")
        print("  solana airdrop 1 --url devnet")
        print("\nThen run 'loggerheads' again!")
        sys.exit(0)

    # Get wallet
    print("\n📍 Wallet location:")
    print(f"   Default: ~/.config/solana/id.json")
    use_default = input("\nUse default wallet? (y/n): ").strip().lower()

    if use_default == 'y':
        try:
            from .blockchain import load_keypair
            keypair = load_keypair()
            employee_pubkey = str(keypair.pubkey())
            print(f"   ✓ Found wallet: {employee_pubkey[:30]}...")
        except Exception as e:
            print(f"\n❌ Could not load default wallet: {e}")
            print("\nPlease ensure wallet exists at ~/.config/solana/id.json")
            sys.exit(1)
    else:
        employee_pubkey = input("\nEnter your wallet address: ").strip()
        if not employee_pubkey:
            print("\n❌ Wallet address is required!")
            sys.exit(1)

    print("\n" + "-"*70)
    print("📝 STEP 2: Employer's Admin Wallet")
    print("-"*70)

    print("\nYour employer should have sent you their admin wallet address.")
    admin_pubkey = input("\nPaste it here: ").strip()

    if not admin_pubkey:
        print("\n❌ Admin wallet is required!")
        print("Ask your employer for their admin wallet address.")
        sys.exit(1)

    # Save configuration
    print("\n" + "-"*70)
    print("💾 Saving Configuration...")
    print("-"*70)

    config = VaultConfig()
    config.set_vault(employee_pubkey, admin_pubkey)

    vault = config.get_vault()
    print("\n✅ Configuration saved!")
    print(f"\n✨ Your vault:")
    print(f"   Vault PDA: {vault['vault_pda'][:40]}...")

    print("\n" + "-"*70)
    print("⏰ STEP 3: Auto-Submit Hours")
    print("-"*70)

    print("\nShould loggerheads automatically submit your hours daily?")
    print("(Recommended: Yes - hands-free earnings)")
    auto_submit_choice = input("\nEnable auto-submit? (y/n): ").strip().lower()

    if auto_submit_choice == 'y':
        print("\nWhat time should we submit? (e.g., 18:00 for 6 PM)")
        time = input("Time (HH:MM, default 18:00): ").strip() or "18:00"
        config.enable_auto_submit(True, time)
        print(f"\n✅ Auto-submit enabled for {time} daily")
    else:
        config.enable_auto_submit(False)
        print("\n📝 You'll need to manually run 'loggerheads submit' daily")

    print("\n" + "="*70)
    print("🎉 SETUP COMPLETE!")
    print("="*70)

    print("\n✅ You're ready to start earning!")
    print("\n📋 Next steps:")
    print("  1. Install auto-start: loggerheads install")
    print("  2. Start tracking: loggerheads start")
    print("\nThat's it! Work normally and earn automatically. 🚀")
    print("")


def show_employer_setup():
    """Show employers how to create vaults and onboard employees."""
    from .oracle import get_oracle_pubkey

    print("\n" + "="*60)
    print("👔 EMPLOYER SETUP GUIDE")
    print("="*60)

    print("\n📋 OVERVIEW:")
    print("   As an employer, you create vaults for employees and fund them.")
    print("   Each vault locks payment that unlocks as employees work.")

    print("\n" + "-"*60)
    print("🔧 STEP 1: Create a Vault for Your Employee")
    print("-"*60)

    print("\n1. Navigate to the scripts directory:")
    print("   cd workchain-program/scripts")

    print("\n2. Run the vault creation script:")
    print("   npx ts-node create-vault.ts")

    print("\n3. When prompted, provide:")
    print("   • Your admin wallet (you control the vault)")
    print("   • Employee's wallet (they give you this)")
    print(f"   • Oracle: {get_oracle_pubkey()}")
    print("     ↑ Use this embedded oracle (already in loggerheads)")

    print("\n4. Fund the vault:")
    print("   • Amount: e.g., $3000 USDC for the month")
    print("   • Daily target: e.g., 8 hours")
    print("   • Daily unlock: e.g., $100 USDC per day")

    print("\n" + "-"*60)
    print("📤 STEP 2: Onboard Your Employee")
    print("-"*60)

    print("\n1. Send your employee ONLY your admin wallet address")
    print("   Example: 'Use this address: ADM123abc...'")

    print("\n2. Tell them to run:")
    print("   pip install loggerheads")
    print("   loggerheads setup-vault")
    print("   loggerheads install")
    print("   loggerheads start")

    print("\n3. That's it! They're now earning automatically.")

    print("\n" + "-"*60)
    print("💡 HOW IT WORKS")
    print("-"*60)

    print("\n• Employee works on their laptop")
    print("• Loggerheads tracks activity automatically")
    print("• At 6 PM daily, hours are submitted to blockchain")
    print("• If they hit target (e.g., 8 hours), funds unlock")
    print("• Employee can withdraw unlocked funds anytime")

    print("\n" + "-"*60)
    print("🔐 SECURITY")
    print("-"*60)

    print("\n• Employee CANNOT fake hours (oracle verifies)")
    print("• Employee CANNOT access locked funds (smart contract enforces)")
    print("• You CANNOT withhold earned funds (blockchain guarantees payment)")

    print("\n" + "="*60)
    print("✅ Ready to create your first vault?")
    print("="*60)
    print("\nRun: cd workchain-program/scripts && npx ts-node create-vault.ts\n")


def setup_vault_interactive():
    """Interactive vault setup - saves addresses for future use."""
    print("\n" + "="*60)
    print("🔐 Vault Setup (Employee)")
    print("="*60)
    print("\n✨ SIMPLIFIED SETUP - Only 2 inputs needed!")
    print("   Everything else is calculated automatically.")
    print("\n📝 Your employer should give you:")
    print("   1. Their admin wallet address (just ONE address!)")
    print("   2. That's it!")

    print("\n" + "-"*60)

    try:
        # Employee wallet (allow default)
        print("\n👤 Employee Wallet:")
        employee_pubkey = input("   Address (or press Enter for ~/.config/solana/id.json): ").strip()

        if not employee_pubkey:
            # Load default keypair
            try:
                from .blockchain import load_keypair
                keypair = load_keypair()
                employee_pubkey = str(keypair.pubkey())
                print(f"   ✓ Using: {employee_pubkey[:20]}...")
            except Exception as e:
                print(f"\n❌ Could not load default keypair: {e}")
                print("Please enter your wallet address manually.")
                employee_pubkey = input("   Employee wallet address: ").strip()

        # Admin wallet (required)
        print("\n👔 Admin Wallet:")
        admin_pubkey = input("   Your employer's admin address: ").strip()

        if not admin_pubkey:
            print("\n❌ Admin wallet is required!")
            return

        # Save configuration (just 2 addresses!)
        config = VaultConfig()
        config.set_vault(employee_pubkey, admin_pubkey)

        # Show what was derived
        vault = config.get_vault()
        print("\n✅ Vault configured successfully!")
        print(f"📁 Config saved to: {config.config_path}")

        print("\n✨ Auto-derived addresses:")
        print(f"   🔐 Vault PDA:      {vault['vault_pda'][:30]}...")
        print(f"   💰 Vault Token:    {vault['vault_token_account'][:30]}...")
        print(f"   💳 Employee Token: {vault['employee_token_account'][:30]}...")

        # Ask about auto-submission
        print("\n" + "-"*60)
        print("⏰ Auto-Submission Setup")
        print("-"*60)
        auto = input("\nEnable automatic daily submission? (y/n): ").strip().lower()

        if auto == 'y':
            time = input("What time? (HH:MM, default 18:00): ").strip() or "18:00"
            config.enable_auto_submit(True, time)
            print(f"\n✅ Auto-submission enabled for {time} daily")
            print("\nTo install the cron job, run:")
            print("  crontab -e")
            print("\nThen add this line:")
            hour, minute = time.split(':')
            print(f"  {minute} {hour} * * * cd {os.getcwd()} && python3 -m loggerheads.auto_submit")
        else:
            config.enable_auto_submit(False)

        print("\n" + "="*60)
        print("✅ Setup complete!")
        print("="*60)

        print("\nYou can now use simplified commands:")
        print("  loggerheads submit       (no addresses needed!)")
        print("  loggerheads withdraw")
        print("  loggerheads vault-info")

    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled")
        sys.exit(0)


def submit_simplified():
    """Submit hours using stored vault config."""
    config = VaultConfig()

    if not config.has_vault():
        print("❌ No vault configured")
        print("Run: loggerheads setup-vault")
        sys.exit(1)

    vault = config.get_vault()

    # Calculate hours
    hours = calculate_hours_worked_today()
    print(f"\n📊 Calculated hours worked today: {hours}")

    if hours == 0:
        print("⚠️  No work hours detected. Make sure the tracker has been running.")
        sys.exit(1)

    try:
        print(f"📤 Submitting {hours} hours to blockchain...")
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
            print(f"   Locked: {format_usdc(vault_info['locked_amount'] - vault_info['unlocked_amount'])} USDC")

    except Exception as e:
        print(f"❌ Error: {e}")
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
        print("❌ No vault configured")
        print("Run: loggerheads setup-vault")
        sys.exit(1)

    vault = config.get_vault()

    # Check how much is unlocked
    vault_pda, _ = derive_vault_pda(
        Pubkey.from_string(vault['employee_pubkey']),
        Pubkey.from_string(vault['admin_pubkey'])
    )
    vault_info = get_vault_info(vault_pda)

    if not vault_info:
        print("❌ Vault not found")
        sys.exit(1)

    unlocked = vault_info['unlocked_amount'] / 1_000_000

    if unlocked == 0:
        print("❌ No unlocked funds available")
        print(f"\nTotal locked: {format_usdc(vault_info['locked_amount'])} USDC")
        print(f"Daily target: {vault_info['daily_target_hours']} hours")
        print("\nKeep working and submit hours to unlock funds!")
        sys.exit(1)

    print(f"\n💰 Available to withdraw: {unlocked} USDC")

    # Get amount from user or command line
    if len(sys.argv) > 2:
        amount = float(sys.argv[2])
    else:
        amount_input = input(f"Amount to withdraw (max {unlocked}): ").strip()
        amount = float(amount_input) if amount_input else unlocked

    if amount > unlocked:
        print(f"❌ Cannot withdraw {amount} USDC (only {unlocked} USDC available)")
        sys.exit(1)

    try:
        print(f"\n💸 Withdrawing {amount} USDC...")
        signature = withdraw(
            amount,
            None,  # Uses default employee keypair
            vault['admin_pubkey'],
            vault['vault_token_account'],
            vault['employee_token_account']
        )

        print(f"✅ Success!")
        print(f"📝 Transaction: {signature}")
        print(f"🔍 Explorer: https://explorer.solana.com/tx/{signature}?cluster=devnet")

    except Exception as e:
        print(f"❌ Error: {e}")
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


def vault_info_simplified():
    """Show vault info using stored config."""
    config = VaultConfig()

    if not config.has_vault():
        print("❌ No vault configured")
        print("Run: loggerheads setup-vault")
        sys.exit(1)

    vault = config.get_vault()

    try:
        vault_pda, _ = derive_vault_pda(
            Pubkey.from_string(vault['employee_pubkey']),
            Pubkey.from_string(vault['admin_pubkey'])
        )

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


def vault_info_manual():
    """Show vault info with manual addresses (backwards compatible)."""
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


def show_all_config():
    """Show all configuration (user context + vault)."""
    print("\n" + "="*60)
    print("📋 Configuration")
    print("="*60)

    # User context
    context = UserContext()
    print(f"\n👤 User Profile:")
    print(f"   Role: {context.config.get('user_role', 'Not set')}")
    print(f"   Industry: {context.config.get('industry', 'Not set')}")
    print(f"   Config: {context.config_path}")

    # Vault config
    config = VaultConfig()
    config.print_config()


def interactive_menu():
    """Interactive menu for easier navigation."""
    while True:
        print("\n" + "="*60)
        print("🔗 WorkChain - Interactive Menu")
        print("="*60)

        print("\n[1] Start tracking")
        print("[2] Submit hours")
        print("[3] Check vault status")
        print("[4] Withdraw funds")
        print("[5] Configuration")
        print("[6] Setup vault")
        print("[7] Exit")

        try:
            choice = input("\nChoice: ").strip()

            if choice == "1":
                print("\n🚀 Starting tracker...")
                run_scheduled_tracker()
            elif choice == "2":
                submit_simplified()
            elif choice == "3":
                vault_info_simplified()
            elif choice == "4":
                withdraw_simplified()
            elif choice == "5":
                show_all_config()
            elif choice == "6":
                setup_vault_interactive()
            elif choice == "7":
                print("\n👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice")

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


def print_help():
    """Print help message."""
    print("""
🔗 WorkChain - Blockchain-Powered Work Tracking

═══════════════════════════════════════════════════════════

🚀 GETTING STARTED (Super Simple!):

    Just run:  loggerheads

    That's it! You'll be guided through setup with simple questions.
    No technical knowledge needed.

═══════════════════════════════════════════════════════════

👤 FOR EMPLOYEES:

    loggerheads              Start here! (interactive setup)
    loggerheads start        Start tracking work
    loggerheads submit       Submit hours to blockchain
    loggerheads withdraw     Withdraw earned USDC
    loggerheads vault-info   Check your balance

═══════════════════════════════════════════════════════════

👔 FOR EMPLOYERS:

    loggerheads              Start here! (choose employer setup)
    loggerheads onboard      Run setup wizard again

    For vault creation, see: SETUP_AND_TESTING_GUIDE.md

═══════════════════════════════════════════════════════════

🔧 OTHER COMMANDS:

    loggerheads install      Enable auto-start on boot
    loggerheads menu         Interactive menu
    loggerheads config       View configuration
    loggerheads help         Show this help

═══════════════════════════════════════════════════════════

💡 FIRST TIME?

    Just run:  loggerheads

    The app will ask simple Y/N questions and guide you through setup.
    Takes 2 minutes. No complexity.

Documentation: See SETUP_AND_TESTING_GUIDE.md
    """)


if __name__ == "__main__":
    main()
