#!/usr/bin/env python3
"""
cli.py — parses a raw `/deck-architect <args>` invocation string into
structured intake parameters. This does NOT generate the deck itself (that's
Claude's job, following SKILL.md, ending in build_deck.py) — it's a small
helper so both Claude Desktop and Claude Code can present a consistent parsed
summary of what the user typed before Claude asks any remaining clarifying
questions.

Usage:
    python3 cli.py "LangGraph + LangSmith (20 slides, advanced, AWS+GCP, PPTX+PDF)"

Prints a JSON object with whatever fields it could confidently parse; missing
fields are simply absent so the caller knows to ask about them.
"""

import argparse
import json
import re
import sys

PROVIDER_KEYWORDS = {
    "aws": "AWS",
    "amazon": "AWS",
    "bedrock": "AWS",
    "gcp": "GCP",
    "google cloud": "GCP",
    "vertex": "GCP",
    "azure": "Azure",
    "kubernetes": "CNCF",
    "k8s": "CNCF",
    "cncf": "CNCF",
}

LEVEL_KEYWORDS = {
    "fundamentals": "Fundamentals",
    "beginner": "Fundamentals",
    "intro": "Fundamentals",
    "intermediate": "Intermediate",
    "advanced": "Advanced",
    "deep dive": "Advanced",
}

FORMAT_KEYWORDS = {
    "pptx": "PPTX",
    "powerpoint": "PPTX",
    "pdf": "PDF",
}


def parse_slide_count(text: str):
    m = re.search(r"(\d{1,3})\s*slides?", text, re.IGNORECASE)
    if m:
        n = int(m.group(1))
        if 3 <= n <= 60:
            return n
    return None


def parse_providers(text: str):
    lower = text.lower()
    found = []
    for kw, provider in PROVIDER_KEYWORDS.items():
        if kw in lower and provider not in found:
            found.append(provider)
    return found


def parse_level(text: str):
    lower = text.lower()
    for kw, level in LEVEL_KEYWORDS.items():
        if kw in lower:
            return level
    return None


def parse_formats(text: str):
    lower = text.lower()
    found = []
    for kw, fmt in FORMAT_KEYWORDS.items():
        if kw in lower and fmt not in found:
            found.append(fmt)
    return found


def strip_parenthetical(text: str):
    """Return the topic with any trailing (...) parameter block removed."""
    return re.sub(r"\s*\([^)]*\)\s*$", "", text).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("invocation", help="Raw text following /deck-architect")
    args = ap.parse_args()

    raw = args.invocation.strip()
    topic = strip_parenthetical(raw)

    result = {
        "topic": topic,
        "raw_invocation": raw,
    }

    slide_count = parse_slide_count(raw)
    if slide_count:
        result["slides"] = slide_count

    providers = parse_providers(raw)
    if providers:
        result["providers"] = providers

    level = parse_level(raw)
    if level:
        result["level"] = level

    formats = parse_formats(raw)
    if formats:
        result["formats"] = formats

    missing = []
    if "slides" not in result:
        missing.append("slides")
    if "providers" not in result:
        missing.append("providers")
    if "level" not in result:
        missing.append("level")
    if "formats" not in result:
        missing.append("formats")
    result["needs_clarification"] = missing

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
