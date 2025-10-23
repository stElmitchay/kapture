"""
AI-powered summarization using Ollama local LLM.
Converts raw OCR text into intelligent work summaries.
"""

import requests
import json
from datetime import datetime
from rich.console import Console
from .user_context import get_user_context

console = Console()


def summarize_work_with_ai(all_ocr_text, ollama_url, ollama_model, is_friday=False):
    """
    Use Ollama local LLM to analyze all OCR text and generate intelligent work summary.

    Args:
        all_ocr_text (list): List of OCR text strings from all screenshots
        ollama_url (str): Ollama API URL (e.g., http://localhost:11434)
        ollama_model (str): Ollama model name (e.g., llama3.2)
        is_friday (bool): Whether today is Friday

    Returns:
        dict: Structured summary with all sections
    """
    if not all_ocr_text or len(all_ocr_text) == 0:
        console.print("[bold red]❌ No OCR text to analyze[/bold red]")
        return None

    # Sample screenshots if too many (take every Nth screenshot for better coverage)
    original_count = len(all_ocr_text)
    if len(all_ocr_text) > 30:
        sample_rate = max(2, len(all_ocr_text) // 30)
        all_ocr_text = all_ocr_text[::sample_rate]
        console.print(f"[cyan]📊 Sampled {len(all_ocr_text)} screenshots from {original_count} total (every {sample_rate}th)[/cyan]")

    # Combine all OCR text
    combined_text = "\n\n---SCREENSHOT---\n\n".join(all_ocr_text)

    # Truncate if still too long
    max_chars = 5000000  # Conservative limit for local models
    if len(combined_text) > max_chars:
        console.print(f"[yellow]⚠️  Text still too long ({len(combined_text)} chars), truncating to {max_chars}[/yellow]")
        combined_text = combined_text[:max_chars]

    # Get user context for intelligent categorization
    user_context = get_user_context()
    user_context_prompt = user_context.get_user_context_prompt()

    # Create the prompt
    today = datetime.now().strftime("%A, %B %d, %Y")

    prompt = f"""You are analyzing screenshots from a user's workday to generate an accurate, narrative-focused daily work summary.

Today is: {today}

{user_context_prompt}

Below is OCR-extracted text from screenshots taken throughout the day. The text is messy and fragmented because it's from OCR.

UNDERSTANDING THE CONTEXT:
Screenshots capture what the user is LOOKING AT on their screen, NOT what they created. You must carefully distinguish between:
- Content the user is CONSUMING (reading, browsing, viewing)
- Content the user is PRODUCING (writing, editing, building, coding)

CRITICAL: WRITE NARRATIVELY, NOT MECHANICALLY
❌ BAD (mechanical, file-focused):
  - "Worked on README.md"
  - "Worked on CLAUDE.md"
  - "Pushed changes to remote"
  - "Committed changes"

✅ GOOD (narrative, context-focused):
  - "Explored Solana Actions (SAS) to better understand how to implement them in the upcoming hackathon projects"
  - "Encountered several issues with the documentation and example repositories, including broken references and mismatched dependencies"
  - "Debugged and fixed all the errors by the end of the day, confirming successful action registration and endpoint response"
  - "Continued working on boilerplate code for the investment tracking idea"

SUMMARY WRITING GUIDELINES:
1. **Tell a story** - Group related activities into cohesive narratives
2. **Explain WHY, not just WHAT** - Why were you working on this? What was the goal?
3. **Be specific about OUTCOMES** - What did you learn? What did you fix? What progress was made?
4. **Avoid listing filenames** - Instead describe the feature/project/problem you were working on
5. **Quality over quantity** - 3-5 well-written narrative bullets > 10 mechanical file mentions
6. **Connect the dots** - If you see multiple related files/activities, synthesize them into one narrative

CONTENT CLASSIFICATION:
1. **Code Editors (VS Code, PyCharm, etc.)**:
   - Look for filenames in window titles or visible in the editor
   - Instead of "Edited setup.py", write "Configured project dependencies and build settings"
   - Instead of "Worked on blockchain.py", write "Implemented blockchain integration for transaction logging"

2. **Terminal/Command Line**:
   - Look for what the commands ACCOMPLISHED, not just that they ran
   - Instead of "Ran tests", write "Verified authentication flow works correctly with new OAuth provider"
   - Instead of "Installed dependencies", write "Set up development environment for Solana smart contract project"

3. **Web Browsers**:
   - If viewing documentation/tutorials: Explain what you were trying to learn/solve
   - Instead of "Researched React hooks", write "Researched React hooks patterns to improve state management in the dashboard component"
   - DO NOT report example code or tutorial content as your work

4. **Documentation/Tutorial Sites**:
   - Focus on the LEARNING GOAL, not the tutorial title
   - Instead of "Read Solana documentation", write "Studied Solana program deployment process to prepare for hackathon project"

5. **Twitter/Social Media**:
   - Only report if directly work-related (Solana ecosystem news, industry updates)
   - Mention the NEWS, not just that you browsed Twitter

QUALITY CHECKS - Before writing each item:
1. Does this explain CONTEXT and PURPOSE? (Good)
2. Does this just list a filename or command? (Bad - rewrite it)
3. Would someone reading this understand what I accomplished and why? (Good)
4. Is this grouped with related activities into a coherent narrative? (Good)

OCR TEXT FROM SCREENSHOTS:
{combined_text}

Generate a summary in this EXACT format:

WORKED_ON:
[Write 3-7 narrative bullets that tell the story of your day. Each bullet should:
- Explain WHAT you worked on and WHY
- Group related files/activities together
- Focus on features/problems/goals, not individual filenames
- Be specific about context and progress made
If you see very little actual work, write "Limited work activity detected - mostly research and planning"]

COMPLETED:
[List only tasks with CLEAR EVIDENCE of completion:
- Tests passing (show what was tested)
- Features deployed (explain what feature)
- Bugs fixed (describe the bug and fix)
- Tutorials/courses finished (mention what you learned)
Be conservative and specific. If uncertain, write "No specific completions identified - work in progress"]

SOLANA_NEWS:
[If you see Twitter/news about Solana ecosystem:
- Quote the actual news/announcement
- Explain why it's relevant to the user's work
If none, write "No Solana news captured in screenshots"]

BLOCKERS:
[List SPECIFIC technical problems you see:
- Error messages (quote the error)
- Failed tests (which tests, why they failed)
- Documentation issues (what was confusing/broken)
If none, write "No significant blockers identified"]

TOMORROW_FOCUS:
{'[Skip this section - it is Friday]' if is_friday else '[Based on incomplete work, suggest 2-3 specific next actions:\n- Continue [specific feature/task] by [specific next step]\n- Focus on [area that needs attention]\nBe actionable and specific. If unclear, write "Continue current project momentum"]'}

FINAL CHECK - Before submitting:
✓ Every item is narrative and contextual (not mechanical)
✓ No standalone filenames without context
✓ Related activities are grouped together
✓ Each bullet explains WHY and WHAT was accomplished
✓ Zero hallucination - only what you actually saw in screenshots
"""

    try:
        console.print(f"[bold magenta]🤖 Calling Ollama ({ollama_model}) to analyze work...[/bold magenta]")

        # Call Ollama API
        response = requests.post(
            f"{ollama_url}/api/generate",
            json={
                "model": ollama_model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 2000
                }
            },
            timeout=120  # 2 minute timeout for local processing
        )

        if response.status_code != 200:
            console.print(f"[bold red]❌ Ollama API error: {response.status_code}[/bold red]")
            return None

        # Parse the response
        response_json = response.json()
        response_text = response_json.get("response", "")

        if not response_text:
            console.print("[bold red]❌ No response from Ollama[/bold red]")
            return None

        # Parse the structured response
        summary = parse_ai_response(response_text, is_friday)

        console.print("[bold green]✅ AI analysis complete[/bold green]")
        return summary

    except requests.exceptions.ConnectionError:
        console.print("[bold red]❌ Could not connect to Ollama.[/bold red] Make sure Ollama is running (ollama serve)")
        return None
    except requests.exceptions.Timeout:
        console.print("[bold red]❌ Ollama request timed out.[/bold red] The model might be too slow or the text too long.")
        return None
    except Exception as e:
        console.print(f"[bold red]❌ Error calling Ollama: {e}[/bold red]")
        return None


