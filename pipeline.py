#!/usr/bin/env python3
"""
pipeline.py
--------------
Standalone command-line entry point for the validation pipeline
(fixes: "create a pipeline"). The multi-agent pipeline itself has
always lived in app/orchestrator.py:run_pipeline(), coordinated by
the Orchestrator Agent - but the ONLY way to run it was through the
Streamlit UI. This script exposes that same pipeline as a plain,
scriptable CLI, decoupled from Streamlit, so it can be run directly,
scheduled (cron / CI), or piped into other tools:

    python pipeline.py "A marketplace app for renting power tools" \\
        --location "Hyderabad, India" \\
        --budget "Bootstrap (very small budget)" \\
        --timeline "3 Months" \\
        --pdf-out validation_report.pdf

It performs the same three things the Streamlit "Validate Idea"
button does, in the same order:
1. Deterministic input validation (tools/input_validator.py)
2. Run the full agent pipeline (app/orchestrator.run_pipeline)
3. Persist the result to Postgres (db/database.py) and write a PDF

Every step degrades gracefully: a missing/unreachable database never
stops the PDF or the printed summary from being produced.
"""

import argparse
import json
import sys

from app.orchestrator import run_pipeline
from tools.input_validator import validate_idea_text, check_sensitive_content, check_plausibility
from tools.pdf_generator import build_report_pdf
from db import database


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run the AI Startup Idea Validator pipeline from the command line."
    )
    parser.add_argument("idea", help="The startup idea description (2-3 sentences).")
    parser.add_argument("--location", default="", help="Target market, e.g. 'Hyderabad, India'.")
    parser.add_argument("--budget", default="Not sure yet", help="Expected budget bracket.")
    parser.add_argument("--timeline", default="3 Months", help="Launch timeline.")
    parser.add_argument("--pdf-out", default="validation_report.pdf", help="Where to write the PDF report.")
    parser.add_argument("--json-out", default=None, help="Optional: also dump the full raw result as JSON here.")
    parser.add_argument("--no-db", action="store_true", help="Skip saving this run to Postgres.")
    return parser.parse_args()


def main():
    args = parse_args()

    input_check = validate_idea_text(args.idea)
    if not input_check["is_valid"]:
        print(f"Invalid input: {input_check['reason']}", file=sys.stderr)
        sys.exit(1)
    sensitive_check = check_sensitive_content(args.idea)
    if sensitive_check.get("is_sensitive"):
        print(f"Rejected: {sensitive_check['reason']}", file=sys.stderr)
        sys.exit(1)
    plausibility_check = check_plausibility(args.idea)
    if not plausibility_check.get("is_plausible", True):
        print(f"Rejected: {plausibility_check['reason']}", file=sys.stderr)
        sys.exit(1)

    print("Running multi-agent validation pipeline...")
    result = run_pipeline(args.idea, args.location)

    if not args.no_db:
        if database.init_db():
            new_id = database.save_validation(
                result, {"budget": args.budget, "timeline": args.timeline}
            )
            if new_id:
                print(f"Saved to database (id={new_id}).")
        else:
            print("Database not reachable - skipping persistence.", file=sys.stderr)

    pdf_bytes = build_report_pdf(result)
    with open(args.pdf_out, "wb") as f:
        f.write(pdf_bytes)
    print(f"PDF report written to {args.pdf_out}")

    if args.json_out:
        with open(args.json_out, "w") as f:
            json.dump(result, f, indent=2, default=str)
        print(f"Raw result JSON written to {args.json_out}")

    viability = result.get("viability_score", {})
    print("\n--- Summary ---")
    print(f"Idea: {result.get('extracted', {}).get('idea_name', '')}")
    print(f"Viability Score: {viability.get('overall_score', 'N/A')}/100 - {viability.get('verdict', '')}")
    print(result.get("quick_summary", ""))


if __name__ == "__main__":
    main()
