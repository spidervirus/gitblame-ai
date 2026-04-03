from anthropic import Anthropic

def roast_with_ai(author: str, worst_lines: list[dict], mode: str) -> str:
    """Send code snippets to Claude and get a roast."""
    client = Anthropic()
    
    code_block = "\n".join(
        f"[File: {e['file']}]\n{e['code']}" for e in worst_lines
    )

    tone_map = {
        "roast":  "You are a brutally honest, savage, but funny senior engineer. Roast the code hard. Be specific about what's wrong. Use dark humor. Be merciless but don't be mean about the person — just the code.",
        "gentle": "You are a kind but slightly disappointed senior engineer. Give constructive feedback with a hint of sadness about the code quality. Be encouraging but honest.",
        "poetic": "You are a Shakespearean bard who reviews code as if reciting dramatic poetry. Use archaic language and dramatic metaphors about the tragedy of bad code.",
        "pirate": "You are a swashbuckling pirate captain who is disappointed in the crew's 'spaghetti' code. Use lots of pirate slang (Arrr, matey, walk the plank) and nautical metaphors.",
        "corporate": "You are a passive-aggressive middle manager. Use heavy corporate jargon (synergy, circle back, low-hanging fruit, bandwidth). Be polite on the surface but deeply condescending about the lack of 'best-in-class' standards.",
        "valley_girl": "You are a stereotypical Valley Girl. Use 'like', 'literally', 'oh my god', and 'toxic'. Treat the bad code like a major fashion faux pas or social disaster.",
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

    # Note: Using a standard model name that exists
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}],
        system=system,
    )

    return response.content[0].text.strip()
