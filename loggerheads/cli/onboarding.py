"""
Onboarding flows for employees and employers.
"""

import sys
from ..vault_config import VaultConfig
from ..blockchain import load_keypair
from ..vault_creation import create_vault_interactive
from .display import print_header, print_separator, print_info


def simple_onboarding():
    """Super simple onboarding - detects role and guides through setup."""
    print_header("🚀 WORKCHAIN SETUP")

    print("\n❓ Are you an employer or an employee?")
    print("")
    print("  [1] 👔 Employer - I want to create vaults and track my team")
    print("  [2] 👤 Employee - My employer sent me here to get set up")
    print("")

    try:
        choice = input("Enter 1 or 2: ").strip()

        if choice == "1":
            employer_onboarding()
        elif choice == "2":
            employee_onboarding()
        else:
            print("\n❌ Invalid choice. Please run 'loggerheads' again and enter 1 or 2.")
            sys.exit(0)

    except KeyboardInterrupt:
        print("\n\n👋 Setup cancelled. Run 'loggerheads' again when ready!")
        sys.exit(0)


def employer_onboarding():
    """Employer onboarding - guide through vault creation."""
    print_header("👔 EMPLOYER SETUP")

    print("\n📋 As an employer, you will:")
    print("  • Create vaults for your employees")
    print("  • Fund vaults with USDC (payment they'll earn)")
    print("  • Set work targets (e.g., 8 hours/day unlocks $100)")
    print("  • Employees earn automatically when they work")

    print_separator()
    print("\n⚠️  IMPORTANT: You'll need:")
    print("  • A Solana wallet with some SOL (for transaction fees)")
    print("  • USDC to fund the vault (the payment amount)")
    print("  • Your employee's wallet address (they can send it to you)")

    print_separator()
    ready = input("\n✅ Ready to create a vault? (y/n): ").strip().lower()

    if ready != 'y':
        print("\n👋 No problem! When you're ready, run:")
        print("   loggerheads onboard")
        print("\nOr see the full guide:")
        print("   loggerheads employer-setup")
        sys.exit(0)

    # Launch vault creation flow
    result = create_vault_interactive()

    if result:
        print_info("TIP: Save your admin wallet address somewhere safe.")
        print("   You'll use it to manage this employee's vault.")
    else:
        print("\n❌ Vault creation failed or was cancelled.")
        print("   Run 'loggerheads onboard' to try again.")


def employee_onboarding():
    """Employee onboarding - super simple setup."""
    print_header("👤 EMPLOYEE SETUP")

    print("\n🎉 Great! Let's get you earning.")
    print("\nYour employer should have sent you their admin wallet address.")
    print("That's the ONLY thing you need from them.")

    print_separator()
    print("\n📝 STEP 1: Your Wallet")
    print_separator()

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

    print_separator()
    print("📝 STEP 2: Employer's Admin Wallet")
    print_separator()

    print("\nYour employer should have sent you their admin wallet address.")
    admin_pubkey = input("\nPaste it here: ").strip()

    if not admin_pubkey:
        print("\n❌ Admin wallet is required!")
        print("Ask your employer for their admin wallet address.")
        sys.exit(1)

    # Save configuration
    print_separator()
    print("💾 Saving Configuration...")
    print_separator()

    config = VaultConfig()
    config.set_vault(employee_pubkey, admin_pubkey)

    vault = config.get_vault()
    print("\n✅ Configuration saved!")
    print(f"\n✨ Your vault:")
    print(f"   Vault PDA: {vault['vault_pda'][:40]}...")

    print_separator()
    print("⏰ STEP 3: Auto-Submit Hours")
    print_separator()

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

    print_header("🎉 SETUP COMPLETE!")

    print("\n✅ You're ready to start earning!")
    print("\n📋 Next steps:")
    print("  1. Start tracking: loggerheads start")
    print("     (launches live dashboard with your stats)")
    print("  2. Install auto-start: loggerheads install")
    print("\nThat's it! Work normally and earn automatically. 🚀")
    print("")
