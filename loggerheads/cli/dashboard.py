"""
Live dashboard with pixel-perfect retro terminal aesthetic.
"""

from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.console import Console, Group
from rich.text import Text
from rich.align import Align
from rich.box import SQUARE, ROUNDED, HEAVY, DOUBLE, Box
from rich import box
from rich.style import Style
from datetime import datetime
from pathlib import Path
import time
import sys

from ..database import calculate_hours_worked_today, get_db_path
from ..user_context import UserContext


console = Console()

# Custom ULTRA THICK box - using Box.substitute() method to modify DOUBLE
# We can't create custom Box easily, so we'll just use the thickest borders with styling
ULTRA_THICK_BOX = box.DOUBLE

# Pixel art font for large text - using block characters
PIXEL_FONT = {
    'L': [
        "██      ",
        "██      ",
        "██      ",
        "██      ",
        "███████ "
    ],
    'O': [
        " ██████  ",
        "██    ██ ",
        "██    ██ ",
        "██    ██ ",
        " ██████  "
    ],
    'G': [
        " ██████  ",
        "██       ",
        "██   ███ ",
        "██    ██ ",
        " ██████  "
    ],
    'E': [
        "███████ ",
        "██      ",
        "█████   ",
        "██      ",
        "███████ "
    ],
    'R': [
        "██████  ",
        "██   ██ ",
        "██████  ",
        "██   ██ ",
        "██    ██"
    ],
    'H': [
        "██   ██ ",
        "██   ██ ",
        "███████ ",
        "██   ██ ",
        "██   ██ "
    ],
    'A': [
        " █████  ",
        "██   ██ ",
        "███████ ",
        "██   ██ ",
        "██   ██ "
    ],
    'D': [
        "██████  ",
        "██   ██ ",
        "██   ██ ",
        "██   ██ ",
        "██████  "
    ],
    'S': [
        " ██████ ",
        "██      ",
        " █████  ",
        "     ██ ",
        "██████  "
    ],
    ' ': [
        "   ",
        "   ",
        "   ",
        "   ",
        "   "
    ],
    '>': [
        "██      ",
        " ██     ",
        "  ███   ",
        " ██     ",
        "██      "
    ],
    '_': [
        "        ",
        "        ",
        "        ",
        "        ",
        "███████ "
    ]
}


def render_pixel_text(text: str, color: str = "bright_green") -> Text:
    """Render text in pixel art style."""
    lines = ["", "", "", "", ""]
    
    for char in text.upper():
        if char in PIXEL_FONT:
            for i, line in enumerate(PIXEL_FONT[char]):
                lines[i] += line + " "
    
    result = Text()
    for line in lines:
        result.append(line + "\n", style=color)
    
    return result


