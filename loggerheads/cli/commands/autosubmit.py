"""
Auto-submit management commands.
"""

from ...vault_config import VaultConfig
from ...cron_manager import install_auto_submit_cron, remove_auto_submit_cron, check_auto_submit_status
from ..display import print_header


def enable_autosubmit():
    """Enable auto-submit with cron installation."""
    print_header("⏰ Enable Auto-Submit")

    config = VaultConfig()

    if not config.has_vault():
        print("\n❌ No vault configured")
        print("   Run: loggerheads onboard")
        return

    print("\nWhat time should we submit your hours daily?")
    print("(This will automatically submit your work hours to the blockchain)")
    time = input("\nTime (HH:MM, default 18:00): ").strip() or "18:00"

    print(f"\n⏳ Installing auto-submit for {time}...")

    # Save config
    config.enable_auto_submit(True, time)

    # Install cron job
    if install_auto_submit_cron(time):
        print(f"\n✅ Auto-submit enabled!")
        print(f"   Your hours will be submitted daily at {time}")
        print(f"   Logs: ~/.loggerheads_logs/auto_submit.log")
    else:
        print(f"\n⚠️  Config saved but cron installation failed")
        print(f"   You can manually run: loggerheads submit")


def disable_autosubmit():
    """Disable auto-submit and remove cron job."""
    print_header("⏰ Disable Auto-Submit")

    config = VaultConfig()

    if not config.is_auto_submit_enabled():
        print("\n❌ Auto-submit is not enabled")
        return

    confirm = input("\nAre you sure you want to disable auto-submit? (y/n): ").strip().lower()

    if confirm != 'y':
        print("\n❌ Cancelled")
        return

    print("\n⏳ Disabling auto-submit...")

    # Remove cron job
    remove_auto_submit_cron()

    # Update config
    config.enable_auto_submit(False)

    print("\n✅ Auto-submit disabled")
    print("   You'll need to manually run 'loggerheads submit' daily")


def show_autosubmit_status():
    """Show auto-submit status."""
    print_header("⏰ Auto-Submit Status")

    config = VaultConfig()

    # Check config
    config_enabled = config.is_auto_submit_enabled()
    config_time = config.get_auto_submit_time()

    # Check cron
    cron_status = check_auto_submit_status()
    cron_installed = cron_status['installed']
    cron_schedule = cron_status['schedule']

    print("\n📋 Configuration:")
    print(f"   Enabled: {'✅ Yes' if config_enabled else '❌ No'}")
    if config_enabled:
        print(f"   Time: {config_time}")

    print("\n🔧 Cron Job:")
    print(f"   Installed: {'✅ Yes' if cron_installed else '❌ No'}")
    if cron_installed:
        print(f"   Schedule: {cron_schedule}")

    # Check for inconsistencies
    if config_enabled and not cron_installed:
        print("\n⚠️  WARNING: Config says enabled but cron job not installed!")
        print("   Run: loggerheads enable-autosubmit")
    elif not config_enabled and cron_installed:
        print("\n⚠️  WARNING: Cron job installed but config says disabled!")
        print("   Run: loggerheads disable-autosubmit")
    elif config_enabled and cron_installed:
        print("\n✅ Auto-submit is working correctly")
    else:
        print("\n📝 Auto-submit is disabled")
        print("   Enable with: loggerheads enable-autosubmit")

    print()
