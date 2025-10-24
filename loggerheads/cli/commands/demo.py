"""
Demo mode - Generate fake work data for quick demonstrations.
"""

import sys
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict
from ...database import save_screenshot, get_db_path, calculate_hours_worked_today
from ..display import (
    print_header, print_success, print_info, print_warning,
    console, confirm, prompt
)
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.panel import Panel
from rich.table import Table
import sqlite3


# Activity templates for realistic fake data
ACTIVITY_TEMPLATES = {
    "blockchain": [
        {"text": "VS Code - blockchain.py - def submit_hours(vault_pda, hours)", "app": "vscode", "weight": 15},
        {"text": "VS Code - vault_creation.py - impl create_vault_with_funding", "app": "vscode", "weight": 15},
        {"text": "VS Code - oracle_secure.py - Loading keypair from environment", "app": "vscode", "weight": 10},
        {"text": "Rust Analyzer - lib.rs - pub fn initialize_vault", "app": "vscode", "weight": 12},
        {"text": "Rust Analyzer - lib.rs - pub fn submit_hours_instruction", "app": "vscode", "weight": 10},
        {"text": "Terminal - anchor test --skip-local-validator", "app": "terminal", "weight": 8},
        {"text": "Terminal - pytest tests/ -v --cov=src", "app": "terminal", "weight": 8},
        {"text": "Terminal - cargo build-bpf", "app": "terminal", "weight": 5},
        {"text": "Chrome - Solana Docs | Program Derived Addresses", "app": "chrome", "weight": 6},
        {"text": "Chrome - Anchor Book | Account Constraints", "app": "chrome", "weight": 5},
        {"text": "GitHub - Pull Request #42 - Fix oracle security vulnerability", "app": "github", "weight": 4},
        {"text": "Slack - #engineering - Discussing PDA derivation approach", "app": "slack", "weight": 2},
    ],
    "frontend": [
        {"text": "VS Code - Dashboard.tsx - Building employee work view", "app": "vscode", "weight": 18},
        {"text": "VS Code - VaultCard.tsx - Displaying vault information", "app": "vscode", "weight": 15},
        {"text": "VS Code - styles.css - Implementing dark mode theme", "app": "vscode", "weight": 12},
        {"text": "Chrome - React Docs | useEffect Hook", "app": "chrome", "weight": 8},
        {"text": "Chrome - TailwindCSS | Flexbox Utilities", "app": "chrome", "weight": 6},
        {"text": "Figma - Dashboard Mockups - Employee View", "app": "figma", "weight": 8},
        {"text": "Terminal - npm run dev", "app": "terminal", "weight": 5},
        {"text": "Terminal - npm test -- --coverage", "app": "terminal", "weight": 6},
        {"text": "Chrome DevTools - Debugging state updates", "app": "chrome", "weight": 8},
        {"text": "GitHub - Pull Request #38 - Add responsive mobile layout", "app": "github", "weight": 4},
        {"text": "Slack - #design - Reviewing color palette choices", "app": "slack", "weight": 2},
    ],
    "backend": [
        {"text": "VS Code - api.py - def create_vault_endpoint", "app": "vscode", "weight": 18},
        {"text": "VS Code - database.py - Optimizing query performance", "app": "vscode", "weight": 15},
        {"text": "VS Code - auth.py - Implementing JWT validation", "app": "vscode", "weight": 12},
        {"text": "Terminal - pytest tests/ -v -s", "app": "terminal", "weight": 10},
        {"text": "Terminal - docker-compose up -d postgres", "app": "terminal", "weight": 5},
        {"text": "Chrome - FastAPI Docs | Dependency Injection", "app": "chrome", "weight": 8},
        {"text": "Chrome - PostgreSQL Docs | Index Optimization", "app": "chrome", "weight": 6},
        {"text": "DataGrip - Analyzing slow query logs", "app": "datagrip", "weight": 6},
        {"text": "Postman - Testing /api/vault/create endpoint", "app": "postman", "weight": 6},
        {"text": "GitHub - Issue #52 - Database migration strategy", "app": "github", "weight": 4},
        {"text": "Slack - #backend - Discussing API rate limiting", "app": "slack", "weight": 2},
    ],
    "devops": [
        {"text": "Terminal - kubectl apply -f deployment.yaml", "app": "terminal", "weight": 15},
        {"text": "Terminal - terraform plan", "app": "terminal", "weight": 12},
        {"text": "Terminal - docker build -t loggerheads:latest .", "app": "terminal", "weight": 10},
        {"text": "VS Code - .github/workflows/ci.yml - Setting up GitHub Actions", "app": "vscode", "weight": 15},
        {"text": "VS Code - Dockerfile - Optimizing build layers", "app": "vscode", "weight": 10},
        {"text": "Chrome - Kubernetes Docs | Pod Security Policies", "app": "chrome", "weight": 8},
        {"text": "Chrome - Datadog Dashboard - Monitoring application metrics", "app": "chrome", "weight": 8},
        {"text": "Chrome - AWS Console - Configuring load balancer", "app": "chrome", "weight": 6},
        {"text": "Terminal - helm upgrade loggerheads ./chart", "app": "terminal", "weight": 5},
        {"text": "GitHub - Pull Request #45 - Add Prometheus monitoring", "app": "github", "weight": 4},
        {"text": "Slack - #ops - Incident response for API latency", "app": "slack", "weight": 2},
    ],
}


