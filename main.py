#!/usr/bin/env python3
"""
gitblame-ai — AI-powered code roaster using git blame.
"""

import subprocess
import sys
import os
import argparse
from pathlib import Path
from collections import defaultdict
from anthropic import Anthropic

client = Anthropic()

# ─── ANSI colors ────────────────────────────────────────────────────────────
RED     = "\033[91m"
YELLOW  = "\033[93m"
GREEN   = "\033[92m"
CYAN    = "\033[96m"
MAGENTA = "\033[95m"
BOLD    = "\033[1m"
DIM     = "\033[2m"
RESET   = "\033[0m"

SUPPORTED_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".rs",
    ".java", ".c", ".cpp", ".cs", ".rb", ".php", ".swift",
    ".kt", ".vue", ".html", ".css", ".sh",
}

BANNER = f"""
{RED}{BOLD}
  ██████╗ ██╗████████╗██████╗ ██╗      █████╗ ███╗   ███╗███████╗      █████╗ ██╗
 ██╔════╝ ██║╚══██╔══╝██╔══██╗██║     ██╔══██╗████╗ ████║██╔════╝     ██╔══██╗██║
 ██║  ███╗██║   ██║   ██████╔╝██║     ███████║██╔████╔██║█████╗       ███████║██║
 ██║   ██║██║   ██║   ██╔══██╗██║     ██╔══██║██║╚██╔╝██║██╔══╝       ██╔══██║██║
 ╚██████╔╝██║   ██║   ██████╔╝███████╗██║  ██║██║ ╚═╝ ██║███████╗     ██║  ██║██║
  ╚═════╝ ╚═╝   ╚═╝   ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝     ╚═╝  ╚═╝╚═╝
{RESET}{DIM}  your code is about to get roasted 🔥{RESET}
"""


def run_git_blame(filepath: str) -> list[dict]:
    """Run git blame on a file and parse output."""
    try:
        result = subprocess.run(
            ["git", "blame", "--line-porcelain", filepath],
            capture_output=True, text=True, check=True
        )
    except subprocess.CalledProcessError:
        return []

    lines = result.stdout.splitlines()
    blame_entries = []
    current = {}

    for line in lines:
        if line.startswith("author ") and "author-mail" not in line:
            current["author"] = line[7:].strip()
        elif line.startswith("author-time "):
            current["timestamp"] = line[12:].strip()
        elif line.startswith("summary "):
            current["commit_msg"] = line[8:].strip()
        elif line.startswith("\t"):
            current["code"] = line[1:]
            blame_entries.append(dict(current))
            current = {}

    return blame_entries


def collect_blame_data(path: str, max_files: int = 10) -> dict:
    """Collect blame data across all code files in a path."""
    target = Path(path)
    author_lines = defaultdict(list)  # author -> list of (file, code, commit_msg)

    if target.is_file():
        files = [target]
    else:
        files = [
            f for f in target.rglob("*")
            if f.suffix in SUPPORTED_EXTENSIONS
            and ".git" not in f.parts
            and "node_modules" not in f.parts
            and "__pycache__" not in f.parts
        ][:max_files]

    if not files:
        print(f"{RED}No supported code files found.{RESET}")
        sys.exit(1)

    print(f"{DIM}  Scanning {len(files)} file(s)...{RESET}\n")

    for f in files:
        entries = run_git_blame(str(f))
        for entry in entries:
            author = entry.get("author", "Unknown")
            code = entry.get("code", "").strip()
            msg = entry.get("commit_msg", "")
            if code and author != "Not Committed Yet":
                author_lines[author].append({
                    "file": str(f),
                    "code": code,
                    "commit_msg": msg,
                })

    return dict(author_lines)


def pick_worst_lines(author_lines: list[dict], n: int = 8) -> list[dict]:
    """Heuristically pick 'suspicious' lines to roast (long, complex, or weird)."""
    def badness_score(entry):
        code = entry["code"]
        score = 0
        score += len(code) // 10                        # long lines
        score += code.count("TODO") * 3                 # TODOs
        score += code.count("FIXME") * 3
        score += code.count("hack") * 2
        score += code.count("temp") * 2
        score += code.count("wtf") * 5
        score += code.count("idk") * 4
        score += code.count("except:") * 3             # bare excepts
        score += code.count("pass") * 2
        score += (1 if "==" in code and "None" in code else 0) * 2
        score += len([c for c in code if c == ';']) * 2
        return score

    sorted_lines = sorted(author_lines, key=badness_score, reverse=True)
    return sorted_lines[:n]


