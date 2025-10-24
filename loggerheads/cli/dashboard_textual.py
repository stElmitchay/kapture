"""
Retro terminal dashboard with live tracking data.
"""

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Grid
from textual.widgets import Static
from textual.reactive import reactive
from datetime import datetime
from pathlib import Path
import subprocess

from ..database import calculate_hours_worked_today, get_db_path
from ..user_context import UserContext


class PixelBox(Static):
    """Large pixelated text box for headers with ASCII art."""

    def __init__(self, text: str, **kwargs):
        super().__init__(**kwargs)
        self.box_text = text

    def render(self) -> str:
        """Render large ASCII art text."""
        if self.box_text == "LOGGER":
            return """[bold white]
██       ██████   ██████   ██████  ███████ ██████
██      ██    ██ ██       ██       ██      ██   ██
██      ██    ██ ██   ███ ██   ███ █████   ██████
██      ██    ██ ██    ██ ██    ██ ██      ██   ██
███████  ██████   ██████   ██████  ███████ ██   ██[/bold white]"""
        elif self.box_text == "HEADS":
            return """[bold white]
██   ██ ███████  █████  ██████  ███████
██   ██ ██      ██   ██ ██   ██ ██
███████ █████   ███████ ██   ██ ███████
██   ██ ██      ██   ██ ██   ██      ██
██   ██ ███████ ██   ██ ██████  ███████[/bold white]"""
        elif self.box_text == "TRACKING":
            return """[bold green]████████ ██████   █████   ██████ ██   ██
    ██    ██   ██ ██   ██ ██      ██  ██
    ██    ██████  ███████ ██      █████
    ██    ██   ██ ██   ██ ██      ██  ██
    ██    ██   ██ ██   ██  ██████ ██   ██[/bold green]"""
        elif self.box_text.startswith(">_"):
            time_str = self.box_text.split(">_")[1].strip()
            return f"""[bold green]


      ▶▶  {time_str}[/bold green]"""
        else:
            return f"\n\n   {self.box_text}\n\n"


class MainContentBox(Static):
    """Main work summary box with real-time data."""

    hours = reactive(0.0)

    def on_mount(self) -> None:
        """Start auto-refresh timer."""
        self.update_data()
        self.set_interval(5.0, self.update_data)

    def update_data(self) -> None:
        """Update hours worked."""
        self.hours = calculate_hours_worked_today()

    def render(self) -> str:
        context = UserContext()
        user_role = context.config.get('user_role', 'employee')
        industry = context.config.get('industry', 'general work')

        hours_display = f"{self.hours:.1f}"

        # Visual hour indicator
        hour_blocks = int(self.hours)
        hour_bar = "█" * hour_blocks + "░" * (10 - hour_blocks) if hour_blocks < 10 else "█" * 10

        return f"""[bold green]╔══════════════════════════════════════╗
║     TODAY'S WORK SUMMARY            ║
╚══════════════════════════════════════╝[/bold green]

[white]⚡ Industry:[/white] [cyan]{industry}[/cyan]
[white]👤 Role:[/white] [yellow]{user_role}[/yellow]
[white]📊 Status:[/white] [bold green]● ACTIVE[/bold green]

[white]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/white]

[white]🕒 Hours Tracked Today:[/white]
   [bold cyan]{hours_display} hours[/bold cyan]

   [{hour_bar}] [dim]{hours_display}/10.0[/dim]

[white]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/white]

[dim white]Your work is logged and ready for
blockchain verification and payment.[/dim white]

[dim green]⌨  Press Ctrl+C to exit[/dim green]"""


