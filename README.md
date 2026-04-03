# 🔥 gitblame-ai

> **AI-powered code roaster. `git blame` was always personal — now it's savage.**

```bash
pip install .
gitblame-ai --roast .
```

---

## What is this?

`gitblame-ai` scans your repo with `git blame`, identifies each author's most *suspicious* code, and sends it to Claude AI for a brutally honest roast.

Perfect for:
- 🤣 Team standups
- 💀 Code review sessions
- 🏆 Friday afternoon vibes
- 😬 Holding people accountable in the funniest way possible

---

## Demo

```
  ██████╗ ██╗████████╗██████╗ ██╗      █████╗ ███╗   ███╗███████╗      █████╗ ██╗
 ██╔════╝ ██║╚══██╔══╝██╔══██╗██║     ██╔══██╗████╗ ████║██╔════╝     ██╔══██╗██║
 ...

  Target: ./my-project
  Mode:   roast
  Top:    3 authors

  🔍 Roasting alice@dev.com... done (3/10)
  🔍 Roasting bob@dev.com... done (7/10)
  🔍 Roasting john@dev.com... done (2/10)


══════════════════════════════════════════════════════════════
  🔥  ROAST RESULTS  🔥
══════════════════════════════════════════════════════════════

──────────────────────────────────────────────────────────────
  👤 john@dev.com  (847 lines of... code)
  ████░░░░░░░░░░░░░░░░  💀 2/10
──────────────────────────────────────────────────────────────
  John, your `except: pass` blocks aren't error handling —
  they're crime scenes. You've written `TODO: fix this later`
  17 times across 3 files, which is impressive dedication to
  procrastination. The variable named `data2` next to `data`
  is genuinely haunting. I've seen better architecture in
  a kindergarten Lego set.

  Verdict: 2/10 💀


  🏆 Hall of Shame: john@dev.com
  Congratulations. You've earned it.
```

---

## How it works

1. Runs `git blame --line-porcelain` on all code files.
2. Groups lines by author and filters out uncommitted changes.
3. Scores each line for "badness" (TODOs, bare excepts, long lines, etc.) using modular heuristics.
4. Sends the worst offenders to Claude AI (using `claude-3-5-sonnet`).
5. Renders a beautiful terminal roast card per author.

---

## Installation

Clone the repo and install it in editable mode:

```bash
git clone https://github.com/yourusername/gitblame-ai.git
cd gitblame-ai
pip install -e .
```

Set your Anthropic API key:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

---

## Usage

```bash
# Roast the whole repo (default: top 3 authors)
gitblame-ai .

# Roast a single file
gitblame-ai gitblame_ai/main.py

# Different modes
gitblame-ai . --mode gentle   # Kind but disappointed
gitblame-ai . --mode poetic   # Shakespearean tragedy
gitblame-ai . --mode roast    # Pure savagery (default)

# Top 5 authors
gitblame-ai . --top 5
```

---

## Modes

| Mode | Vibe |
|------|------|
| `roast` | Brutal, savage, funny. No mercy. |
| `gentle` | Constructive. Like a disappointed parent. |
| `poetic` | Shakespeare reviews your spaghetti code. |

---

## Project Structure

```text
gitblame-ai/
├── gitblame_ai/       # Core package
│   ├── git.py         # Git blame parsing & file discovery
│   ├── ai.py          # Anthropic API integration
│   ├── roaster.py     # Heuristics & Terminal UI
│   └── main.py        # CLI Entry point
├── pyproject.toml     # Package configuration
└── README.md          # This file
```

---

## Requirements

- Python 3.10+
- Git repo
- [Anthropic API key](https://console.anthropic.com)

---

## Contributing

PRs welcome. Especially:
- New "badness" heuristics
- More roast modes
- Export to markdown/HTML report
- GitHub Action integration

---

## License

MIT — roast freely, roast often.

---

> *"With great `git blame` comes great responsibility."*
> — probably someone

**[⭐ Star this if your teammates deserve it](https://github.com/yourusername/gitblame-ai)**
