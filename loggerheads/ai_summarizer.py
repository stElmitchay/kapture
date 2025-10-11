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

    prompt = f"""You are analyzing screenshots from a user's workday to generate an accurate daily work summary.

Today is: {today}

{user_context_prompt}

Below is OCR-extracted text from screenshots taken throughout the day. The text is messy and fragmented because it's from OCR.

UNDERSTANDING THE CONTEXT:
Screenshots capture what the user is LOOKING AT on their screen, NOT what they created. You must carefully distinguish between:
- Content the user is CONSUMING (reading, browsing, viewing)
- Content the user is PRODUCING (writing, editing, building, coding)

CRITICAL RULES:
1. **Code Editors (VS Code, PyCharm, etc.)**:
   - Look for filenames in window titles or visible in the editor
   - Report: "Edited [filename]" or "Worked on [project/file]"
   - Don't report: generic code snippets without context

2. **Terminal/Command Line**:
   - Report commands the user typed and ran
   - Report: "Ran tests", "Deployed to production", "Installed dependencies"
   - Don't report: command output unless it shows errors/blockers

3. **Web Browsers**:
   - This is where most errors happen! Be very careful here.
   - If viewing documentation/tutorials: Report "Researched [topic/technology]"
   - DO NOT report example code, sample projects, or tutorial content as work done
   - Example: Seeing "Build a Todo App Tutorial" → Report: "Researched web app development"
   - Example: Seeing tutorial code for a chat app → Report: "Studied chat application patterns"
   - DO NOT say "I built X" unless you see it in a code editor with filenames

4. **Documentation/Tutorial Sites**:
   - These show EXAMPLE content, not YOUR content
   - Only mention you researched/learned the topic
   - Never claim you built the examples shown

5. **Twitter/Social Media**:
   - Only report if it's directly work-related (e.g., Solana news for your industry)
   - Don't report casual browsing

6. **Communication Tools (Slack, Discord, Email)**:
   - Report topics discussed if work-related
   - Don't include personal chats

QUALITY CHECKS - Ask yourself for EACH item:
1. Did I see this in a CODE EDITOR with a filename? → OK to report as "worked on"
2. Did I see this run in a TERMINAL? → OK to report as "ran/executed"
3. Did I see this on a WEBSITE/TUTORIAL? → Only report "researched [topic]", NOT the example content
4. Can I identify a specific file, command, or project name? → Good, be specific
5. Is this just example/demo content from a tutorial? → DO NOT report as work done

OCR TEXT FROM SCREENSHOTS:
{combined_text}

Generate a summary in this EXACT format:

WORKED_ON:
[List ONLY activities where you saw the user CREATING something (editing files, writing code, running commands, building projects). Include specific filenames/projects. For web research, only say "Researched [topic]" - do NOT mention the example content shown. Minimum 3-8 items. If you see almost no actual work, write "Limited work activity detected"]

COMPLETED:
[List ONLY tasks with clear evidence of completion (tests passing, PR merged, deployment succeeded, tutorial finished). Be conservative. If uncertain, write "No specific completions identified from screenshots"]

SOLANA_NEWS:
[List ONLY if you see Twitter/news screenshots about Solana. Quote what you saw. If none, write "No Solana news captured in screenshots"]

BLOCKERS:
[List ONLY specific errors, failed tests, or problems you see in terminal/console output. If none, write "No significant blockers identified"]

TOMORROW_FOCUS:
{"[Skip this section - it's Friday]" if is_friday else "[Based on what was started but not completed, suggest 2-3 specific next steps. If unclear, write 'Continue with current project work']"}

FINAL CHECK - Before submitting, verify:
✓ No example/tutorial content reported as user's work
✓ Every "worked on" item is from code editor, terminal, or has specific filename/project
✓ Web browsing reported only as "researched [topic]", not the examples shown
✓ Zero hallucination - only what you actually saw
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
            lines.append(f"{task}")
    else:
        lines.append("[List specific tasks you worked on - be detailed, not vague]")
        lines.append("[Mention key progress made on projects]")
    lines.append("")

    # 🏁 What I Completed
    completed = summary.get('completed_tasks', [])
    if completed:
        lines.append("🏁 What I Completed:")
        for item in completed:
            lines.append(f"{item}")
        lines.append("")

    # 📰 What's the latest in the Solana Ecosystem
    solana_news = summary.get('solana_news', [])
    if solana_news and solana_news[0] != "No Solana news captured in screenshots":
        lines.append("📰 What's the latest in the Solana Ecosystem:")
        for news in solana_news:
            lines.append(f"{news}")
        lines.append("")

    # ⚠️ Issues / Blockers
    lines.append("⚠️ Issues / Blockers:")
    blockers = summary.get('problems_blockers', [])
    if blockers and blockers[0] != "No significant blockers identified":
        for blocker in blockers:
            lines.append(f"{blocker}")
    else:
        lines.append("[Mention specific challenges or dependencies]")
        lines.append("[Explain what help you need or how you're addressing them]")
    lines.append("")

    # 🔜 Focus for Tomorrow
    if not summary.get('is_friday', False):
        lines.append("🔜 Focus for Tomorrow:")
        tomorrow = summary.get('tomorrow_focus', [])
        if tomorrow:
            for focus in tomorrow:
                lines.append(f"{focus}")
        else:
            lines.append("[List specific priorities for the next day]")
        lines.append("")

    return "\n".join(lines)
