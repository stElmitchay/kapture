"""
Application-based work analyzer.
Detects what apps the user was using and generates summaries based on that,
instead of trying to extract keywords from OCR text.
"""

import re
from collections import Counter
from datetime import datetime


# App categories
WORK_APPS = {
    'code_editors': [
        'cursor', 'vscode', 'visual studio code', 'pycharm', 'sublime',
        'atom', 'vim', 'neovim', 'emacs', 'intellij', 'webstorm'
    ],
    'terminals': [
        'terminal', 'iterm', 'zsh', 'bash', 'powershell', 'cmd',
        'hyper', 'alacritty', 'wezterm'
    ],
    'browsers_work': [
        'github', 'stackoverflow', 'stack overflow', 'documentation',
        'docs.', 'readthedocs', 'npm', 'pypi', 'crates.io',
        'developer.', 'api.', 'localhost'
    ],
    'design_tools': [
        'figma', 'sketch', 'adobe xd', 'inkscape', 'gimp'
    ],
    'communication_work': [
        'slack', 'discord', 'zoom', 'microsoft teams', 'telegram'
    ]
}

# Context indicators - words/phrases that indicate work-related content
WORK_CONTEXT_INDICATORS = [
    # Technical terms
    'api', 'documentation', 'docs', 'tutorial', 'guide', 'error', 'bug',
    'code', 'programming', 'development', 'deploy', 'server', 'database',
    'function', 'class', 'variable', 'import', 'export', 'build', 'test',
    'repository', 'commit', 'branch', 'pull request', 'merge', 'git',

    # Work-related terms
    'project', 'deadline', 'meeting', 'client', 'task', 'sprint', 'issue',
    'feature', 'requirement', 'specification', 'design', 'architecture',
    'implementation', 'review', 'approval', 'proposal', 'contract',

    # Technical platforms
    'github', 'stackoverflow', 'stack overflow', 'npm', 'pypi', 'cargo',
    'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'vercel', 'netlify',

    # Blockchain/crypto (for your specific work)
    'solana', 'ethereum', 'blockchain', 'smart contract', 'wallet',
    'token', 'nft', 'defi', 'web3', 'crypto', 'anchor', 'rust',

    # Learning/research
    'how to', 'learn', 'understand', 'explain', 'course', 'lesson',
    'example', 'sample', 'demo', 'proof of concept', 'poc'
]

# Non-work context indicators
NON_WORK_CONTEXT_INDICATORS = [
    'birthday', 'party', 'weekend', 'vacation', 'holiday', 'concert',
    'movie', 'music', 'game', 'sport', 'football', 'basketball',
    'recipe', 'cooking', 'restaurant', 'food', 'shopping', 'buy',
    'sale', 'discount', 'price', 'order', 'delivery',
    'funny', 'lol', 'haha', 'meme', 'cute', 'awesome'
]

# Potentially work apps (need context to determine)
CONTEXT_DEPENDENT_APPS = [
    'youtube', 'whatsapp', 'twitter', 'reddit', 'facebook',
    'chrome', 'safari', 'firefox', 'edge'
]


def detect_work_context(ocr_text):
    """
    Determine if the content is work-related based on context, not just the app.

    Args:
        ocr_text (str): OCR text

    Returns:
        dict: {'is_work': bool, 'confidence': float, 'indicators': list}
    """
    if not ocr_text:
        return {'is_work': False, 'confidence': 0.0, 'indicators': []}

    text_lower = ocr_text.lower()
    work_score = 0
    non_work_score = 0
    indicators_found = []

    # Count work indicators
    for indicator in WORK_CONTEXT_INDICATORS:
        if indicator in text_lower:
            work_score += 1
            indicators_found.append(indicator)

    # Count non-work indicators
    for indicator in NON_WORK_CONTEXT_INDICATORS:
        if indicator in text_lower:
            non_work_score += 1

    # Calculate confidence
    total_score = work_score + non_work_score
    if total_score == 0:
        return {'is_work': True, 'confidence': 0.3, 'indicators': []}  # Default: assume work

    work_confidence = work_score / total_score

    return {
        'is_work': work_score > non_work_score,
        'confidence': work_confidence,
        'indicators': indicators_found
    }


def detect_app_from_text(ocr_text):
    """
    Detect what application is shown in the screenshot based on OCR text.
    Uses CONTEXT for ambiguous apps like YouTube, WhatsApp, browsers.

    Args:
        ocr_text (str): OCR extracted text

    Returns:
        dict: {'app_type': str, 'app_name': str, 'is_work': bool, 'context': dict}
    """
    if not ocr_text:
        return {'app_type': 'unknown', 'app_name': 'unknown', 'is_work': False, 'context': {}}

    text_lower = ocr_text.lower()

    # Check if it's a definitely work app (code editors, terminals)
    for category, apps in WORK_APPS.items():
        for app in apps:
            if app in text_lower:
                return {
                    'app_type': category,
                    'app_name': app,
                    'is_work': True,
                    'context': {'reason': 'work_app'}
                }

    # Check if it's a context-dependent app (YouTube, WhatsApp, browsers)
    detected_app = None
    for app in CONTEXT_DEPENDENT_APPS:
        if app in text_lower:
            detected_app = app
            break

    if detected_app:
        # Use context to determine if it's work-related
        context = detect_work_context(ocr_text)
        return {
            'app_type': 'context_dependent',
            'app_name': detected_app,
            'is_work': context['is_work'],
            'context': context
        }

    # Default: assume work if we can't tell (conservative approach)
    return {
        'app_type': 'unknown',
        'app_name': 'unknown',
        'is_work': True,
        'context': {'reason': 'default_work'}
    }