def roast_with_ai(author: str, worst_lines: list[dict], mode: str) -> str:
    """Send code snippets to Claude and get a roast."""
    code_block = "\n".join(
        f"[File: {e['file']}]\n{e['code']}" for e in worst_lines
    )

    tone_map = {
        "roast":  "You are a brutally honest, savage, but funny senior engineer. Roast the code hard. Be specific about what's wrong. Use dark humor. Be merciless but don't be mean about the person — just the code.",
        "gentle": "You are a kind but slightly disappointed senior engineer. Give constructive feedback with a hint of sadness about the code quality. Be encouraging but honest.",
        "poetic": "You are a Shakespearean bard who reviews code as if reciting dramatic poetry. Use archaic language and dramatic metaphors about the tragedy of bad code.",
    }

    system = tone_map.get(mode, tone_map["roast"])

    prompt = f"""
Author: {author}
Their code samples:
{code_block}

Write a SHORT roast (4-6 sentences max). Be specific — reference actual patterns from the code.
End with a 'Verdict' rating out of 10 (1 = absolute disaster, 10 = suspiciously clean).
Format: just the roast text, then on a new line: Verdict: X/10
"""

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}],
        system=system,
    )

    return response.content[0].text.strip()


def extract_score(roast_text: str) -> int:
    """Extract numeric score from roast text."""
    import re
    match = re.search(r"Verdict:\s*(\d+)/10", roast_text)
    return int(match.group(1)) if match else 5


def print_roast_card(author: str, roast: str, score: int, line_count: int):
    """Print a styled roast card for an author."""
    bar_filled = int((score / 10) * 20)
    bar_empty = 20 - bar_filled

    if score <= 3:
        score_color = RED
        emoji = "💀"
    elif score <= 6:
        score_color = YELLOW
        emoji = "😬"
    else:
        score_color = GREEN
        emoji = "✅"

    bar = f"{score_color}{'█' * bar_filled}{RESET}{DIM}{'░' * bar_empty}{RESET}"

    print(f"\n{BOLD}{'─' * 60}{RESET}")
    print(f"  {CYAN}{BOLD}👤 {author}{RESET}  {DIM}({line_count} lines of... code){RESET}")
    print(f"  {bar}  {score_color}{BOLD}{emoji} {score}/10{RESET}")
    print(f"{'─' * 60}{RESET}")

    # Word-wrap roast text
    words = roast.replace("Verdict: " + str(score) + "/10", "").strip().split()
    line = "  "
    for word in words:
        if len(line) + len(word) + 1 > 70:
            print(line)
            line = "  " + word + " "
        else:
            line += word + " "
    if line.strip():
        print(line)

    print(f"\n  {score_color}{BOLD}Verdict: {score}/10{RESET} {emoji}")


def run(path: str, mode: str, top: int):
    print(BANNER)
    print(f"  {CYAN}Target:{RESET} {path}")
    print(f"  {CYAN}Mode:{RESET}   {mode}")
    print(f"  {CYAN}Top:{RESET}    {top} authors\n")

    author_data = collect_blame_data(path)

    if not author_data:
        print(f"{RED}No git blame data found. Is this a git repo?{RESET}")
        sys.exit(1)

    # Sort authors by line count (most prolific = most to roast)
    sorted_authors = sorted(author_data.items(), key=lambda x: len(x[1]), reverse=True)[:top]

    results = []

    for author, lines in sorted_authors:
        print(f"  {MAGENTA}🔍 Roasting {author}...{RESET}", end="", flush=True)
        worst = pick_worst_lines(lines)
        roast = roast_with_ai(author, worst, mode)
        score = extract_score(roast)
        print(f" done {DIM}({score}/10){RESET}")
        results.append((author, roast, score, len(lines)))

    print(f"\n\n{BOLD}{RED}{'═' * 60}{RESET}")
    print(f"{BOLD}{RED}  🔥  ROAST RESULTS  🔥{RESET}")
    print(f"{BOLD}{RED}{'═' * 60}{RESET}")

    # Sort by score ascending (worst first)
    results.sort(key=lambda x: x[2])

    for author, roast, score, line_count in results:
        print_roast_card(author, roast, score, line_count)

    # Hall of shame
    worst_author = results[0][0]
    print(f"\n\n  {RED}{BOLD}🏆 Hall of Shame: {worst_author}{RESET}")
    print(f"  {DIM}Congratulations. You've earned it.{RESET}\n")


def main():
    parser = argparse.ArgumentParser(
        prog="gitblame-ai",
        description="🔥 AI-powered code roaster using git blame",
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="File or directory to roast (default: current directory)",
    )
    parser.add_argument(
        "--mode",
        choices=["roast", "gentle", "poetic"],
        default="roast",
        help="Roast style: roast (savage), gentle (kind-ish), poetic (Shakespeare)",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=3,
        help="Number of top authors to roast (default: 3)",
    )

    args = parser.parse_args()

    if not os.getenv("ANTHROPIC_API_KEY"):
        print(f"{RED}Error: ANTHROPIC_API_KEY environment variable not set.{RESET}")
        print(f"{DIM}Get your key at: https://console.anthropic.com{RESET}")
        sys.exit(1)

    run(args.path, args.mode, args.top)


if __name__ == "__main__":
    main()