def parse_ai_response(response_text, is_friday):
    """
    Parse Claude's response into structured format.

    Args:
        response_text (str): Claude's response
        is_friday (bool): Whether today is Friday

    Returns:
        dict: Structured summary
    """
    summary = {
        'tasks_worked_on': [],
        'completed_tasks': [],
        'solana_news': [],
        'problems_blockers': [],
        'tomorrow_focus': [],
        'is_friday': is_friday
    }

    current_section = None

    for line in response_text.split('\n'):
        line = line.strip()

        if line.startswith('WORKED_ON:'):
            current_section = 'tasks_worked_on'
            continue
        elif line.startswith('COMPLETED:'):
            current_section = 'completed_tasks'
            continue
        elif line.startswith('SOLANA_NEWS:'):
            current_section = 'solana_news'
            continue
        elif line.startswith('BLOCKERS:'):
            current_section = 'problems_blockers'
            continue
        elif line.startswith('TOMORROW_FOCUS:'):
            current_section = 'tomorrow_focus' if not is_friday else None
            continue

        # Add content to current section
        if current_section and line and not line.startswith('['):
            # Remove bullet points and clean up
            clean_line = line.lstrip('•-*').strip()
            if clean_line and len(clean_line) > 5:
                summary[current_section].append(clean_line)

    return summary