WORK_SUMMARIES = {
    "blockchain": {
        "worked_on": [
            "Implemented secure oracle keypair loading from environment variables",
            "Refactored CLI into clean modular structure with separate command files",
            "Added Rich library for beautiful error messages and success notifications",
            "Debugged vault creation PDA derivation to match Rust program",
            "Fixed token account creation race conditions in blockchain.py",
        ],
        "completed": [
            "Oracle security fixes with documentation (docs/ORACLE_SECURITY.md)",
            "CLI refactoring reducing main file from 1194 to 153 lines",
            "All integration tests passing (87% code coverage)",
        ],
        "blockers": [
            "Occasional RPC rate limiting on devnet (need exponential backoff)",
            "Token account initialization requires 2 transactions (looking into atomic approach)",
        ],
        "tomorrow": [
            "Implement live dashboard with Rich TUI for real-time tracking",
            "Polish AI summary prompts for better readability",
            "Add vault creation presets for common scenarios",
        ],
    },
    "frontend": [
        "Built responsive dashboard for employee work tracking view",
        "Implemented dark mode theme with smooth transitions",
        "Added real-time WebSocket updates for live hour tracking",
        "Created reusable VaultCard component with loading states",
    ],
    "backend": [
        "Built RESTful API endpoints for vault management",
        "Optimized database queries reducing response time by 60%",
        "Implemented JWT authentication with refresh token rotation",
        "Added comprehensive API documentation with OpenAPI/Swagger",
    ],
    "devops": [
        "Set up Kubernetes cluster with auto-scaling for production",
        "Configured CI/CD pipeline with automated testing and deployment",
        "Implemented monitoring and alerting with Prometheus and Grafana",
        "Optimized Docker images reducing build time from 8min to 2min",
    ],
}


