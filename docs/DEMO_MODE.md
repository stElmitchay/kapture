# Demo Mode - Architecture & Design

## Overview

Demo mode generates **realistic fake work data** for quick demonstrations without requiring actual work tracking. Perfect for hackathon judges, client demos, or testing the full flow in minutes.

---

## Why Demo Mode?

### The Problem
In normal operation:
1. Start tracking → Wait hours → Get screenshots → Submit → Withdraw
2. **Takes 8+ hours** for a complete demo
3. **Not practical** for hackathon presentations or quick demos

### The Solution
Demo mode:
1. Run `loggerheads demo --hours 8` → **30 seconds**
2. Generates realistic fake data
3. Can immediately submit and withdraw
4. **Perfect for 5-minute demos**

---

## How Demo Mode Works

### Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│  loggerheads demo --hours 8                                      │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  1. GENERATE FAKE SCREENSHOTS (48 screenshots for 8 hours)      │
│     • Realistic filenames with timestamps                        │
│     • Convincing OCR text (code editors, terminals, browsers)    │
│     • Activity patterns (focus time, breaks, meetings)           │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  2. POPULATE DATABASE                                            │
│     • Save screenshot metadata                                   │
│     • Add realistic timestamps (9 AM - 5 PM)                     │
│     • Track window titles and apps                               │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  3. GENERATE AI SUMMARY                                          │
│     • Realistic work description                                 │
│     • Completed tasks                                            │
│     • Blockers/issues                                            │
│     • Tomorrow's focus                                           │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  4. SHOW RESULTS                                                 │
│     • Display summary in rich format                             │
│     • Show hours tracked                                         │
│     • Prompt: "Ready to submit to blockchain?"                   │
└─────────────────────────────────────────────────────────────────┘
```

### Data Generation

#### Fake Screenshots
```python
Screenshot Filename Pattern:
  screenshot_20251023_093215.png
  screenshot_20251023_093515.png
  ...

OCR Text Examples:
  - "VS Code - blockchain.py - def submit_hours(vault_pda, hours):"
  - "Terminal - pytest tests/ -v --cov=85%"
  - "Chrome - Solana Documentation | Program Derived Addresses"
  - "GitHub - Pull Request #42 - Add oracle security fixes"
  - "Slack - #engineering - Discussing architecture decisions"
  - "Figma - Dashboard Mockups - Employee View"
```

#### Activity Patterns
```python
Realistic 8-hour workday:
  09:00-10:30 - Deep work (coding) - 90 min
  10:30-10:45 - Break              - 15 min
  10:45-12:00 - Coding + reviews   - 75 min
  12:00-13:00 - Lunch break        - 60 min
  13:00-14:30 - Meetings/docs      - 90 min
  14:30-14:45 - Break              - 15 min
  14:45-17:00 - Coding + testing   - 135 min
```

#### OCR Text Templates
```python
activities = [
    # Coding
    {"text": "VS Code - {file}.py - {function}", "app": "vscode", "weight": 40},
    {"text": "VS Code - {file}.rs - impl {struct}", "app": "vscode", "weight": 30},
    
    # Terminal
    {"text": "Terminal - cargo test --all", "app": "terminal", "weight": 10},
    {"text": "Terminal - pytest tests/ -v", "app": "terminal", "weight": 10},
    {"text": "Terminal - git commit -m '{msg}'", "app": "terminal", "weight": 5},
    
    # Browser (docs)
    {"text": "Chrome - Solana Docs | {topic}", "app": "chrome", "weight": 15},
    {"text": "Chrome - Rust Book | {chapter}", "app": "chrome", "weight": 10},
    
    # Reviews
    {"text": "GitHub - Pull Request #{num} - {title}", "app": "github", "weight": 10},
    {"text": "GitHub - Issue #{num} - {issue}", "app": "github", "weight": 5},
    
    # Communication
    {"text": "Slack - #{channel} - {topic}", "app": "slack", "weight": 8},
    {"text": "Discord - {server} | {discussion}", "app": "discord", "weight": 5},
    
    # Design
    {"text": "Figma - {project} - {screen}", "app": "figma", "weight": 3},
]
```

---

## CLI Commands

### Generate Demo Data

```bash
# Generate 8 hours of fake work
loggerheads demo --hours 8

