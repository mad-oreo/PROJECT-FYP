# Cross-distance conversion with Riegel's formula: T2 = T1 * (D2 / D1) ^ 1.06
# Used to convert a predicted marathon time into 5K / 10K / 21K / 42K times.

DISTANCES_KM = {"5K": 5.0, "10K": 10.0, "21K": 21.0975, "42K": 42.195}


def riegel(t1_min, d1_km, d2_km, exponent=1.06):
    return t1_min * (d2_km / d1_km) ** exponent


def all_distances(marathon_min):
    return {k: riegel(marathon_min, 42.195, d) for k, d in DISTANCES_KM.items()}