def format_ai_summary_for_display(summary):
    """
    Format AI-generated summary for display using exact specified template.

    Args:
        summary (dict): Structured summary from AI

    Returns:
        str: Formatted string for display
    """
    lines = []

    # ✅ What I Worked on Today
    lines.append("✅ What I Worked on Today:")
    tasks = summary.get('tasks_worked_on', [])
    if tasks:
        for task in tasks:
            # Add bullet point if not already present
            task_line = task if task.startswith('-') or task.startswith('•') else f"- {task}"
            lines.append(task_line)
    else:
        lines.append("- Limited work activity detected")
    lines.append("")

    # 🏁 What I Completed
    completed = summary.get('completed_tasks', [])
    if completed and completed[0] != "No specific completions identified from screenshots" and completed[0] != "No specific completions identified - work in progress":
        lines.append("🏁 What I Completed:")
        for item in completed:
            # Add bullet point if not already present
            item_line = item if item.startswith('-') or item.startswith('•') else f"- {item}"
            lines.append(item_line)
        lines.append("")

    # 📰 What's the latest in the Solana Ecosystem
    solana_news = summary.get('solana_news', [])
    if solana_news and solana_news[0] != "No Solana news captured in screenshots":
        lines.append("📰 What's the latest in the Solana Ecosystem:")
        for news in solana_news:
            # Add bullet point if not already present
            news_line = news if news.startswith('-') or news.startswith('•') else f"- {news}"
            lines.append(news_line)
        lines.append("")

    # ⚠️ Issues / Blockers
    lines.append("⚠️ Issues / Blockers:")
    blockers = summary.get('problems_blockers', [])
    if blockers and blockers[0] != "No significant blockers identified":
        for blocker in blockers:
            # Add bullet point if not already present
            blocker_line = blocker if blocker.startswith('-') or blocker.startswith('•') else f"- {blocker}"
            lines.append(blocker_line)
    else:
        lines.append("- None identified")
    lines.append("")

    # 🔜 Focus for Tomorrow
    if not summary.get('is_friday', False):
        lines.append("🔜 Focus for Tomorrow:")
        tomorrow = summary.get('tomorrow_focus', [])
        if tomorrow and tomorrow[0] != "Continue current project momentum" and "Continue current project work" not in tomorrow[0]:
            for focus in tomorrow:
                # Add bullet point if not already present
                focus_line = focus if focus.startswith('-') or focus.startswith('•') else f"- {focus}"
                lines.append(focus_line)
        else:
            # Show the generic message if that's what we got
            lines.append(f"- {tomorrow[0] if tomorrow else 'Continue current project work'}")
        lines.append("")

    return "\n".join(lines)