# Quick demo (4 hours)
loggerheads demo --hours 4

# Full day with overtime
loggerheads demo --hours 10

# Quiet mode (no progress display)
loggerheads demo --hours 8 --quiet

# Interactive (asks for hours)
loggerheads demo
```

### Reset Demo Data

```bash
# Reset all data (screenshots, database, config)
loggerheads demo --reset

# Reset and generate new data
loggerheads demo --reset --hours 8
```

### Show Demo Summary

```bash
# Show generated summary
loggerheads demo --summary

# Export summary to file
loggerheads demo --summary --export summary.md
```

---

## Demo Flow Example

### 5-Minute Hackathon Demo

```bash
# 1. Reset everything (10 seconds)
$ loggerheads demo --reset
✅ All data cleared. Fresh start!

# 2. Generate 8 hours of work (30 seconds)
$ loggerheads demo --hours 8

🎬 Demo Mode: Generating 8.0 hours of work...

1️⃣  Generating screenshots...
   ✓ Created 48 realistic screenshots

2️⃣  Populating database...
   ✓ Saved 48 screenshot records

3️⃣  Analyzing work patterns...
   ✓ Detected: 85% coding, 10% docs, 5% meetings

4️⃣  Generating AI summary...

╭─────────────────────── Work Summary ───────────────────────╮
│                                                             │
│  ✅ What I Worked On Today:                                 │
│  • Implemented blockchain oracle security fixes            │
│  • Refactored CLI into modular structure                    │
│  • Added Rich library for beautiful error handling          │
│  • Debugged vault creation PDA derivation issues            │
│                                                             │
│  🏁 What I Completed:                                       │
│  • Oracle keypair generation utility                        │
│  • Security documentation                                   │
│  • All tests passing (87% coverage)                         │
│                                                             │
│  ⚠️  Issues / Blockers:                                      │
│  • Token account creation race condition (investigating)    │
│                                                             │
│  🔜 Tomorrow's Focus:                                       │
│  • Implement live dashboard with Rich TUI                   │
│  • Polish AI summary prompts                                │
│                                                             │
╰─────────────────────────────────────────────────────────────╯

📊 Hours Tracked: 8.2 hours
📸 Screenshots: 48
⏰ Time Range: 09:00 AM - 05:12 PM

✅ Demo data generated successfully!

💡 Next steps:
   • Submit to blockchain: loggerheads submit
   • Check balance: loggerheads balance
   • Withdraw earnings: loggerheads withdraw

# 3. Submit to blockchain (5 seconds)
$ loggerheads submit
📤 Submitting 8 hours to blockchain...
✅ Success! Transaction: ABC123...XYZ789

# 4. Check balance (2 seconds)
$ loggerheads balance
💰 Available: $100.00 USDC
🔒 Locked: $2,900.00 USDC

# 5. Withdraw (5 seconds)
$ loggerheads withdraw
💸 Withdrawing $100.00 USDC...
✅ Success! Check your wallet.

# Total time: ~60 seconds (vs 8+ hours for real tracking)
```

---

## Advanced Features

### Custom Scenarios

```bash
# Frontend developer scenario
$ loggerheads demo --hours 8 --role frontend
# Generates: React, TypeScript, CSS, Figma, browser testing

# Backend developer scenario
$ loggerheads demo --hours 8 --role backend
# Generates: Python, databases, APIs, Docker, testing

# DevOps scenario
$ loggerheads demo --hours 8 --role devops
# Generates: Kubernetes, CI/CD, monitoring, infrastructure

# Blockchain developer scenario (default)
$ loggerheads demo --hours 8 --role blockchain
# Generates: Rust, Solana, smart contracts, testing
```

### Time Travel

```bash
# Generate data for yesterday
$ loggerheads demo --hours 8 --date 2025-10-22

# Generate data for last week
$ loggerheads demo --hours 8 --date 2025-10-16

# Generate multiple days at once
$ loggerheads demo --days 5 --hours 8
# Generates 5 days of 8-hour work data
```

### Realistic Variations

```bash
# Add randomness (6-10 hours)
$ loggerheads demo --hours-range 6-10

# Simulate productive day
$ loggerheads demo --hours 9 --productivity high

# Simulate distracted day
$ loggerheads demo --hours 6 --productivity low