def generate_fake_screenshots(hours: float, role: str = "blockchain", target_date: str = None) -> List[Dict]:
    """Generate realistic fake screenshot metadata."""
    num_screenshots = int(hours * 6)  # 1 screenshot every 10 minutes
    
    # Determine date
    if target_date:
        try:
            base_date = datetime.strptime(target_date, "%Y-%m-%d")
        except ValueError:
            base_date = datetime.now()
    else:
        base_date = datetime.now()
    
    # Start at 9 AM
    start_time = base_date.replace(hour=9, minute=0, second=0, microsecond=0)
    
    # Get activities for role
    activities = ACTIVITY_TEMPLATES.get(role, ACTIVITY_TEMPLATES["blockchain"])
    
    screenshots = []
    current_time = start_time
    
    # Simulate work patterns (focus periods and breaks)
    for i in range(num_screenshots):
        # Select activity based on weights
        activity = random.choices(
            activities,
            weights=[a["weight"] for a in activities],
            k=1
        )[0]
        
        # Add realistic timestamp progression
        if i > 0:
            # Add 8-12 minutes (not exactly 10 to be realistic)
            minutes_delta = random.randint(8, 12)
            current_time += timedelta(minutes=minutes_delta)
            
            # Add lunch break (around 12-1 PM)
            if 12 <= current_time.hour < 13 and random.random() < 0.3:
                current_time += timedelta(minutes=random.randint(20, 40))
            
            # Add short breaks (random)
            if random.random() < 0.05:  # 5% chance of break
                current_time += timedelta(minutes=random.randint(5, 15))
        
        screenshot = {
            "timestamp": current_time.isoformat(),
            "ocr_text": activity["text"],
            "app": activity["app"],
            "is_demo": True,
        }
        screenshots.append(screenshot)
    
    return screenshots


def generate_fake_summary(role: str = "blockchain") -> str:
    """Generate a realistic work summary."""
    summaries = WORK_SUMMARIES.get(role, WORK_SUMMARIES["blockchain"])
    
    if isinstance(summaries, dict):
        # Structured summary
        worked_on = random.sample(summaries["worked_on"], min(4, len(summaries["worked_on"])))
        completed = random.sample(summaries["completed"], min(3, len(summaries["completed"])))
        blockers = random.sample(summaries["blockers"], min(2, len(summaries["blockers"])))
        tomorrow = random.sample(summaries["tomorrow"], min(3, len(summaries["tomorrow"])))
        
        summary = "## ✅ What I Worked On Today:\n"
        for item in worked_on:
            summary += f"• {item}\n"
        
        summary += "\n## 🏁 What I Completed:\n"
        for item in completed:
            summary += f"• {item}\n"
        
        summary += "\n## ⚠️ Issues / Blockers:\n"
        if blockers:
            for item in blockers:
                summary += f"• {item}\n"
        else:
            summary += "• None\n"
        
        summary += "\n## 🔜 Tomorrow's Focus:\n"
        for item in tomorrow:
            summary += f"• {item}\n"
        
        return summary
    else:
        # Simple list summary
        selected = random.sample(summaries, min(5, len(summaries)))
        summary = "## Work Summary:\n"
        for item in selected:
            summary += f"• {item}\n"
        return summary


def save_demo_screenshots(screenshots: List[Dict]):
    """Save demo screenshots to database."""
    for screenshot in screenshots:
        # Create fake screenshot path
        timestamp_str = screenshot["timestamp"].replace(":", "").replace("-", "").replace("T", "_")[:15]
        fake_path = f"screenshot_{timestamp_str}_demo.png"
        
        # Save to database with custom timestamp
        save_screenshot(
            file_path=fake_path,
            extracted_text=screenshot["ocr_text"],
            log_id=None,
            timestamp=screenshot["timestamp"]
        )


def reset_demo_data():
    """Reset all demo data (or all data if no non-demo data exists)."""
    db_path = get_db_path()
    
    # Check if database exists
    if not Path(db_path).exists():
        print_info("No data to reset (database doesn't exist)")
        return
    
    # Connect and check for demo data
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # For now, just clear all today's data
    cursor.execute("""
        DELETE FROM screenshots 
        WHERE DATE(timestamp) = DATE('now')
    """)
    
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    
    print_success(f"Reset complete", {"Deleted records": str(deleted)})


