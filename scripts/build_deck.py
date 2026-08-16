#!/usr/bin/env python3
"""
build_deck.py — Deck Architect's main build orchestrator.

Takes a content-plan JSON (see references/content-plan-schema.json), renders any
Mermaid diagrams referenced in Topology slides to themed PNGs, calls the
pptxgenjs engine (deck_engine.js) to produce the .pptx, optionally converts to
PDF via LibreOffice, and runs a light validation pass.

Usage:
    python3 build_deck.py --plan plan.json --out /mnt/user-data/outputs/deck.pptx [--pdf] [--verbose]
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    import jsonschema
except ImportError:
    jsonschema = None

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
THEMES_PATH = REPO_ROOT / "data" / "themes.json"
SCHEMA_PATH = REPO_ROOT / "references" / "content-plan-schema.json"
RENDER_MERMAID = SCRIPT_DIR / "render_mermaid.py"
DECK_ENGINE = SCRIPT_DIR / "deck_engine.js"

VERBOSE = False

def log(msg, level="INFO"):
    """Log message to stderr with level prefix."""
    timestamp = ""
    prefix = f"[{level}]"
    print(f"{prefix} {msg}", file=sys.stderr)


def log_verbose(msg):
    """Log only if --verbose is set."""
    if VERBOSE:
        log(msg, "VERBOSE")


def validate_plan(plan):
    """Validate content plan against JSON schema. Raises SystemExit with detailed errors."""
    if not jsonschema:
        log("WARNING: jsonschema not installed, skipping validation (install with: pip install jsonschema)", "WARNING")
        return

    if not SCHEMA_PATH.exists():
        log(f"Schema file not found: {SCHEMA_PATH}", "WARNING")
        return

    try:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            schema = json.load(f)
    except json.JSONDecodeError as e:
        log(f"Failed to parse schema file: {e}", "ERROR")
        raise SystemExit(f"Schema file is invalid JSON: {e}")

    try:
        jsonschema.validate(instance=plan, schema=schema)
        log("Content plan validated successfully", "INFO")
    except jsonschema.ValidationError as e:
        log("Content plan validation FAILED", "ERROR")
        log(f"  Error: {e.message}", "ERROR")
        if e.path:
            log(f"  At path: {'.'.join(str(p) for p in e.path)}", "ERROR")
        if e.validator_value:
            log(f"  Expected: {e.validator_value}", "ERROR")
        log(f"  Check slide content against references/content-plan-schema.json", "ERROR")
        raise SystemExit(f"Validation failed: {e.message}")
    except jsonschema.SchemaError as e:
        log(f"Schema file is invalid: {e}", "ERROR")
        raise SystemExit(f"Schema validation error: {e}")


def check_required_fields(plan):
    """Check that all required fields are present in the plan."""
    errors = []
    
    if not plan.get("title"):
        errors.append("Missing required field: 'title'")
    
    if not plan.get("theme"):
        errors.append("Missing required field: 'theme'")
    elif plan["theme"] not in ["aws-orange", "gcp-multi", "azure-electric", "cncf-teal", "cyber-neon", "multi-cloud", "light-editorial"]:
        errors.append(f"Invalid theme: '{plan['theme']}' (must be one of: aws-orange, gcp-multi, azure-electric, cncf-teal, cyber-neon, multi-cloud, light-editorial)")
    
    if not plan.get("slides") or not isinstance(plan["slides"], list):
        errors.append("Missing or invalid required field: 'slides' (must be a non-empty array)")
    elif len(plan["slides"]) == 0:
        errors.append("Content plan has no slides")
    else:
        for i, slide in enumerate(plan["slides"], 1):
            if not slide.get("archetype"):
                errors.append(f"Slide {i}: Missing required field 'archetype'")
            if not slide.get("title"):
                errors.append(f"Slide {i}: Missing required field 'title'")
    
    if errors:
        for error in errors:
            log(error, "ERROR")
        raise SystemExit("Content plan has missing required fields")


def render_diagrams(plan, work_dir: Path, theme_key: str):
    """Render any Mermaid source in Topology slides to PNGs, in place."""
    diagram_slides = [slide for slide in plan.get("slides", []) if slide.get("archetype") == "Topology"]
    
    if not diagram_slides:
        log_verbose("No Topology slides found, skipping diagram rendering")
        return plan
    
    log(f"Rendering {len(diagram_slides)} diagram(s)...")
    
    for i, slide in enumerate(plan.get("slides", [])):
        if slide.get("archetype") != "Topology":
            continue
        mermaid_src = slide.get("mermaid")
        if not mermaid_src:
            log(f"  Slide {i+1}: No mermaid source found (diagram_image placeholder will show)", "WARNING")
            continue
        
        out_png = work_dir / f"diagram_{i:02d}.png"
        try:
            log(f"  Rendering diagram for slide {i+1}/{len(diagram_slides)}...", "VERBOSE")
            result = subprocess.run(
                [
                    sys.executable,
                    str(RENDER_MERMAID),
                    "--theme", theme_key,
                    "--out", str(out_png),
                ],
                input=mermaid_src,
                text=True,
                timeout=30,
                capture_output=True,
            )
            if result.returncode != 0:
                log(f"  Slide {i+1}: Diagram render failed — {result.stderr}", "WARNING")
                continue
            slide["diagram_image"] = str(out_png)
            log(f"  Slide {i+1}: ✓ Rendered to {out_png.name}", "VERBOSE")
        except subprocess.TimeoutExpired:
            log(f"  Slide {i+1}: Diagram render timed out (>30s) — check mermaid source", "WARNING")
        except subprocess.CalledProcessError as e:
            log(f"  Slide {i+1}: Diagram render failed: {e.stderr}", "WARNING")
        except Exception as e:
            log(f"  Slide {i+1}: Unexpected error rendering diagram: {e}", "ERROR")
    
    log("Diagram rendering complete")
    return plan


def build_pptx(plan_path: Path, out_path: Path):
    """Build PPTX from plan using deck_engine.js. Raises SystemExit on failure."""
    log("Building PPTX...")
    result = subprocess.run(
        ["node", str(DECK_ENGINE), str(plan_path), str(out_path), str(THEMES_PATH)],
        timeout=60,
        capture_output=True,
        text=True,
    )
    
    if result.stdout:
        log_verbose(result.stdout)
    
    if result.returncode != 0:
        log("PPTX build FAILED", "ERROR")
        if result.stderr:
            log(f"  Error output:\n{result.stderr}", "ERROR")
        raise SystemExit("deck_engine.js failed — see error output above")
    
    if not out_path.exists():
        log("PPTX file was not created", "ERROR")
        raise SystemExit("Output PPTX file does not exist")
    
    size_mb = out_path.stat().st_size / (1024 * 1024)
    log(f"✓ PPTX built successfully ({size_mb:.1f} MB)")


def convert_to_pdf(pptx_path: Path, out_dir: Path):
    """Convert PPTX to PDF via LibreOffice. Returns PDF path or None if conversion fails."""
    log("Converting to PDF...")
    
    # Check if LibreOffice is available
    import shutil
    soffice_bin = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice_bin:
        log("LibreOffice not found on system — PDF conversion skipped", "WARNING")
        log("  Install with: brew install libreoffice (macOS) or apt install libreoffice (Linux)", "INFO")
        return None
    
    soffice_wrapper = REPO_ROOT.parent / "pptx" / "scripts" / "office" / "soffice.py"
    # Prefer the Anthropic-provided pptx skill's soffice wrapper if present (handles sandboxing);
    # otherwise fall back to calling soffice directly.
    candidates = [
        Path("/mnt/skills/public/pptx/scripts/office/soffice.py"),
        soffice_wrapper,
    ]
    wrapper = next((c for c in candidates if c.exists()), None)
    if wrapper:
        cmd = [sys.executable, str(wrapper), "--headless", "--convert-to", "pdf",
               "--outdir", str(out_dir), str(pptx_path)]
    else:
        cmd = [soffice_bin, "--headless", "--convert-to", "pdf", "--outdir", str(out_dir), str(pptx_path)]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        log_verbose(result.stdout)
        
        if result.returncode != 0:
            log(f"PDF conversion failed: {result.stderr}", "WARNING")
            return None
        
        pdf_path = out_dir / (pptx_path.stem + ".pdf")
        if pdf_path.exists():
            size_mb = pdf_path.stat().st_size / (1024 * 1024)
            log(f"✓ PDF created successfully ({size_mb:.1f} MB)")
            return pdf_path
        else:
            log("PDF file was not created", "WARNING")
            return None
    except subprocess.TimeoutExpired:
        log("PDF conversion timed out (>120s)", "WARNING")
        return None
    except Exception as e:
        log(f"PDF conversion error: {e}", "WARNING")
        return None


def log_history(plan, out_path: Path):
    """Log generated deck to history.jsonl for future reference."""
    history_path = REPO_ROOT / "data" / "history.jsonl"
    entry = {
        "title": plan.get("title"),
        "theme": plan.get("theme"),
        "level": plan.get("level"),
        "slide_count": len(plan.get("slides", [])),
        "output": str(out_path),
    }
    try:
        with open(history_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
        log_verbose(f"Logged to history: {history_path}")
    except OSError as e:
        log(f"Could not write history log: {e}", "WARNING")


def main():
    global VERBOSE
    
    ap = argparse.ArgumentParser(
        description="Build a Deck Architect PPTX from a content plan JSON"
    )
    ap.add_argument("--plan", required=True, help="Path to content-plan JSON")
    ap.add_argument("--out", required=True, help="Output .pptx path")
    ap.add_argument("--pdf", action="store_true", help="Also export a PDF")
    ap.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    args = ap.parse_args()
    
    VERBOSE = args.verbose

    plan_path = Path(args.plan)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    log(f"build_deck starting — plan: {plan_path}, output: {out_path}")

    # Load and validate plan
    try:
        with open(plan_path, "r", encoding="utf-8") as f:
            plan = json.load(f)
    except json.JSONDecodeError as e:
        log(f"Failed to parse JSON: {e}", "ERROR")
        raise SystemExit(f"Invalid JSON in {plan_path}: {e}")
    except FileNotFoundError:
        log(f"Plan file not found: {plan_path}", "ERROR")
        raise SystemExit(f"Plan file not found: {plan_path}")
    
    # Run validation
    check_required_fields(plan)
    validate_plan(plan)

    # Build deck
    try:
        with tempfile.TemporaryDirectory(prefix="deck-architect-") as tmp:
            work_dir = Path(tmp)
            plan = render_diagrams(plan, work_dir, plan.get("theme", "cyber-neon"))

            resolved_plan_path = work_dir / "plan.resolved.json"
            with open(resolved_plan_path, "w", encoding="utf-8") as f:
                json.dump(plan, f)

            build_pptx(resolved_plan_path, out_path)

        log(f"✓ Deck built: {out_path}")

        if args.pdf:
            pdf_path = convert_to_pdf(out_path, out_path.parent)
            if pdf_path:
                log(f"✓ PDF created: {pdf_path}")
            else:
                log("PDF conversion was not successful, but PPTX is ready", "WARNING")

        log_history(plan, out_path)
        log("Build complete!")

    except SystemExit:
        raise
    except Exception as e:
        log(f"Unexpected error during build: {e}", "ERROR")
        raise SystemExit(f"Build failed: {e}")


if __name__ == "__main__":
    main()