def extract_file_mentions(ocr_text):
    """
    Extract mentions of files being edited.

    Args:
        ocr_text (str): OCR text

    Returns:
        list: List of filenames found
    """
    if not ocr_text:
        return []

    # Pattern: filename.extension
    file_pattern = r'\b(\w+\.(py|js|ts|jsx|tsx|rs|go|java|cpp|c|h|md|txt|json|yaml|yml|toml|sql|sh|bash))\b'
    files = re.findall(file_pattern, ocr_text, re.IGNORECASE)
    return [f[0] for f in files if f[0]]


def extract_git_activity(ocr_text):
    """
    Extract git commands/activity.

    Args:
        ocr_text (str): OCR text

    Returns:
        list: Git activities detected
    """
    if not ocr_text:
        return []

    activities = []
    text_lower = ocr_text.lower()

    git_commands = {
        'git push': 'Pushed changes to remote',
        'git commit': 'Committed changes',
        'git pull': 'Pulled updates',
        'git merge': 'Merged branches',
        'git checkout': 'Switched branches',
        'git add': 'Staged changes'
    }

    for command, activity in git_commands.items():
        if command in text_lower:
            activities.append(activity)

    return activities


def generate_app_based_summary(screenshots_data):
    """
    Generate work summary based on application usage.

    Args:
        screenshots_data (list): List of dicts with 'ocr_text' and 'timestamp'

    Returns:
        dict: Summary with tasks, apps used, etc.
    """
    if not screenshots_data:
        return {
            'tasks_worked_on': [],
            'completed_tasks': [],
            'problems_blockers': [],
            'apps_used': {},
            'files_edited': [],
            'total_screenshots': 0,
            'work_screenshots': 0,
            'non_work_screenshots': 0
        }

    all_apps = []
    all_files = []
    all_git_activities = []
    work_count = 0
    non_work_count = 0

    for item in screenshots_data:
        ocr_text = item.get('ocr_text', '')

        # Detect app
        app_info = detect_app_from_text(ocr_text)
        all_apps.append(app_info['app_name'])

        if app_info['is_work']:
            work_count += 1

            # Extract files mentioned
            files = extract_file_mentions(ocr_text)
            all_files.extend(files)

            # Extract git activity
            git_activities = extract_git_activity(ocr_text)
            all_git_activities.extend(git_activities)
        else:
            non_work_count += 1

    # Count app usage
    app_counts = Counter(all_apps)
    file_counts = Counter(all_files)

    # Generate task list based on apps and files
    tasks = []

    # Code editor usage
    code_editor_count = sum(count for app, count in app_counts.items()
                           if app in WORK_APPS['code_editors'])
    if code_editor_count > 0:
        if file_counts:
            # List specific files
            for file, count in file_counts.most_common(10):
                tasks.append(f"Worked on {file}")
        else:
            tasks.append(f"Code editing session ({code_editor_count} screenshots)")

    # Terminal usage
    terminal_count = sum(count for app, count in app_counts.items()
                        if app in WORK_APPS['terminals'])
    if terminal_count > 0:
        if all_git_activities:
            tasks.extend(set(all_git_activities))
        else:
            tasks.append(f"Terminal/command line work ({terminal_count} screenshots)")

    # Browser/research
    browser_work_count = sum(count for app, count in app_counts.items()
                            if app in WORK_APPS['browsers_work'])
    if browser_work_count > 0:
        tasks.append(f"Technical research and documentation ({browser_work_count} screenshots)")

    return {
        'tasks_worked_on': tasks if tasks else ['Active work session detected'],
        'completed_tasks': list(set(all_git_activities)),  # Git activities = completions
        'problems_blockers': [],  # Can't detect from app usage alone
        'apps_used': dict(app_counts.most_common()),
        'files_edited': list(set(all_files)),
        'total_screenshots': len(screenshots_data),
        'work_screenshots': work_count,
        'non_work_screenshots': non_work_count,
        'work_percentage': round((work_count / len(screenshots_data)) * 100) if screenshots_data else 0
    }


def format_app_summary_for_display(summary):
    """
    Format app-based summary for display.

    Args:
        summary (dict): Summary from generate_app_based_summary()

    Returns:
        str: Formatted string
    """
    lines = []

    # What I Worked on Today
    lines.append("✅ What I Worked on Today:")
    tasks = summary.get('tasks_worked_on', [])
    if tasks:
        for task in tasks:
            lines.append(f"  • {task}")
    else:
        lines.append("  • No specific tasks detected")
    lines.append("")

    # What I Completed
    lines.append("🏁 What I Completed:")
    completed = summary.get('completed_tasks', [])
    if completed:
        for item in completed:
            lines.append(f"  • {item}")
    else:
        lines.append("  • In progress - no completions detected yet")
    lines.append("")

    # Work Stats
    lines.append("📊 Work Statistics:")
    lines.append(f"  • Total activity: {summary.get('total_screenshots', 0)} screenshots")
    lines.append(f"  • Work-related: {summary.get('work_screenshots', 0)} ({summary.get('work_percentage', 0)}%)")
    lines.append(f"  • Non-work: {summary.get('non_work_screenshots', 0)}")

    if summary.get('files_edited'):
        lines.append(f"  • Files edited: {len(summary['files_edited'])}")

    lines.append("")

    # Problems/Blockers
    lines.append("⚠️ Issues / Blockers:")
    problems = summary.get('problems_blockers', [])
    if problems:
        for problem in problems:
            lines.append(f"  • {problem}")
    else:
        lines.append("  • None identified")

    return "\n".join(lines)
