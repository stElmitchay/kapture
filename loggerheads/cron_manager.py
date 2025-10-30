"""
Cron job management for auto-submit functionality.
Automatically installs and removes cron jobs for submitting hours.
"""

import os
import subprocess
import sys
from pathlib import Path


def get_current_crontab() -> str:
    """Get current crontab contents."""
    try:
        result = subprocess.run(
            ['crontab', '-l'],
            capture_output=True,
            text=True,
            check=False  # Don't raise exception if no crontab exists
        )
        if result.returncode == 0:
            return result.stdout
        return ""
    except FileNotFoundError:
        print("⚠️  cron not found on this system")
        return None


def install_auto_submit_cron(time: str = "18:00") -> bool:
    """
    Install cron job for auto-submitting hours.

    Args:
        time: Time in HH:MM format (e.g., "18:00")

    Returns:
        True if successfully installed, False otherwise
    """
    # Parse time
    try:
        hour, minute = time.split(":")
        hour = int(hour)
        minute = int(minute)

        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ValueError("Invalid time")
    except:
        print(f"❌ Invalid time format: {time}")
        print("   Expected format: HH:MM (e.g., 18:00)")
        return False

    # Get current directory (where the package is installed)
    package_dir = Path(__file__).parent.parent.absolute()

    # Get Python executable path
    python_path = sys.executable

    # Build cron command
    cron_command = f"{minute} {hour} * * * cd {package_dir} && {python_path} -m loggerheads.auto_submit >> ~/.loggerheads_logs/auto_submit.log 2>&1"

    # Check if cron is available
    current_crontab = get_current_crontab()

    if current_crontab is None:
        print("❌ cron is not available on this system")
        print("\n📝 To manually submit hours daily:")
        print("   loggerheads submit")
        return False

    # Check if job already exists
    if "loggerheads.auto_submit" in current_crontab:
        # Remove old entry
        lines = current_crontab.split('\n')
        new_lines = [line for line in lines if "loggerheads.auto_submit" not in line]
        current_crontab = '\n'.join(new_lines)

    # Add new entry
    new_crontab = current_crontab.rstrip('\n') + '\n' + cron_command + '\n'

    # Install new crontab
    try:
        # Create log directory
        log_dir = Path.home() / '.loggerheads_logs'
        log_dir.mkdir(exist_ok=True)

        # Install crontab
        process = subprocess.Popen(
            ['crontab', '-'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate(input=new_crontab)

        if process.returncode == 0:
            print(f"✅ Auto-submit installed!")
            print(f"   Will run daily at {time}")
            print(f"   Logs: ~/.loggerheads_logs/auto_submit.log")
            return True
        else:
            print(f"❌ Failed to install cron job: {stderr}")
            return False

    except Exception as e:
        print(f"❌ Error installing cron job: {e}")
        return False


def remove_auto_submit_cron() -> bool:
    """
    Remove auto-submit cron job.

    Returns:
        True if successfully removed, False otherwise
    """
    current_crontab = get_current_crontab()

    if current_crontab is None:
        return False

    if "loggerheads.auto_submit" not in current_crontab:
        print("ℹ️  No auto-submit cron job found")
        return True

    # Remove all loggerheads.auto_submit entries
    lines = current_crontab.split('\n')
    new_lines = [line for line in lines if "loggerheads.auto_submit" not in line]
    new_crontab = '\n'.join(new_lines)

    # Install new crontab
    try:
        process = subprocess.Popen(
            ['crontab', '-'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate(input=new_crontab)

        if process.returncode == 0:
            print("✅ Auto-submit cron job removed")
            return True
        else:
            print(f"❌ Failed to remove cron job: {stderr}")
            return False

    except Exception as e:
        print(f"❌ Error removing cron job: {e}")
        return False


def check_auto_submit_status() -> dict:
    """
    Check if auto-submit cron job is installed.

    Returns:
        Dict with 'installed' (bool) and 'schedule' (str) keys
    """
    current_crontab = get_current_crontab()

    if current_crontab is None or "loggerheads.auto_submit" not in current_crontab:
        return {'installed': False, 'schedule': None}

    # Extract schedule from crontab
    for line in current_crontab.split('\n'):
        if "loggerheads.auto_submit" in line:
            parts = line.strip().split()
            if len(parts) >= 5:
                minute = parts[0]
                hour = parts[1]
                return {
                    'installed': True,
                    'schedule': f"{hour:0>2}:{minute:0>2}"
                }

    return {'installed': False, 'schedule': None}