# Add meeting-heavy day
$ loggerheads demo --hours 8 --meetings 4
```

---

## Technical Implementation

### File Structure

```
loggerheads/
└── cli/
    └── commands/
        ├── demo.py              # Main demo command
        └── demo_generators/
            ├── __init__.py
            ├── screenshots.py   # Fake screenshot generation
            ├── activities.py    # Activity templates
            ├── summaries.py     # AI summary generation
            └── patterns.py      # Work patterns (breaks, focus)
```

### Core Functions

```python
# demo.py
def run_demo(hours: float, quiet: bool = False, role: str = "blockchain"):
    """Main demo orchestration"""
    1. validate_inputs(hours, role)
    2. generate_screenshots(hours, role)
    3. populate_database(screenshots)
    4. generate_summary(screenshots)
    5. display_results()

# screenshots.py
def generate_fake_screenshots(hours: float, role: str) -> List[Screenshot]:
    """Generate realistic screenshot metadata"""
    - Calculate num_screenshots (hours * 6)
    - Generate timestamps (workday pattern)
    - Select activity templates based on role
    - Create screenshot records

# activities.py
ACTIVITY_TEMPLATES = {
    "blockchain": [...],
    "frontend": [...],
    "backend": [...],
    "devops": [...],
}

def get_activities_for_role(role: str, hours: float) -> List[Activity]:
    """Get realistic activity mix for role"""

# summaries.py
def generate_fake_summary(screenshots: List[Screenshot]) -> Dict:
    """Generate realistic work summary"""
    - Analyze activity distribution
    - Create believable task descriptions
    - Generate completed items
    - Add realistic blockers
```

---

## Advantages for Hackathon

### For Judges
✅ See complete flow in 5 minutes  
✅ No waiting for real work tracking  
✅ Reproducible demo (same every time)  
✅ Shows system works end-to-end

### For Presenters
✅ No live coding stress  
✅ Can reset and re-demo anytime  
✅ Multiple scenarios prepared  
✅ Backup if live demo fails

### For Testing
✅ Fast integration testing  
✅ Test edge cases (0.5h, 20h)  
✅ Test different work patterns  
✅ Validate full workflow

---

## Limitations

### What Demo Mode Does NOT Do
❌ Actually track real work  
❌ Generate actual screenshot images (only metadata)  
❌ Use real AI (pre-generated summaries with templates)  
❌ Replace real usage

### Clearly Marked as Demo
```python
# All demo data flagged in database
screenshots.is_demo = True

# Warnings when using demo data
⚠️  Demo Mode: Using fake data (not real work tracking)

# Clear distinction in UI
[DEMO] in status displays
```

---

## Future Enhancements

### Potential Additions
1. **Image generation** - Actually create fake screenshot PNGs using PIL
2. **Video replay** - Show timelapse of fake work session
3. **Team mode** - Generate data for multiple employees
4. **Export demos** - Save demo scenarios for reuse
5. **Demo scripts** - Automated presentation mode

---

## Comparison: Real vs Demo

| Aspect | Real Mode | Demo Mode |
|--------|-----------|-----------|
| **Time** | 8+ hours | 30 seconds |
| **Screenshots** | Actual images | Metadata only |
| **OCR** | Real text extraction | Pre-generated text |
| **AI Summary** | Ollama API | Template-based |
| **Blockchain** | Same | Same |
| **Purpose** | Production use | Testing/demos |

---

## Commands Summary

```bash
# Generate demo data
loggerheads demo --hours 8

# Reset and start fresh
loggerheads demo --reset

# Different roles
loggerheads demo --hours 8 --role frontend
loggerheads demo --hours 8 --role backend
loggerheads demo --hours 8 --role devops

# Advanced
loggerheads demo --hours 8 --date 2025-10-22
loggerheads demo --hours-range 6-10
loggerheads demo --days 5 --hours 8

# Show summary
loggerheads demo --summary
```

---

## Conclusion

Demo mode solves the **"8-hour wait" problem** for demonstrations. Perfect for:
- 🏆 Hackathon presentations
- 💼 Client demos
- 🧪 Testing
- 📚 Documentation

**Next:** Implement `loggerheads/cli/commands/demo.py` with beautiful Rich output.
