#!/usr/bin/env python3
"""
render_mermaid.py — renders Mermaid diagram source (from stdin) to a themed,
transparent-background PNG using the Mermaid CLI (mmdc), or falls back to a
simplified box-and-arrow SVG built with plain drawing primitives if mmdc is
unavailable.

Usage:
    echo "flowchart LR; A-->B" | python3 render_mermaid.py --theme aws-orange --out diagram.png
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
THEMES_PATH = REPO_ROOT / "data" / "themes.json"


def load_theme(theme_key: str):
    with open(THEMES_PATH, "r", encoding="utf-8") as f:
        themes = json.load(f)
    return themes.get(theme_key, themes.get("cyber-neon"))


def mermaid_config(theme):
    """Build a Mermaid CLI theme config matching the deck's active palette."""
    return {
        "theme": "base",
        "themeVariables": {
            "primaryColor": f"#{theme['card_dark']}",
            "primaryTextColor": f"#{theme.get('text', 'E6E6E6')}",
            "primaryBorderColor": f"#{theme['accent_primary']}",
            "lineColor": f"#{theme['accent_primary']}",
            "secondaryColor": f"#{theme['accent_secondary']}",
            "tertiaryColor": f"#{theme['bg_dark']}",
            "fontFamily": theme.get("font", "Arial"),
            "background": "transparent",
        },
    }


def render_with_mmdc(mermaid_src: str, theme, out_path: Path) -> bool:
    mmdc = shutil.which("mmdc")
    if not mmdc:
        return False
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        mmd_file = tmp / "diagram.mmd"
        cfg_file = tmp / "config.json"
        puppeteer_cfg = tmp / "puppeteer.json"

        mmd_file.write_text(mermaid_src, encoding="utf-8")
        cfg_file.write_text(json.dumps(mermaid_config(theme)), encoding="utf-8")
        # Sandboxed environments typically need --no-sandbox for headless Chromium.
        puppeteer_cfg.write_text(json.dumps({"args": ["--no-sandbox"]}), encoding="utf-8")

        cmd = [
            mmdc,
            "-i", str(mmd_file),
            "-o", str(out_path),
            "-c", str(cfg_file),
            "-p", str(puppeteer_cfg),
            "-b", "transparent",
            "-s", "2",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(result.stderr, file=sys.stderr)
            return False
        return out_path.exists()


def parse_simple_nodes(mermaid_src: str):
    """Very small parser: pulls 'A[Label] --> B[Label]' style edges out of a
    flowchart for the fallback SVG renderer. Not a full Mermaid parser —
    only used when mmdc is unavailable."""
    import re

    edges = []
    node_labels = {}
    edge_pattern = re.compile(r"(\w+)(\[[^\]]+\])?\s*-->\s*(\w+)(\[[^\]]+\])?")
    for line in mermaid_src.splitlines():
        m = edge_pattern.search(line)
        if not m:
            continue
        a_id, a_label, b_id, b_label = m.groups()
        if a_label:
            node_labels[a_id] = a_label.strip("[]")
        if b_label:
            node_labels[b_id] = b_label.strip("[]")
        edges.append((a_id, b_id))
    nodes = list(dict.fromkeys([n for edge in edges for n in edge]))
    return nodes, edges, node_labels


def _wrap_text(draw, text, font, max_width):
    """Greedy word-wrap text to fit max_width, returns list of lines."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        bbox = draw.textbbox((0, 0), trial, font=font)
        if bbox[2] - bbox[0] <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def render_fallback_svg(mermaid_src: str, theme, out_path: Path):
    """Draw a simplified left-to-right box-and-arrow diagram as a PNG using
    Pillow primitives (Pillow has no native SVG support, so this draws
    directly rather than emitting SVG). Wraps long labels and scales box
    width/height to the longest label so 4-6 node diagrams stay legible."""
    from PIL import Image, ImageDraw, ImageFont

    nodes, edges, labels = parse_simple_nodes(mermaid_src)
    if not nodes:
        nodes, edges, labels = ["A", "B"], [("A", "B")], {"A": "Start", "B": "End"}

    n = max(len(nodes), 1)
    # Scale canvas and box size down as node count grows so text still wraps
    # to a readable width instead of a single overflowing line.
    box_w = max(200, min(340, int(2200 / n)))
    box_h = 130
    W = n * box_w + (n + 1) * 60
    H = 420
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    accent = tuple(int(theme["accent_primary"][i:i + 2], 16) for i in (0, 2, 4)) + (255,)
    card = tuple(int(theme["card_dark"][i:i + 2], 16) for i in (0, 2, 4)) + (255,)
    text_color = (230, 230, 230, 255)

    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    try:
        font = ImageFont.truetype(font_path, 20)
    except OSError:
        font = ImageFont.load_default()

    gap = (W - n * box_w) / (n + 1)
    centers = []
    y = H / 2 - box_h / 2
    pad = 16

    for i, node_id in enumerate(nodes):
        x = gap + i * (box_w + gap)
        draw.rounded_rectangle([x, y, x + box_w, y + box_h], radius=14, fill=card, outline=accent, width=3)
        label = labels.get(node_id, node_id)
        lines = _wrap_text(draw, label, font, box_w - 2 * pad)
        # Shrink font if too many wrapped lines would overflow the box
        line_h = 26
        while len(lines) * line_h > box_h - 2 * pad and font.size > 12:
            font = ImageFont.truetype(font_path, font.size - 2) if os.path.exists(font_path) else font
            lines = _wrap_text(draw, label, font, box_w - 2 * pad)
        total_h = len(lines) * line_h
        start_y = y + box_h / 2 - total_h / 2
        for li, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            tw = bbox[2] - bbox[0]
            draw.text((x + box_w / 2 - tw / 2, start_y + li * line_h), line, fill=text_color, font=font)
        centers.append((x + box_w, y + box_h / 2, x, y + box_h / 2))

    id_to_idx = {node_id: i for i, node_id in enumerate(nodes)}
    for a, b in edges:
        if a not in id_to_idx or b not in id_to_idx:
            continue
        ax_right, ay, _, _ = centers[id_to_idx[a]]
        _, _, bx_left, by = centers[id_to_idx[b]]
        draw.line([ax_right, ay, bx_left, by], fill=accent, width=4)
        # simple arrowhead
        draw.polygon(
            [(bx_left, by), (bx_left - 14, by - 8), (bx_left - 14, by + 8)],
            fill=accent,
        )

    img.save(out_path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--theme", default="cyber-neon")
    ap.add_argument("--out", required=True)
    ap.add_argument("--fallback-svg", action="store_true", help="Force the fallback renderer")
    args = ap.parse_args()

    mermaid_src = sys.stdin.read()
    if not mermaid_src.strip():
        print("No Mermaid source provided on stdin", file=sys.stderr)
        sys.exit(1)

    theme = load_theme(args.theme)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if not args.fallback_svg and render_with_mmdc(mermaid_src, theme, out_path):
        print(f"Rendered via mmdc -> {out_path}")
        return

    print("mmdc unavailable or failed — using fallback box-and-arrow renderer", file=sys.stderr)
    render_fallback_svg(mermaid_src, theme, out_path)
    print(f"Rendered via fallback -> {out_path}")


if __name__ == "__main__":
    main()
