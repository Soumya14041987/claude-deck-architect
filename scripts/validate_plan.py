#!/usr/bin/env python3
"""
validate_plan.py — Standalone validation script for Deck Architect content plans.

Users can run this to validate their content-plan JSON before submitting to build_deck.py.

Usage:
    python3 scripts/validate_plan.py --plan my-deck-plan.json
    python3 scripts/validate_plan.py --plan plan.json --verbose
"""

import argparse
import json
import sys
from pathlib import Path

try:
    import jsonschema
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
SCHEMA_PATH = REPO_ROOT / "references" / "content-plan-schema.json"

# ANSI colors for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"


def print_success(msg):
    print(f"{GREEN}✓{RESET} {msg}")


def print_error(msg):
    print(f"{RED}✗{RESET} {msg}")


def print_warning(msg):
    print(f"{YELLOW}⚠{RESET}  {msg}")


def print_info(msg):
    print(f"{BLUE}ℹ{RESET}  {msg}")


def print_header(msg):
    print(f"\n{BOLD}{msg}{RESET}")


def validate_file_exists(plan_path):
    """Check that the plan file exists and is readable."""
    if not plan_path.exists():
        print_error(f"Plan file not found: {plan_path}")
        return False
    return True


def validate_json_parseable(plan_path):
    """Check that the file is valid JSON."""
    try:
        with open(plan_path, "r", encoding="utf-8") as f:
            json.load(f)
        print_success("JSON is valid")
        return True
    except json.JSONDecodeError as e:
        print_error(f"Invalid JSON: {e}")
        return False


def validate_required_fields(plan):
    """Check for required top-level fields."""
    required = ["title", "theme", "slides"]
    missing = [f for f in required if f not in plan or not plan[f]]
    
    if missing:
        print_error(f"Missing required fields: {', '.join(missing)}")
        return False
    
    print_success("Required fields present: title, theme, slides")
    return True


def validate_theme(plan):
    """Check that the theme is valid."""
    valid_themes = ["aws-orange", "gcp-multi", "azure-electric", "cncf-teal", "cyber-neon", "multi-cloud", "light-editorial"]
    theme = plan.get("theme")
    
    if theme not in valid_themes:
        print_error(f"Invalid theme: '{theme}'. Must be one of: {', '.join(valid_themes)}")
        return False
    
    print_success(f"Theme is valid: {theme}")
    return True


def validate_slides(plan):
    """Check that slides array is valid."""
    slides = plan.get("slides", [])
    
    if not isinstance(slides, list):
        print_error("'slides' must be an array")
        return False
    
    if len(slides) == 0:
        print_error("'slides' array is empty (minimum 1 slide required)")
        return False
    
    print_success(f"Slide count: {len(slides)}")
    
    valid_archetypes = [
        "Title", "Agenda", "ProblemFriction", "KeyConcept", "Topology",
        "DeepDive", "CodeSpec", "Comparison", "Timeline", "BenchmarkMatrix",
        "ProductionGotchas", "Demo", "Quote", "Resources", "Speaker", "CallToAction"
    ]
    
    errors = []
    for i, slide in enumerate(slides, 1):
        if not isinstance(slide, dict):
            errors.append(f"  Slide {i}: is not an object")
            continue
        
        if "archetype" not in slide:
            errors.append(f"  Slide {i}: missing 'archetype' field")
            continue
        
        if slide["archetype"] not in valid_archetypes:
            errors.append(f"  Slide {i}: invalid archetype '{slide['archetype']}'")
        
        if "title" not in slide or not slide["title"]:
            errors.append(f"  Slide {i}: missing or empty 'title' field")
    
    if errors:
        print_error(f"Slide validation failed:")
        for error in errors:
            print(f"    {error}")
        return False
    
    print_success("All slides have valid archetype and title")
    return True


def validate_with_schema(plan):
    """Validate against JSON Schema."""
    if not HAS_JSONSCHEMA:
        print_warning("jsonschema not installed — skipping full schema validation")
        print_info("Install with: pip install jsonschema")
        return True
    
    if not SCHEMA_PATH.exists():
        print_warning(f"Schema file not found: {SCHEMA_PATH}")
        return True
    
    try:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            schema = json.load(f)
    except json.JSONDecodeError as e:
        print_error(f"Schema file is invalid JSON: {e}")
        return False
    
    try:
        jsonschema.validate(instance=plan, schema=schema)
        print_success("Full JSON Schema validation passed")
        return True
    except jsonschema.ValidationError as e:
        print_error(f"Schema validation failed: {e.message}")
        if e.path:
            path_str = ".".join(str(p) for p in e.path)
            print(f"    At: {path_str}")
        return False
    except jsonschema.SchemaError as e:
        print_error(f"Schema file is invalid: {e}")
        return False


def main():
    ap = argparse.ArgumentParser(
        description="Validate a Deck Architect content plan before building"
    )
    ap.add_argument("--plan", required=True, help="Path to content-plan JSON file")
    ap.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = ap.parse_args()
    
    plan_path = Path(args.plan)
    
    print_header("Deck Architect Content Plan Validator")
    print(f"Plan: {plan_path}\n")
    
    checks_passed = 0
    checks_total = 0
    
    # Check 1: File exists
    print_header("1. File Check")
    checks_total += 1
    if validate_file_exists(plan_path):
        checks_passed += 1
    else:
        print("Cannot proceed without valid file")
        sys.exit(1)
    
    # Check 2: Valid JSON
    print_header("2. JSON Syntax")
    checks_total += 1
    if validate_json_parseable(plan_path):
        checks_passed += 1
    else:
        print("Cannot proceed without valid JSON")
        sys.exit(1)
    
    # Load plan for remaining checks
    with open(plan_path, "r", encoding="utf-8") as f:
        plan = json.load(f)
    
    # Check 3: Required fields
    print_header("3. Required Fields")
    checks_total += 1
    if validate_required_fields(plan):
        checks_passed += 1
    
    # Check 4: Theme validation
    print_header("4. Theme Validation")
    checks_total += 1
    if validate_theme(plan):
        checks_passed += 1
    
    # Check 5: Slides validation
    print_header("5. Slides Validation")
    checks_total += 1
    if validate_slides(plan):
        checks_passed += 1
    
    # Check 6: Full schema validation
    print_header("6. Full Schema Validation")
    checks_total += 1
    if validate_with_schema(plan):
        checks_passed += 1
    
    # Summary
    print_header("Validation Summary")
    if checks_passed == checks_total:
        print(f"{GREEN}{BOLD}✓ All checks passed ({checks_passed}/{checks_total}){RESET}")
        print("\nYour content plan is ready to build!")
        print(f"Next step: python3 scripts/build_deck.py --plan {plan_path} --out output.pptx")
        sys.exit(0)
    else:
        print(f"{RED}{BOLD}✗ Validation failed ({checks_passed}/{checks_total}){RESET}")
        print("\nFix the errors above and try again.")
        sys.exit(1)


if __name__ == "__main__":
    main()
