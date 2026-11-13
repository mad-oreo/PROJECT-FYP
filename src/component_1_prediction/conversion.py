# Cross-distance conversion using the Riegel power-law formula as a proxy for the
# Dash (2024) generalised approach. Replace _EXPONENT and formula below once
# Win_Your_Race_Goal_...md is verified against the actual paper.
#
# Formula: T2 = T1 * (D2 / D1) ^ k   where k = 1.06 (Riegel exponent)

_BASE_KM  = 42.195   # marathon
_EXPONENT = 1.06

DISTANCES_KM = {
    '5K':       5.0,
    '10K':      10.0,
    'Half':     21.0975,
    'Marathon': 42.195,
}


def convert_time(marathon_time_min: float, target_km: float) -> float:
    return marathon_time_min * (target_km / _BASE_KM) ** _EXPONENT


def convert_all_distances(marathon_time_min: float) -> dict:
    return {label: convert_time(marathon_time_min, km) for label, km in DISTANCES_KM.items()}
