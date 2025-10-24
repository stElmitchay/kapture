"""
Tracking commands - start, status, logs, screenshots.
"""

import subprocess
from pathlib import Path
from datetime import datetime
from ...scheduler import run_scheduled_tracker
from ...database import calculate_hours_worked_today
from ...user_context import UserContext
from ...vault_config import VaultConfig
from ...blockchain import load_keypair
from ..display import print_header, print_separator, print_info


def start():
    """Start tracking with config check."""
    vault_config = VaultConfig()
    if vault_config.has_vault():
        try:
            keypair = load_keypair()
            my_wallet = str(keypair.pubkey())
            vault = vault_config.get_vault()

            if my_wallet == vault['admin_pubkey'] and my_wallet != vault['employee_pubkey']:
                print_header("⚠️  EMPLOYER DETECTED")
                print("\nYou are the EMPLOYER in this vault.")
                print(f"Employee: {vault['employee_pubkey'][:16]}...{vault['employee_pubkey'][-8:]}")
                print()
                print("⚠️  IMPORTANT:")
                print("   • In production, the EMPLOYEE should run tracking")
                print("   • If you're testing, this will track YOUR work")
                print("   • Hours will be submitted to the employee's vault")
                print()
                proceed = input("Continue tracking as employer? (y/n): ").strip().lower()
                if proceed != 'y':
                    print("\n👋 Tracking cancelled")
                    return
        except:
            pass

    context = UserContext()

    # Check if user has configured their work preferences
    if not context.config.get('user_role') or not context.config.get('industry'):
        print_header("⚙️  FIRST TIME TRACKING SETUP")
        print("\nBefore we start tracking, let's configure what to track.")
        print("This helps the AI understand your work patterns.")
        print("")

        setup = input("Run configuration now? (y/n): ").strip().lower()

        if setup == 'y':
            context.setup_interactive()
            print("\n✅ Configuration complete!")
            print("Now starting tracker...\n")
        else:
            print("\n⚠️  Tracking without configuration.")
            print("   You can configure later with: loggerheads setup")
            print("")

    print("🚀 Starting tracker...")
    print("📊 Launching dashboard...\n")

    # Import dashboard
    from ..dashboard_textual import show_textual_dashboard

    # Start tracker in background
    from ...scheduler import run_as_daemon
    run_as_daemon()

    # Give it a moment to start
    import time
    time.sleep(1)

    # Launch dashboard (blocks until user exits)
    show_textual_dashboard()


def show_status():
    """Show current tracking status - hours, screenshots, running status."""
    print_header("⏱️  TRACKING STATUS")

    # Check if logs exist
    log_dir = Path.home() / ".loggerheads_logs"
    log_file = log_dir / "loggerheads.log"
    screenshot_dir = log_dir / "screenshots"
    db_path = log_dir / "activity_log.db"

    # Check if tracking is running
    try:
        result = subprocess.run(
            ["pgrep", "-f", "loggerheads.*start"],
            capture_output=True,
            text=True
        )
        is_running = bool(result.stdout.strip())
    except Exception:
        is_running = False

    status_icon = "🟢" if is_running else "🔴"
    status_text = "RUNNING" if is_running else "NOT RUNNING"

    print(f"\n{status_icon} Tracker: {status_text}")

    # Hours worked today
    if db_path.exists():
        try:
            hours = calculate_hours_worked_today()
            print(f"⏰ Hours today: {hours:.1f} hours")
        except Exception as e:
            print(f"⏰ Hours today: Unable to calculate ({e})")
    else:
        print("⏰ Hours today: No data (database not found)")

    # Screenshot count today
    if screenshot_dir.exists():
        today = datetime.now().strftime("%Y-%m-%d")
        screenshots_today = list(screenshot_dir.glob(f"screenshot_{today}*"))
        print(f"📸 Screenshots today: {len(screenshots_today)}")
    else:
        print("📸 Screenshots today: 0 (directory not found)")

    # Log file status
    if log_file.exists():
        size_mb = log_file.stat().st_size / (1024 * 1024)
        print(f"📝 Log file: {size_mb:.2f} MB")
    else:
        print("📝 Log file: Not found")

    print("\n" + "-"*70)

    if is_running:
        print("\n💡 Commands:")
        print("   loggerheads logs          View live logs")
        print("   loggerheads screenshots   View recent screenshots")
        print("   loggerheads submit        Submit hours to blockchain")
    else:
        print("\n💡 Start tracking:")
        print("   loggerheads start")

    print()


def view_logs():
    """View logs with tail -f."""
    log_file = Path.home() / ".loggerheads_logs" / "loggerheads.log"

    if not log_file.exists():
        print("\n❌ Log file not found")
        print(f"   Expected: {log_file}")
        print_info("Logs are created when you start tracking:")
        print("   loggerheads start")
        return

    print("\n📝 Viewing logs (Ctrl+C to exit)...\n")
    print("="*70)

    try:
        subprocess.run(["tail", "-f", str(log_file)])
    except KeyboardInterrupt:
        print("\n\n👋 Stopped viewing logs")


def view_screenshots():
    """View recent screenshots."""
    screenshot_dir = Path.home() / ".loggerheads_logs" / "screenshots"

    if not screenshot_dir.exists():
        print("\n❌ Screenshot directory not found")
        print(f"   Expected: {screenshot_dir}")
        return

    # Get recent screenshots (last 20)
    screenshots = sorted(screenshot_dir.glob("screenshot_*.png"), key=lambda p: p.stat().st_mtime, reverse=True)[:20]

    if not screenshots:
        print("\n📸 No screenshots found")
        print_info("Screenshots are captured when tracking is active")
        return

    print_header("📸 RECENT SCREENSHOTS")

    today = datetime.now().strftime("%Y-%m-%d")
    screenshots_today = [s for s in screenshots if today in s.name]

    print(f"\n📊 Total today: {len(screenshots_today)}")
    print(f"📂 Location: {screenshot_dir}")

    print("\n" + "-"*70)
    print("Last 10 screenshots:")
    print("-"*70)

    for i, screenshot in enumerate(screenshots[:10], 1):
        size_kb = screenshot.stat().st_size / 1024
        timestamp = datetime.fromtimestamp(screenshot.stat().st_mtime)
        time_str = timestamp.strftime("%H:%M:%S")
        print(f"{i:2}. {screenshot.name:40} ({size_kb:6.1f} KB) at {time_str}")

    print_info("Open screenshot folder:")
    print(f"   open {screenshot_dir}")
    print()