class LiveDashboard:
    """Real-time work tracking dashboard with pixel-perfect retro styling."""

    def __init__(self):
        self.layout = Layout()
        self._setup_layout()
        self.console = Console()

    def _setup_layout(self):
        """Create grid-based dashboard layout."""
        # Top row: Large pixel headers
        self.layout.split(
            Layout(name="header_row", size=8),
            Layout(name="middle_row", ratio=2),
            Layout(name="bottom_row", ratio=2)
        )
        
        # Split header into boxes
        self.layout["header_row"].split_row(
            Layout(name="logo1", ratio=1),
            Layout(name="logo2", ratio=1),
            Layout(name="logo3", ratio=1),
            Layout(name="logo4", ratio=1)
        )
        
        # Middle row: Main content
        self.layout["middle_row"].split_row(
            Layout(name="main_content", ratio=2),
            Layout(name="status_panel", ratio=1)
        )
        
        # Bottom row: Details
        self.layout["bottom_row"].split_row(
            Layout(name="stats_panel", ratio=1),
            Layout(name="activity_panel", ratio=2)
        )

    def run(self):
        """Start live updating dashboard."""
        try:
            with Live(
                self.layout,
                refresh_per_second=1,
                screen=True,
                console=self.console
            ) as live:
                while True:
                    self._update_display()
                    time.sleep(1)
        except KeyboardInterrupt:
            pass

    def _update_display(self):
        """Update all dashboard panels."""
        self._update_header_boxes()
        self._update_main_content()
        self._update_status_panel()
        self._update_stats_panel()
        self._update_activity_panel()

    def _update_header_boxes(self):
        """Update header with EXTREMELY THICK text boxes."""
        # Box 1: "LOGGER" - MAXIMUM THICKNESS
        logo1_text = Text()
        logo1_text.append("████████████████████\n", style="bold bright_white")
        logo1_text.append("████████████████████\n", style="bold bright_white")
        logo1_text.append("████          ██████\n", style="bold bright_white")
        logo1_text.append("████ ██     ██ █████\n", style="bold bright_white")
        logo1_text.append("████ ██     ██ █████\n", style="bold bright_white")
        logo1_text.append("████ ██     ██ █████\n", style="bold bright_white")
        logo1_text.append("████ ████████  █████\n", style="bold bright_white")
        logo1_text.append("████          ██████\n", style="bold bright_white")
        logo1_text.append("████████████████████\n", style="bold bright_white")
        logo1_text.append("████████████████████", style="bold bright_white")
        
        # Wrap in extra border for thickness
        inner_panel = Panel(
            Align.center(logo1_text, vertical="middle"),
            style="bright_white on black",
            box=HEAVY,
            padding=(0, 1),
            border_style="bold underline overline bright_white"
        )
        logo1 = Panel(
            inner_panel,
            style="bright_white on black",
            box=ULTRA_THICK_BOX,
            padding=(0, 0),
            border_style="bold underline overline bright_white"
        )
        
        # Box 2: "HEADS" - MAXIMUM THICKNESS
        logo2_text = Text()
        logo2_text.append("████████████████████\n", style="bold bright_white")
        logo2_text.append("████████████████████\n", style="bold bright_white")
        logo2_text.append("████          ██████\n", style="bold bright_white")
        logo2_text.append("████ ██  ██ ██ █████\n", style="bold bright_white")
        logo2_text.append("████ ██████ ██ █████\n", style="bold bright_white")
        logo2_text.append("████ ██  ██ ██ █████\n", style="bold bright_white")
        logo2_text.append("████ ██  ██ ██ █████\n", style="bold bright_white")
        logo2_text.append("████          ██████\n", style="bold bright_white")
        logo2_text.append("████████████████████\n", style="bold bright_white")
        logo2_text.append("████████████████████", style="bold bright_white")
        
        # Wrap in extra border for thickness
        inner_panel2 = Panel(
            Align.center(logo2_text, vertical="middle"),
            style="bright_white on black",
            box=HEAVY,
            padding=(0, 1),
            border_style="bold underline overline bright_white"
        )
        logo2 = Panel(
            inner_panel2,
            style="bright_white on black",
            box=ULTRA_THICK_BOX,
            padding=(0, 0),
            border_style="bold underline overline bright_white"
        )
        
        # Box 3: "LIVE/IDLE" - MAXIMUM THICKNESS
        is_running = self._is_tracking_running()
        status_color = "bright_green" if is_running else "bright_red"
        
        logo3_text = Text()
        logo3_text.append("████████████████████\n", style=f"bold {status_color}")
        logo3_text.append("████████████████████\n", style=f"bold {status_color}")
        logo3_text.append("████          ██████\n", style=f"bold {status_color}")
        logo3_text.append("████          ██████\n", style=f"bold {status_color}")
        if is_running:
            logo3_text.append("████  ██ LIVE ██████\n", style=f"bold {status_color}")
        else:
            logo3_text.append("████  ██ IDLE ██████\n", style=f"bold {status_color}")
        logo3_text.append("████          ██████\n", style=f"bold {status_color}")
        logo3_text.append("████          ██████\n", style=f"bold {status_color}")
        logo3_text.append("████          ██████\n", style=f"bold {status_color}")
        logo3_text.append("████████████████████\n", style=f"bold {status_color}")
        logo3_text.append("████████████████████", style=f"bold {status_color}")
        
        # Wrap in extra border for thickness
        inner_panel3 = Panel(
            Align.center(logo3_text, vertical="middle"),
            style=f"{status_color} on black",
            box=HEAVY,
            padding=(0, 1),
            border_style=f"bold {status_color}"
        )
        logo3 = Panel(
            inner_panel3,
            style=f"{status_color} on black",
            box=ULTRA_THICK_BOX,
            padding=(0, 0),
            border_style=f"bold underline overline {status_color}"
        )
        
        # Box 4: Terminal prompt MAXIMUM THICKNESS
        now = datetime.now().strftime("%H:%M")
        logo4_text = Text()
        logo4_text.append("████████████████████\n", style="bold bright_green")
        logo4_text.append("████████████████████\n", style="bold bright_green")
        logo4_text.append("████          ██████\n", style="bold bright_green")
        logo4_text.append("████          ██████\n", style="bold bright_green")
        logo4_text.append(f"████  ▶▶ {now} ██████\n", style="bold bright_green")
        logo4_text.append("████          ██████\n", style="bold bright_green")
        logo4_text.append("████          ██████\n", style="bold bright_green")
        logo4_text.append("████          ██████\n", style="bold bright_green")
        logo4_text.append("████████████████████\n", style="bold bright_green")
        logo4_text.append("████████████████████", style="bold bright_green")
        
        # Wrap in extra border for thickness
        inner_panel4 = Panel(
            Align.center(logo4_text, vertical="middle"),
            style="bright_green on black",
            box=HEAVY,
            padding=(0, 1),
            border_style="bold underline overline bright_green"
        )
        logo4 = Panel(
            inner_panel4,
            style="bright_green on black",
            box=ULTRA_THICK_BOX,
            padding=(0, 0),
            border_style="bold underline overline bright_green"
        )
        
        self.layout["logo1"].update(logo1)
        self.layout["logo2"].update(logo2)
        self.layout["logo3"].update(logo3)
        self.layout["logo4"].update(logo4)

    def _update_main_content(self):
        """Update main content area with work summary."""
        hours = calculate_hours_worked_today()
        
        # Create green title with MAXIMUM thickness
        title = Text()
        title.append("████████████████████████████████████████\n", style="bold bright_green on black")
        title.append("████████████████████████████████████████\n", style="bold bright_green on black")
        title.append("████████████████████████████████████████\n", style="bold bright_green on black")
        title.append("████  TODAY'S WORK                  ████\n", style="bold bright_green on black")
        title.append("████████████████████████████████████████\n", style="bold bright_green on black")
        title.append("████████████████████████████████████████\n", style="bold bright_green on black")
        title.append("████████████████████████████████████████", style="bold bright_green on black")
        
        # Body text with bolder formatting
        content_text = Text("\n\n", style="bold white on black")
        content_text.append(
            "  You've been tracking your work today.\n",
            style="bold white on black"
        )
        content_text.append("  The system has captured ", style="bold white on black")
        content_text.append(f"▶ {hours:.1f} hours ◀", style="bold bright_cyan on black")
        content_text.append("\n  of activity through automated\n", style="bold white on black")
        content_text.append("  screenshots and monitoring.\n\n", style="bold white on black")
        
        content_text.append(
            "  Your work is being logged securely\n",
            style="bold white on black"
        )
        content_text.append("  and can be ", style="bold white on black")
        content_text.append("submitted to blockchain\n", style="bold bright_green on black")
        content_text.append("  for verification and payment.", style="bold bright_green on black")
        
        # Double-wrapped for extra thick borders
        inner = Panel(
            Group(title, content_text),
            style="bright_white on black",
            box=HEAVY,
            padding=(1, 2),
            border_style="bold underline overline bright_white"
        )
        panel = Panel(
            inner,
            style="bright_white on black",
            box=DOUBLE,
            padding=(0, 0),
            border_style="bold underline overline bright_white"
        )
        
        self.layout["main_content"].update(panel)

    def _update_status_panel(self):
        """Update status panel with JSON-like info."""
        hours = calculate_hours_worked_today()
        target = self._get_daily_target()
        percentage = min(int((hours / target) * 100), 100) if target > 0 else 0
        
        # Create JSON-style display with ultra bold spacing
        status_text = Text()
        status_text.append("{\n\n", style="bold bright_white on black")
        status_text.append('  ▶ "Hours"', style="bold bright_cyan on black")
        status_text.append(': ', style="bold white on black")
        status_text.append(f'"{hours:.1f}"', style="bold bright_yellow on black")
        status_text.append(',\n\n', style="bold white on black")
        status_text.append('  ▶ "Target"', style="bold bright_cyan on black")
        status_text.append(': ', style="bold white on black")
        status_text.append(f'"{target:.1f}"', style="bold bright_yellow on black")
        status_text.append(',\n\n', style="bold white on black")
        status_text.append('  ▶ "Progress"', style="bold bright_cyan on black")
        status_text.append(': ', style="bold white on black")
        status_text.append(f'"{percentage}%"', style="bold bright_green on black" if percentage >= 100 else "bold bright_yellow on black")
        status_text.append('\n\n}', style="bold bright_white on black")
        
        # Double-wrapped for extra thick borders
        inner = Panel(
            status_text,
            style="bright_white on black",
            box=HEAVY,
            padding=(2, 2),
            border_style="bold underline overline bright_white"
        )
        panel = Panel(
            inner,
            style="bright_white on black",
            box=ULTRA_THICK_BOX,
            padding=(0, 0),
            border_style="bold underline overline bright_white"
        )
        
        self.layout["status_panel"].update(panel)

    def _update_stats_panel(self):
        """Update stats panel with EXTREMELY THICK numbers."""
        screenshots = self._get_screenshot_count()
        
        # MAXIMUM thickness display
        stats_text = Text()
        stats_text.append("████████████████████\n", style="bold bright_green on black")
        stats_text.append("████████████████████\n", style="bold bright_green on black")
        stats_text.append("████████████████████\n", style="bold bright_green on black")
        stats_text.append("████  STATS   ██████\n", style="bold bright_green on black")
        stats_text.append("████████████████████\n", style="bold bright_green on black")
        stats_text.append("████████████████████\n", style="bold bright_green on black")
        stats_text.append(f"████          ██████\n", style="bold bright_green on black")
        stats_text.append(f"████  ▶{screenshots:^4d}◀  ██████\n", style="bold bright_green on black")
        stats_text.append(f"████          ██████\n", style="bold bright_green on black")
        stats_text.append("████████████████████\n", style="bold bright_green on black")
        stats_text.append("████SCREENSHOTS█████\n", style="bold bright_green on black")
        stats_text.append("████████████████████\n", style="bold bright_green on black")
        stats_text.append("████████████████████", style="bold bright_green on black")
        
        # Double-wrapped for extra thick borders
        inner = Panel(
            Align.center(stats_text, vertical="middle"),
            style="bright_green on black",
            box=HEAVY,
            padding=(1, 1),
            border_style="bold underline overline bright_green"
        )
        panel = Panel(
            inner,
            style="bright_green on black",
            box=ULTRA_THICK_BOX,
            padding=(0, 0),
            border_style="bold underline overline bright_green"
        )
        
        self.layout["stats_panel"].update(panel)

    def _update_activity_panel(self):
        """Update activity panel with description."""
        vault_info = self._get_vault_info()
        
        # Green title with MAXIMUM thickness
        title = Text()
        title.append("████████████████████████████████████████████████\n", style="bold bright_green on black")
        title.append("████████████████████████████████████████████████\n", style="bold bright_green on black")
        title.append("████████████████████████████████████████████████\n", style="bold bright_green on black")
        title.append("████  BLOCKCHAIN STATUS                    ████\n", style="bold bright_green on black")
        title.append("████████████████████████████████████████████████\n", style="bold bright_green on black")
        title.append("████████████████████████████████████████████████\n", style="bold bright_green on black")
        title.append("████████████████████████████████████████████████", style="bold bright_green on black")
        
        # Body text with bolder formatting
        content_text = Text("\n\n", style="bold white on black")
        
        if vault_info:
            unlocked = vault_info.get('unlocked_amount', 0) / 1_000_000
            locked = (vault_info.get('locked_amount', 0) - vault_info.get('unlocked_amount', 0)) / 1_000_000
            
            content_text.append(
                "  Your work vault is connected to\n",
                style="bold white on black"
            )
            content_text.append("  the Solana blockchain.\n\n", style="bold white on black")
            content_text.append("  You have ", style="bold white on black")
            content_text.append(
                f"▶ ${unlocked:.2f} USDC ◀",
                style="bold bright_cyan on black"
            )
            content_text.append(" available\n", style="bold white on black")
            content_text.append("  to withdraw and ", style="bold white on black")
            content_text.append(
                f"▶ ${locked:.2f} USDC ◀",
                style="bold bright_yellow on black"
            )
            content_text.append("\n  still locked in your vault.\n\n", style="bold white on black")
            
            content_text.append("  ▶▶ Submit: ", style="bold dim white on black")
            content_text.append("loggerheads submit", style="bold bright_green on black")
        else:
            content_text.append(
                "  No vault configured.\n",
                style="bold white on black"
            )
            content_text.append("  Set up a vault to start earning\n", style="bold white on black")
            content_text.append("  cryptocurrency for your work.\n\n", style="bold white on black")
            content_text.append("  ▶▶ Run: ", style="bold dim white on black")
            content_text.append("loggerheads setup-vault", style="bold bright_green on black")
        
        # Add timestamp with MAXIMUM thickness separator
        timestamp = datetime.now().strftime("%d/%m/%Y")
        footer = Text()
        footer.append("\n\n", style="bold dim white on black")
        footer.append("████████████████████████████████████████████████\n", style="bold dim white on black")
        footer.append(f"████  {timestamp}  ", style="bold dim white on black")
        
        # Double-wrapped for extra thick borders
        inner = Panel(
            Group(title, content_text, footer),
            style="bright_white on black",
            box=HEAVY,
            padding=(1, 2),
            border_style="bold underline overline bright_white"
        )
        panel = Panel(
            inner,
            style="bright_white on black",
            box=ULTRA_THICK_BOX,
            padding=(0, 0),
            border_style="bold underline overline bright_white"
        )
        
        self.layout["activity_panel"].update(panel)



    def _is_tracking_running(self) -> bool:
        """Check if tracker is currently running."""
        try:
            import subprocess
            result = subprocess.run(
                ["pgrep", "-f", "python.*loggerheads.*start"],
                capture_output=True,
                text=True,
                timeout=1
            )
            return bool(result.stdout.strip())
        except:
            return False

    def _get_screenshot_count(self) -> int:
        """Get today's screenshot count."""
        screenshot_dir = Path.home() / ".loggerheads_logs" / "screenshots"
        if not screenshot_dir.exists():
            return 0
        
        today = datetime.now().strftime("%Y-%m-%d")
        return len(list(screenshot_dir.glob(f"screenshot_{today}*")))

    def _get_daily_target(self) -> float:
        """Get daily hour target from config."""
        try:
            user_ctx = UserContext()
            if user_ctx.has_vault():
                vault = user_ctx.get_vault()
                return float(vault.get('daily_target_hours', 8))
        except:
            pass
        return 8.0

    def _get_vault_info(self) -> dict:
        """Get vault balance and info."""
        try:
            from solana.rpc.api import Client
            from solders.pubkey import Pubkey
            
            user_ctx = UserContext()
            if not user_ctx.has_vault():
                return None
            
            vault = user_ctx.get_vault()
            vault_pda = vault.get('vault_pda')
            if not vault_pda:
                return None
            
            # Get RPC URL from config
            rpc_url = user_ctx.config.get('rpc_url', 'https://api.devnet.solana.com')
            client = Client(rpc_url)
            
            # Fetch vault account
            vault_pubkey = Pubkey.from_string(vault_pda)
            account_info = client.get_account_info(vault_pubkey)
            
            if account_info and account_info.value:
                # Parse vault data (simplified - actual parsing depends on account structure)
                return {
                    'locked_amount': vault.get('amount', 0),
                    'unlocked_amount': 0,  # Would need to parse from account data
                    'daily_pay': vault.get('daily_pay', 0),
                    'daily_target_hours': vault.get('daily_target_hours', 8)
                }
        except:
            pass
        
        # Fallback to config values
        try:
            user_ctx = UserContext()
            vault = user_ctx.get_vault()
            return {
                'locked_amount': vault.get('amount', 0),
                'unlocked_amount': 0,
                'daily_pay': vault.get('daily_pay', 0),
                'daily_target_hours': vault.get('daily_target_hours', 8)
            }
        except:
            return None

    def _get_recent_screenshots(self, limit: int = 5) -> list:
        """Get recent screenshot data."""
        try:
            import sqlite3
            db_path = get_db_path()
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT timestamp, extracted_text
                FROM screenshots
                WHERE DATE(timestamp) = DATE('now')
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))
            
            results = cursor.fetchall()
            conn.close()
            
            return [
                {
                    'timestamp': row[0],
                    'ocr': row[1] or 'No text extracted'
                }
                for row in results
            ]
        except:
            return []


def show_dashboard():
    """Show live dashboard."""
    dashboard = LiveDashboard()
    
    console.print("\n[bright_green]═══════════════════════════════════════[/bright_green]")
    console.print("[bright_white bold]   Starting Live Dashboard...[/bright_white bold]")
    console.print("[bright_green]═══════════════════════════════════════[/bright_green]\n")
    
    time.sleep(0.5)
    
    try:
        dashboard.run()
    except KeyboardInterrupt:
        console.print("\n\n[bright_cyan]Dashboard closed[/bright_cyan]")
