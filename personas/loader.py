"""Persona fixtures (brief section 10).

Each persona gives only a predicted 5K time; the other three predicted times are
filled with Riegel's formula, T2 = T1 x (D2 / D1)^1.06. This stands in for
Component 1's output and lives here, not in Component 2, which never computes
predictions itself.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from components.component2 import config
from components.component2.models import PlanInputs
from components.component2.serialize import inputs_from_dict, parse_duration

PERSONA_DIR = Path(__file__).resolve().parent
RIEGEL_EXPONENT = 1.06


def riegel_fill(t5k_s: float) -> dict[str, float]:
    """All four predicted times from a 5K time (Riegel, exponent 1.06)."""
    return {d: t5k_s * (config.DISTANCE_KM[d] / config.DISTANCE_KM["5K"]) ** RIEGEL_EXPONENT
            for d in config.DISTANCES}


def persona_paths() -> list[Path]:
    return sorted(PERSONA_DIR.glob("P*.json"))


def load_persona(path: Path) -> tuple[dict[str, Any], PlanInputs]:
    """Return (persona metadata incl. 'expect', PlanInputs)."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    raw = dict(data["inputs"])
    raw["predicted_times_s"] = riegel_fill(parse_duration(raw.pop("predicted_5k")))
    return data, inputs_from_dict(raw)


def all_personas() -> list[tuple[dict[str, Any], PlanInputs]]:
    return [load_persona(p) for p in persona_paths()]
