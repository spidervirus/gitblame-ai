import re

# ─── ANSI colors ────────────────────────────────────────────────────────────
RED     = "\033[91m"
YELLOW  = "\033[93m"
GREEN   = "\033[92m"
CYAN    = "\033[96m"
MAGENTA = "\033[95m"
BOLD    = "\033[1m"
DIM     = "\033[2m"
RESET   = "\033[0m"

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

def extract_score(roast_text: str) -> int:
    """Extract numeric score from roast text."""
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