class StatsBox(Static):
    """Stats box with hours, target, and progress."""

    hours = reactive(0.0)
    target = reactive(8.0)
    progress = reactive(0)

    def on_mount(self) -> None:
        """Start auto-refresh timer."""
        self.update_data()
        self.set_interval(5.0, self.update_data)

    def update_data(self) -> None:
        """Update stats."""
        self.hours = calculate_hours_worked_today()
        self.target = self._get_daily_target()
        self.progress = min(int((self.hours / self.target) * 100), 100) if self.target > 0 else 0

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

    def render(self) -> str:
        progress_color = "green" if self.progress >= 100 else "yellow" if self.progress >= 75 else "cyan"

        # Progress bar visualization
        filled = int(self.progress / 5)  # 20 blocks max
        progress_bar = "▰" * filled + "▱" * (20 - filled)

        # Status icon
        if self.progress >= 100:
            status_icon = "✓"
            status_text = "COMPLETE"
        elif self.progress >= 75:
            status_icon = "▶"
            status_text = "ON TRACK"
        else:
            status_icon = "○"
            status_text = "IN PROGRESS"

        return f"""[bold cyan]┌────────────────────┐
│   DAILY METRICS    │
└────────────────────┘[/bold cyan]

[cyan]📈 Hours Worked[/cyan]
   [bold white]{self.hours:.1f}[/bold white] [dim]/ {self.target:.1f} hrs[/dim]

[cyan]🎯 Target Progress[/cyan]
   [{progress_color}]{progress_bar}[/{progress_color}]
   [bold {progress_color}]{self.progress}%[/bold {progress_color}]

[cyan]🔄 Status[/cyan]
   [{progress_color}]{status_icon} {status_text}[/{progress_color}]

[dim cyan]━━━━━━━━━━━━━━━━━━━[/dim cyan]
[dim white]Updated: {datetime.now().strftime('%H:%M:%S')}[/dim white]"""


class StatusBox(Static):
    """Large status display box."""

    is_running = reactive(False)

    def on_mount(self) -> None:
        """Start auto-refresh timer."""
        self.update_status()
        self.set_interval(10.0, self.update_status)

    def update_status(self) -> None:
        """Check if tracker is running."""
        try:
            result = subprocess.run(
                ["pgrep", "-f", "python.*loggerheads"],
                capture_output=True,
                text=True,
                timeout=1
            )
            self.is_running = bool(result.stdout.strip())
        except:
            self.is_running = False

    def render(self) -> str:
        status_text = "LIVE" if self.is_running else "IDLE"
        status_color = "green" if self.is_running else "yellow"
        status_icon = "●" if self.is_running else "○"

        hours = calculate_hours_worked_today()

        return f"""[bold {status_color}]╔═══════════════════════════╗
║    SYSTEM STATUS         ║
╚═══════════════════════════╝[/bold {status_color}]

[bold {status_color}]{status_icon} {status_text}[/bold {status_color}]

[white]━━━━━━━━━━━━━━━━━━━━━━━━━━━[/white]

[white]⏱  Runtime Status:[/white]
   {"[bold green]▶ ACTIVE TRACKING[/bold green]" if self.is_running else "[bold yellow]⏸ IDLE[/bold yellow]"}

[white]📊 Session Hours:[/white]
   [bold cyan]{hours:.1f}[/bold cyan] hrs

[white]━━━━━━━━━━━━━━━━━━━━━━━━━━━[/white]

[dim {status_color}]{'⚡ Capturing activity...' if self.is_running else '💤 Waiting to start...'}[/dim {status_color}]"""


