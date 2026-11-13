"""JSON output, determinism and the CLI."""
import json
import subprocess
import sys
from pathlib import Path

from pacu.component2 import generate_plan
from pacu.component2.serialize import inputs_from_dict, inputs_to_dict, plan_to_json, pretty_table

from helpers import make_inputs

ROOT = Path(__file__).resolve().parents[1]


def test_json_format():
    d = json.loads(plan_to_json(generate_plan(make_inputs(max_hr=190))))
    w = d["weeks"][0]
    assert w["start_date"] == "2026-12-07"
    seg = w["sessions"][0]["segments"][0]
    assert seg["pace"].endswith("/km") and ":" in seg["pace"]
    assert all(round(s["km"], 1) == s["km"] for s in w["sessions"])
    assert isinstance(w["sessions"][0]["minutes"], int)
    assert w["sessions"][0]["hr_range"] is not None
    assert d["race"]["date"] == "2027-03-28" and d["config"]["LOAD_METHOD"] == "session"


def test_deterministic():
    assert plan_to_json(generate_plan(make_inputs())) == plan_to_json(generate_plan(make_inputs()))


def test_inputs_round_trip():
    inp = make_inputs()
    again = inputs_from_dict(inputs_to_dict(inp))
    assert again.race_date == inp.race_date and again.recovery_answers == inp.recovery_answers
    assert inputs_from_dict({**inputs_to_dict(inp), "easy_pace_s_per_km": "6:40"}).easy_pace_s_per_km == 400


def test_pretty_table_lists_weeks():
    text = pretty_table(generate_plan(make_inputs()))
    assert "ACWR" in text and "RACE" in text and "\n16 " in text


def test_cli(tmp_path):
    inp = tmp_path / "in.json"
    inp.write_text(json.dumps(inputs_to_dict(make_inputs())), encoding="utf-8")
    out = tmp_path / "plan.json"
    r = subprocess.run([sys.executable, "-m", "pacu.component2", "--input", str(inp), "--out", str(out),
                        "--pretty"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0, r.stderr
    assert json.loads(out.read_text(encoding="utf-8"))["status"] == "OK"
    assert "Week" in r.stdout
