"""CLI: python -m pacu.component2 --input path.json [--out plan.json] [--pretty]"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import config
from .engine import generate_plan
from .serialize import inputs_from_dict, plan_to_json, pretty_table


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m pacu.component2",
                                 description="PACU Component 2: rule-based training plan engine.")
    ap.add_argument("--input", required=True, help="PlanInputs JSON file")
    ap.add_argument("--out", help="write the plan JSON here")
    ap.add_argument("--pretty", action="store_true", help="print a week-by-week text table")
    ap.add_argument("--load-method", choices=config.LOAD_METHODS, help="override LOAD_METHOD (S6, A-17)")
    args = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # titles use the multiplication sign

    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    data = data.get("inputs", data)  # accept a bare PlanInputs object or {"inputs": {...}}
    cfg = config.with_overrides(LOAD_METHOD=args.load_method) if args.load_method else config
    plan = generate_plan(inputs_from_dict(data), cfg)
    text = plan_to_json(plan)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    if args.pretty:
        print(pretty_table(plan))
    elif not args.out:
        sys.stdout.write(text + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