def run_demo(hours: float = None, role: str = None, quiet: bool = False, reset: bool = False):
    """Main demo mode function."""
    
    # Handle reset
    if reset:
        if confirm("Reset all demo data?", default=False):
            reset_demo_data()
        else:
            console.print("[yellow]Reset cancelled[/yellow]")
            return
    
    # Interactive mode if no hours specified
    if hours is None:
        print_header("🎬 Demo Mode")
        print_warning(
            "Demo Mode generates fake work data for testing and demonstrations",
            "This is NOT real work tracking. Use 'loggerheads start' for actual tracking."
        )
        
        hours_input = prompt("Hours to simulate", default="8.0")
        try:
            hours = float(hours_input)
        except ValueError:
            print_error("Invalid hours", "Please enter a number (e.g., 8 or 8.5)")
            sys.exit(1)
    
    # Validate hours
    if hours <= 0 or hours > 24:
        print_error("Invalid hours", "Please enter hours between 0.1 and 24")
        sys.exit(1)
    
    # Default role
    if role is None:
        role = "blockchain"
    
    # Validate role
    if role not in ACTIVITY_TEMPLATES:
        print_error(
            f"Unknown role: {role}",
            f"Available roles: {', '.join(ACTIVITY_TEMPLATES.keys())}"
        )
        sys.exit(1)
    
    # Generate data with progress display
    if not quiet:
        print_header(f"🎬 Generating {hours} hours of {role} work...")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        console=console if not quiet else None,
        transient=True
    ) as progress:
        # Step 1: Generate screenshots
        task1 = progress.add_task("Generating screenshots...", total=100)
        screenshots = generate_fake_screenshots(hours, role)
        progress.update(task1, completed=100)
        
        # Step 2: Save to database
        task2 = progress.add_task("Saving to database...", total=len(screenshots))
        for i, screenshot in enumerate(screenshots):
            save_demo_screenshots([screenshot])
            progress.update(task2, completed=i + 1)
        
        # Step 3: Generate summary
        task3 = progress.add_task("Generating summary...", total=100)
        summary = generate_fake_summary(role)
        progress.update(task3, completed=100)
    
    # Display results
    console.print()
    console.print(Panel(
        summary,
        title="[bold cyan]📝 Work Summary[/bold cyan]",
        border_style="cyan",
        padding=(1, 2)
    ))
    
    # Show statistics
    actual_hours = calculate_hours_worked_today()
    stats = Table(show_header=False, box=None, padding=(0, 2))
    stats.add_column("Label", style="cyan")
    stats.add_column("Value", style="bold white")
    
    stats.add_row("📊 Hours Tracked:", f"{actual_hours:.1f} hours")
    stats.add_row("📸 Screenshots:", str(len(screenshots)))
    stats.add_row("⏰ Time Range:", f"{screenshots[0]['timestamp'][11:16]} - {screenshots[-1]['timestamp'][11:16]}")
    stats.add_row("🎭 Role:", role.capitalize())
    
    console.print()
    console.print(stats)
    
    # Success message
    print_success(
        "Demo data generated successfully!",
        {
            "Next steps": "loggerheads submit (to submit to blockchain)",
            "Or": "loggerheads balance (to check earnings)",
            "Reset": "loggerheads demo --reset (to clear and start over)"
        }
    )


def demo_command():
    """Handle demo command from CLI."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate demo work data")
    parser.add_argument("--hours", type=float, help="Hours to simulate")
    parser.add_argument("--role", type=str, choices=list(ACTIVITY_TEMPLATES.keys()), 
                        help="Role/job type for realistic data")
    parser.add_argument("--quiet", action="store_true", help="Suppress progress display")
    parser.add_argument("--reset", action="store_true", help="Reset all demo data")
    
    args = parser.parse_args(sys.argv[2:])  # Skip 'loggerheads' and 'demo'
    
    run_demo(
        hours=args.hours,
        role=args.role,
        quiet=args.quiet,
        reset=args.reset
    )


if __name__ == "__main__":
    demo_command()
