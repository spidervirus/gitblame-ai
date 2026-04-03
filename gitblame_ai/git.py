import subprocess
import sys
from pathlib import Path
from collections import defaultdict

SUPPORTED_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".rs",
    ".java", ".c", ".cpp", ".cs", ".rb", ".php", ".swift",
    ".kt", ".vue", ".html", ".css", ".sh",
}

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
        from .roaster import RED, RESET
        print(f"{RED}No supported code files found.{RESET}")
        sys.exit(1)

    from .roaster import DIM, RESET
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
