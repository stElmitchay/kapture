"""
Interactive menu system.
"""

from ..vault_config import VaultConfig
from ..blockchain import load_keypair
from ..vault_creation import create_vault_interactive
from .commands.tracking import start as start_tracking
from .commands.work import submit_simplified, withdraw_simplified
from .commands.vault import vault_info_simplified, show_employer_setup, show_all_config, setup_vault_interactive
from .commands.wallet import show_balance
from .commands.tracking import view_logs
from .display import print_header


def interactive_menu():
    """Interactive menu with smart role detection."""
    # Detect ACTUAL role based on wallet address
    config = VaultConfig()

    # Determine user's actual role by comparing wallet addresses
    user_role = "unknown"
    if config.has_vault():
        try:
            keypair = load_keypair()
            my_wallet = str(keypair.pubkey())
            vault = config.get_vault()

            if my_wallet == vault['employee_pubkey']:
                user_role = "employee"
            elif my_wallet == vault['admin_pubkey']:
                user_role = "employer"
        except:
            user_role = "employee"  # Default fallback
    else:
        user_role = "employer"  # No vault = probably setting up as employer

    while True:
        print_header("🔗 WorkChain - Interactive Menu")

        # Show ACTUAL role (not switchable)
        mode_icon = "👤" if user_role == "employee" else "👔"
        mode_name = "Employee" if user_role == "employee" else "Employer"
        print(f"\n{mode_icon} Your role: {mode_name}")

        if user_role == "employee":
            print("\n[1] Start tracking")
            print("[2] Submit hours")
            print("[3] Check vault status")
            print("[4] Withdraw funds")
            print("[5] Check balance")
            print("[6] View logs")
            print("[7] Configuration")
            print("[8] Setup vault (employee)")
            print("[9] Exit")
        else:
            print("\n[1] Create vault for employee")
            print("[2] View employer guide")
            print("[3] Check balance")
            print("[4] Configuration")
            print("[5] Exit")

        try:
            choice = input("\nChoice: ").strip().lower()

            # Handle choices based on ACTUAL role
            if user_role == "employee":
                if choice == "1":
                    start_tracking()
                elif choice == "2":
                    submit_simplified()
                elif choice == "3":
                    vault_info_simplified()
                elif choice == "4":
                    withdraw_simplified()
                elif choice == "5":
                    show_balance()
                elif choice == "6":
                    view_logs()
                elif choice == "7":
                    show_all_config()
                elif choice == "8":
                    setup_vault_interactive()
                elif choice == "9":
                    print("\n👋 Goodbye!")
                    break
                else:
                    print("❌ Invalid choice")
            elif user_role == "employer":
                if choice == "1":
                    create_vault_interactive()
                elif choice == "2":
                    show_employer_setup()
                elif choice == "3":
                    show_balance()
                elif choice == "4":
                    show_all_config()
                elif choice == "5":
                    print("\n👋 Goodbye!")
                    break
                else:
                    print("❌ Invalid choice")
            else:
                # Unknown role
                print("❌ Could not determine your role")
                print("💡 Run: loggerheads setup-vault")
                break

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


def show_welcome_and_launch():
    """Welcome screen - check if configured, otherwise run onboarding."""
    from .onboarding import simple_onboarding
    
    config = VaultConfig()

    if config.has_vault():
        # Already configured - show menu
        interactive_menu()
    else:
        # Not configured - run onboarding
        print_header("👋 WELCOME TO WORKCHAIN!")
        print("\nBlockchain-powered work tracking that pays you automatically.")
        print("\nLet's get you set up in 2 minutes...")
        print("")

        input("Press Enter to start setup...")
        simple_onboarding()
