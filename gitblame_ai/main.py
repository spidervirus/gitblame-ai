import argparse
import os
import sys

from .git import collect_blame_data
from .ai import roast_with_ai
from .roaster import (
    BANNER, RED, CYAN, MAGENTA, RESET, DIM, BOLD,
    pick_worst_lines, extract_score, print_roast_card
)

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
    if results:
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
        choices=["roast", "gentle", "poetic", "pirate", "corporate", "valley_girl"],
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