class VaultBox(Static):
    """Vault and blockchain status box."""

    vault_info = reactive(None)

    def on_mount(self) -> None:
        """Start auto-refresh timer."""
        self.update_vault()
        self.set_interval(30.0, self.update_vault)

    def update_vault(self) -> None:
        """Update vault info."""
        self.vault_info = self._get_vault_info()

    def _get_vault_info(self) -> dict:
        """Get vault balance and info."""
        try:
            user_ctx = UserContext()
            if not user_ctx.has_vault():
                return None

            vault = user_ctx.get_vault()
            return {
                'locked_amount': vault.get('amount', 0),
                'daily_pay': vault.get('daily_pay', 0),
                'daily_target_hours': vault.get('daily_target_hours', 8),
                'vault_pda': vault.get('vault_pda', '')
            }
        except:
            return None

    def render(self) -> str:
        if self.vault_info:
            locked = self.vault_info['locked_amount'] / 1_000_000
            daily_pay = self.vault_info['daily_pay'] / 1_000_000
            vault_pda = self.vault_info['vault_pda'][:16] + "..." if self.vault_info['vault_pda'] else "N/A"

            return f"""[bold green]╔════════════════════════════════════════╗
║      ⛓  BLOCKCHAIN STATUS            ║
╚════════════════════════════════════════╝[/bold green]

[white]🔗 Network:[/white] [bold cyan]Solana[/bold cyan]

[white]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/white]

[white]💰 Vault Balance[/white]
   [bold cyan]${locked:.2f} USDC[/bold cyan]

[white]💵 Daily Rate[/white]
   [bold yellow]${daily_pay:.2f} USDC[/bold yellow]

[white]🔑 Vault Address[/white]
   [dim]{vault_pda}[/dim]

[white]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/white]

[bold green]💡 Ready to claim payment?[/bold green]
   [white]▶[/white] [green]loggerheads submit[/green]

[dim green]🕒 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}[/dim green]"""
        else:
            return f"""[bold yellow]╔════════════════════════════════════════╗
║      ⚠  BLOCKCHAIN STATUS            ║
╚════════════════════════════════════════╝[/bold yellow]

[white]⚠️  No vault configured[/white]

[white]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/white]

[dim white]Set up a vault to start earning
cryptocurrency for your tracked work.[/dim white]

[white]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/white]

[bold green]🚀 Get Started:[/bold green]
   [white]▶[/white] [green]loggerheads setup-vault[/green]

[dim green]🕒 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}[/dim green]"""


class LoggerheadsDashboard(App):
    """Live tracking dashboard with real-time data."""

    CSS = """
    Screen {
        background: black;
        overflow: hidden;
        layout: vertical;
    }

    PixelBox {
        border: double white;
        background: black;
        height: 100%;
        width: 1fr;
        content-align: center middle;
    }

    MainContentBox {
        border: double white;
        background: black;
        padding: 2;
        width: 2fr;
        height: 100%;
    }

    StatsBox {
        border: double white;
        background: black;
        padding: 2;
        width: 1fr;
        height: 100%;
    }

    StatusBox {
        border: double white;
        background: black;
        padding: 2;
        width: 1fr;
        height: 100%;
    }

    VaultBox {
        border: double white;
        background: black;
        padding: 2;
        width: 2fr;
        height: 100%;
    }

    #header-row {
        height: 8;
        margin: 0;
    }

    #middle-row {
        height: 1fr;
        margin: 0;
    }

    #bottom-row {
        height: 1fr;
        margin: 0;
    }

    Grid {
        grid-size: 4;
        grid-gutter: 0 1;
        height: 100%;
        margin: 0;
        padding: 0;
    }

    Horizontal {
        height: 100%;
        margin: 0;
    }

    Container {
        height: 100vh;
        width: 100%;
        margin: 0;
        padding: 0;
        layout: vertical;
    }
    """

    def compose(self) -> ComposeResult:
        """Create live dashboard layout."""
        with Container():
            # Top row: 4 pixel boxes with branding and time
            current_time = datetime.now().strftime('%H:%M')
            with Grid(id="header-row"):
                yield PixelBox("LOGGER")
                yield PixelBox("HEADS")
                yield PixelBox("TRACKING")
                yield PixelBox(f">_ {current_time}")

            # Middle row: Work summary + Stats
            with Horizontal(id="middle-row"):
                yield MainContentBox()
                yield StatsBox()

            # Bottom row: Status + Vault info
            with Horizontal(id="bottom-row"):
                yield StatusBox()
                yield VaultBox()


def show_textual_dashboard():
    """Launch the Textual dashboard."""
    app = LoggerheadsDashboard()
    app.run()
