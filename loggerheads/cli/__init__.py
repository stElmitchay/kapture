"""
Main CLI entry point - clean and modular.
"""

import sys
from .commands import tracking, wallet, work, vault, demo, autosubmit
from .onboarding import simple_onboarding
from .menu import interactive_menu, show_welcome_and_launch
from ..autostart import install_autostart, uninstall_autostart, check_autostart_status
from ..user_context import UserContext
from ..auto_submit import auto_submit


# Command routing map
COMMAND_MAP = {
    # Tracking commands
    'start': tracking.start,
    'status': tracking.show_status,
    'logs': tracking.view_logs,
    'screenshots': tracking.view_screenshots,
    'dashboard': lambda: __import__('loggerheads.cli.dashboard_textual', fromlist=['show_textual_dashboard']).show_textual_dashboard(),
    'dashboard-old': lambda: __import__('loggerheads.cli.dashboard', fromlist=['show_dashboard']).show_dashboard(),
    
    # Wallet commands
    'balance': wallet.show_balance,
    
    # Work commands (simplified - auto-detect config vs manual)
    'submit': lambda: work.submit_simplified() if len(sys.argv) < 4 else work.submit_manual(),
    'withdraw': lambda: work.withdraw_simplified() if len(sys.argv) < 6 else work.withdraw_manual(),
    
    # Vault commands
    'setup-vault': vault.setup_vault_interactive,
    'vault-info': lambda: vault.vault_info_simplified() if len(sys.argv) < 4 else vault.vault_info_manual(),
    'employer-setup': vault.show_employer_setup,
    'config': vault.show_all_config,
    
    # Onboarding
    'onboard': simple_onboarding,
    'setup': lambda: UserContext().setup_interactive(),
    
    # Menu
    'menu': interactive_menu,
    
    # Autostart
    'install': install_autostart,
    'uninstall': uninstall_autostart,
    'autostart-status': check_autostart_status,
    
    # Auto-submit
    'auto-submit': auto_submit,
    'enable-autosubmit': autosubmit.enable_autosubmit,
    'disable-autosubmit': autosubmit.disable_autosubmit,
    'autosubmit-status': autosubmit.show_autosubmit_status,

    # Demo mode
    'demo': demo.demo_command,
}


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
    loggerheads start        Start tracking with live dashboard
    loggerheads status       Check tracking status
    loggerheads balance      Check SOL/USDC balances
    loggerheads submit       Submit hours to blockchain
    loggerheads withdraw     Withdraw earned USDC
    loggerheads vault-info   Check your vault balance

═══════════════════════════════════════════════════════════

👔 FOR EMPLOYERS:

    loggerheads              Start here! (choose employer setup)
    loggerheads onboard      Run setup wizard again

    For vault creation, see: SETUP_AND_TESTING_GUIDE.md

═══════════════════════════════════════════════════════════

🔧 OTHER COMMANDS:

    loggerheads logs                View live logs
    loggerheads screenshots         View recent screenshots
    loggerheads demo                Generate fake work data (for testing/demos)
    loggerheads install             Enable auto-start on boot
    loggerheads menu                Interactive menu
    loggerheads config              View configuration
    loggerheads enable-autosubmit   Enable automatic daily submission
    loggerheads disable-autosubmit  Disable automatic daily submission
    loggerheads autosubmit-status   Check auto-submit status
    loggerheads help                Show this help

═══════════════════════════════════════════════════════════

💡 FIRST TIME?

    Just run:  loggerheads

    The app will ask simple Y/N questions and guide you through setup.
    Takes 2 minutes. No complexity.

Documentation: See SETUP_AND_TESTING_GUIDE.md
    """)


def main():
    """Main CLI entry point with improved UX."""
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        # Handle version command
        if command == "version":
            from .. import __version__
            print(f"loggerheads v{__version__}")
            return
        
        # Handle help command
        if command == "help":
            print_help()
            return
        
        # Route to appropriate command handler
        handler = COMMAND_MAP.get(command)
        
        if handler:
            try:
                handler()
            except KeyboardInterrupt:
                print("\n\n👋 Cancelled")
                sys.exit(0)
            except Exception as e:
                print(f"\n❌ Error: {e}")
                sys.exit(1)
        else:
            print(f"Unknown command: {command}")
            print_help()
    else:
        # No command - show welcome/menu
        try:
            show_welcome_and_launch()
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            sys.exit(0)


if __name__ == "__main__":
    main()
