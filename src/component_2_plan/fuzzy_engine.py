# Mamdani-style fuzzy inference for training capacity.
# Inputs : weekly_mileage_km (0-100), recovery_score (0-100, derived from RPE).
# Output : capacity score (0-100) — drives peak volume and progression rate.
# MFs, rule base, and conflict-resolution ordering are Naji's own design.

import numpy as np

_UNIVERSE = np.linspace(0, 100, 300)


# --- Membership functions ---

def _trimf(x: float, a: float, b: float, c: float) -> float:
    left  = 1.0 if a == b else (x - a) / (b - a)
    right = 1.0 if b == c else (c - x) / (c - b)
    return float(np.clip(min(left, right), 0.0, 1.0))


def _trapf(x: float, a: float, b: float, c: float, d: float) -> float:
    left  = 1.0 if a == b else (x - a) / (b - a)
    right = 1.0 if c == d else (d - x) / (d - c)
    return float(np.clip(min(left, 1.0, right), 0.0, 1.0))


def _mileage_mf(km: float) -> dict:
    return {
        'low':    _trapf(km,  0,  0, 20, 40),
        'medium': _trimf(km, 20, 45, 70),
        'high':   _trapf(km, 60, 80, 100, 100),
    }


def _recovery_mf(score: float) -> dict:
    return {
        'low':    _trapf(score,  0,  0, 30, 50),
        'medium': _trimf(score, 30, 50, 70),
        'high':   _trapf(score, 50, 70, 100, 100),
    }


def _cap_low(x: float)    -> float: return _trapf(x,  0,  0, 25, 45)
def _cap_medium(x: float) -> float: return _trimf(x, 25, 50, 75)
def _cap_high(x: float)   -> float: return _trapf(x, 55, 75, 100, 100)


_CAP_FNS = {'low': _cap_low, 'medium': _cap_medium, 'high': _cap_high}


# --- Inference ---

_RULES = [
    # (mileage_label, recovery_label, output_label)
    ('low',    'low',    'low'),
    ('low',    'medium', 'low'),
    ('low',    'high',   'medium'),
    ('medium', 'low',    'low'),
    ('medium', 'medium', 'medium'),
    ('medium', 'high',   'high'),
    ('high',   'low',    'medium'),
    ('high',   'medium', 'high'),
    ('high',   'high',   'high'),
]


def compute_capacity(weekly_mileage_km: float, recovery_score: float) -> float:
    """
    Returns a capacity score in [0, 100].
    recovery_score should be derived from the runner's self-reported RPE:
        recovery_score = (10 - borg_cr10_rpe) * 10
    """
    m = _mileage_mf(weekly_mileage_km)
    r = _recovery_mf(recovery_score)

    aggregated = np.zeros(len(_UNIVERSE))
    for mil_label, rec_label, out_label in _RULES:
        strength = min(m[mil_label], r[rec_label])
        if strength <= 0:
            continue
        mf_vals = np.array([_CAP_FNS[out_label](x) for x in _UNIVERSE])
        aggregated = np.maximum(aggregated, np.minimum(mf_vals, strength))

    total = aggregated.sum()
    if total == 0:
        return 50.0
    return float(np.dot(_UNIVERSE, aggregated) / total)


def rpe_to_recovery_score(borg_cr10: float) -> float:
    """Convert Borg CR10 RPE (0-10) to a 0-100 recovery score (inverse)."""
    return float(np.clip((10.0 - borg_cr10) * 10.0, 0.0, 100.0))
