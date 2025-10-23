"""
Vault commands - setup, info, onboarding.
"""

import sys
import os
from ...vault_config import VaultConfig
from ...blockchain import load_keypair, get_vault_info, derive_vault_pda, format_usdc
from ...oracle import get_oracle_pubkey
from ...user_context import UserContext
from solders.pubkey import Pubkey
from ..display import print_header, print_separator, print_info


def setup_vault_interactive():
    """Interactive vault setup - saves addresses for future use."""
    print_header("🔐 Vault Setup (Employee)")
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

        print_header("✅ Setup complete!")

        print("\nYou can now use simplified commands:")
        print("  loggerheads submit       (no addresses needed!)")
        print("  loggerheads withdraw")
        print("  loggerheads vault-info")

    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled")
        sys.exit(0)


def vault_info_simplified():
    """Show vault info in user-friendly format."""
    config = VaultConfig()

    if not config.has_vault():
        print("\n❌ No work account set up")
        print_info("Get started: loggerheads setup-vault")
        sys.exit(1)

    vault = config.get_vault()

    try:
        vault_pda, _ = derive_vault_pda(
            Pubkey.from_string(vault['employee_pubkey']),
            Pubkey.from_string(vault['admin_pubkey'])
        )

        vault_info = get_vault_info(vault_pda)

        if vault_info:
            print_header("📊 Your Work Contract")

            unlocked = format_usdc(vault_info['unlocked_amount'])
            locked = format_usdc(vault_info['locked_amount'] - vault_info['unlocked_amount'])
            total = format_usdc(vault_info['locked_amount'])
            daily_unlock = format_usdc(vault_info['daily_unlock'])

            print(f"\n💰 Money:")
            print(f"   Available now: ${unlocked}")
            print(f"   Still earning: ${locked}")
            print(f"   Total contract: ${total}")

            print(f"\n⏰ Work Requirements:")
            print(f"   Daily target: {vault_info['daily_target_hours']} hours")
            print(f"   You earn: ${daily_unlock} per day when you hit target")

            days_remaining = int(float(locked) / float(daily_unlock)) if float(daily_unlock) > 0 else 0
            if days_remaining > 0:
                print(f"\n📅 {days_remaining} workdays remaining on contract")

            print()
        else:
            print("\n❌ Could not find your work contract")
            print_info("Contact your employer to set up your account")

    except Exception as e:
        print(f"\n❌ Could not load contract info")
        print_info("Make sure your work account is set up:")
        print("   loggerheads setup-vault")
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


def show_employer_setup():
    """Show employers how to create vaults and onboard employees."""
    print_header("👔 EMPLOYER SETUP GUIDE")

    print("\n📋 OVERVIEW:")
    print("   As an employer, you create vaults for employees and fund them.")
    print("   Each vault locks payment that unlocks as employees work.")

    print_separator()
    print("🔧 STEP 1: Create a Vault for Your Employee")
    print_separator()

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

    print_separator()
    print("📤 STEP 2: Onboard Your Employee")
    print_separator()

    print("\n1. Send your employee ONLY your admin wallet address")
    print("   Example: 'Use this address: ADM123abc...'")

    print("\n2. Tell them to run:")
    print("   pip install loggerheads")
    print("   loggerheads setup-vault")
    print("   loggerheads install")
    print("   loggerheads start")

    print("\n3. That's it! They're now earning automatically.")

    print_separator()
    print("💡 HOW IT WORKS")
    print_separator()

    print("\n• Employee works on their laptop")
    print("• Loggerheads tracks activity automatically")
    print("• At 6 PM daily, hours are submitted to blockchain")
    print("• If they hit target (e.g., 8 hours), funds unlock")
    print("• Employee can withdraw unlocked funds anytime")

    print_separator()
    print("🔐 SECURITY")
    print_separator()

    print("\n• Employee CANNOT fake hours (oracle verifies)")
    print("• Employee CANNOT access locked funds (smart contract enforces)")
    print("• You CANNOT withhold earned funds (blockchain guarantees payment)")

    print_header("✅ Ready to create your first vault?")
    print("\nRun: cd workchain-program/scripts && npx ts-node create-vault.ts\n")


def show_all_config():
    """Show all configuration (user context + vault)."""
    print_header("📋 Configuration")

    # User context
    context = UserContext()
    print(f"\n👤 User Profile:")
    print(f"   Role: {context.config.get('user_role', 'Not set')}")
    print(f"   Industry: {context.config.get('industry', 'Not set')}")
    print(f"   Config: {context.config_path}")

    # Vault config
    config = VaultConfig()
    config.print_config()
