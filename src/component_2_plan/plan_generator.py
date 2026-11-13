import copy

PLAN_WEEKS = {
    '5K':       6,
    '10K':      8,
    'Half':     12,
    'Marathon': 16,
}

PHASE_SCHEDULE = {
    '5K':       ['Base', 'Base', 'Build', 'Build', 'Peak', 'Taper'],
    '10K':      ['Base', 'Base', 'Base', 'Build', 'Build', 'Build', 'Peak', 'Taper'],
    'Half':     ['Base']*4 + ['Build']*4 + ['Peak']*2 + ['Taper']*2,
    'Marathon': ['Base']*5 + ['Build']*5 + ['Peak']*4 + ['Taper']*2,
}

PHASE_MULTIPLIER = {
    'Base':  1.00,
    'Build': 1.10,
    'Peak':  1.20,
    'Taper': 0.60,
}

# Capacity scale factors applied to all non-rest session durations.
# Rep structures and capacity tiers are Naji's own design.
_CAPACITY_SCALE = {'low': 0.80, 'medium': 1.00, 'high': 1.20}

# ---- Single-week session templates (used by generate_plan for non-Half plans) ----

_BASE_SESSIONS = {
    'low': [
        {'day': 'Monday',    'type': 'Rest',     'duration_min': 0,  'rpe': 0, 'zone': '-'},
        {'day': 'Tuesday',   'type': 'Easy Run', 'duration_min': 35, 'rpe': 3, 'zone': '1-2'},
        {'day': 'Wednesday', 'type': 'Rest',     'duration_min': 0,  'rpe': 0, 'zone': '-'},
        {'day': 'Thursday',  'type': 'Easy Run', 'duration_min': 35, 'rpe': 3, 'zone': '1-2'},
        {'day': 'Friday',    'type': 'Rest',     'duration_min': 0,  'rpe': 0, 'zone': '-'},
        {'day': 'Saturday',  'type': 'Long Run', 'duration_min': 50, 'rpe': 4, 'zone': '2'},
        {'day': 'Sunday',    'type': 'Rest',     'duration_min': 0,  'rpe': 0, 'zone': '-'},
    ],
    'medium': [
        {'day': 'Monday',    'type': 'Rest',      'duration_min': 0,  'rpe': 0, 'zone': '-'},
        {'day': 'Tuesday',   'type': 'Easy Run',  'duration_min': 45, 'rpe': 3, 'zone': '1-2'},
        {'day': 'Wednesday', 'type': 'Tempo Run', 'duration_min': 35, 'rpe': 6, 'zone': '3-4'},
        {'day': 'Thursday',  'type': 'Rest',      'duration_min': 0,  'rpe': 0, 'zone': '-'},
        {'day': 'Friday',    'type': 'Easy Run',  'duration_min': 40, 'rpe': 3, 'zone': '2'},
        {'day': 'Saturday',  'type': 'Long Run',  'duration_min': 70, 'rpe': 4, 'zone': '2'},
        {'day': 'Sunday',    'type': 'Rest',      'duration_min': 0,  'rpe': 0, 'zone': '-'},
    ],
    'high': [
        {'day': 'Monday',    'type': 'Rest',      'duration_min': 0,  'rpe': 0, 'zone': '-'},
        {'day': 'Tuesday',   'type': 'Interval',  'duration_min': 50, 'rpe': 8, 'zone': '4-5'},
        {'day': 'Wednesday', 'type': 'Easy Run',  'duration_min': 50, 'rpe': 3, 'zone': '2'},
        {'day': 'Thursday',  'type': 'Tempo Run', 'duration_min': 45, 'rpe': 6, 'zone': '3-4'},
        {'day': 'Friday',    'type': 'Easy Run',  'duration_min': 45, 'rpe': 3, 'zone': '2'},
        {'day': 'Saturday',  'type': 'Long Run',  'duration_min': 90, 'rpe': 4, 'zone': '2'},
        {'day': 'Sunday',    'type': 'Rest',      'duration_min': 0,  'rpe': 0, 'zone': '-'},
    ],
}

# ---- 12-week Half Marathon plan — medium capacity baseline ----
# Each tuple: (day, session_type, duration_min, rpe, zone)
# LOW and HIGH capacity are derived by scaling duration_min (×0.80 / ×1.20).
# Week 4, 8 = deliberate recovery weeks (reduced volume) within Base and Build phases.
# Week 12 = race week; Saturday marked as RACE DAY with duration=0.

_R  = ('Rest',                0, 0, '-')
_HALF_PLAN_12W = [
    # ── WEEK 1  Base ────────────────────────────────────────────────────
    [_R,
     ('Easy Run',          40, 3, '1-2'),
     _R,
     ('Easy Run',          35, 3, '1-2'),
     _R,
     ('Long Run',          60, 4, '2'),
     _R],
    # ── WEEK 2  Base ────────────────────────────────────────────────────
    [_R,
     ('Easy Run',          45, 3, '1-2'),
     _R,
     ('Easy Run',          40, 3, '1-2'),
     _R,
     ('Long Run',          70, 4, '2'),
     _R],
    # ── WEEK 3  Base  (introduce tempo) ─────────────────────────────────
    [_R,
     ('Easy Run',          45, 3, '1-2'),
     ('Tempo Run',         30, 6, '3-4'),
     _R,
     ('Easy Run',          40, 3, '2'),
     ('Long Run',          75, 4, '2'),
     _R],
    # ── WEEK 4  Base  (recovery week) ───────────────────────────────────
    [_R,
     ('Easy Run',          35, 3, '1-2'),
     _R,
     ('Easy Run',          30, 3, '1-2'),
     _R,
     ('Long Run',          55, 4, '2'),
     _R],
    # ── WEEK 5  Build ───────────────────────────────────────────────────
    [_R,
     ('Easy Run',          45, 3, '1-2'),
     ('Tempo Run',         35, 6, '3-4'),
     _R,
     ('Easy Run',          40, 3, '2'),
     ('Long Run',          80, 4, '2'),
     _R],
    # ── WEEK 6  Build  (add intervals) ──────────────────────────────────
    [_R,
     ('Interval',          45, 8, '4-5'),
     ('Easy Run',          40, 3, '2'),
     ('Tempo Run',         35, 6, '3-4'),
     _R,
     ('Long Run',          85, 4, '2'),
     _R],
    # ── WEEK 7  Build  (peak build week) ────────────────────────────────
    [_R,
     ('Interval',          50, 8, '4-5'),
     ('Easy Run',          45, 3, '2'),
     ('Tempo Run',         40, 6, '3-4'),
     ('Easy Run',          35, 3, '2'),
     ('Long Run',          90, 4, '2'),
     _R],
    # ── WEEK 8  Build  (recovery week) ──────────────────────────────────
    [_R,
     ('Easy Run',          40, 3, '1-2'),
     ('Tempo Run',         30, 6, '3-4'),
     _R,
     ('Easy Run',          35, 3, '2'),
     ('Long Run',          65, 4, '2'),
     _R],
    # ── WEEK 9  Peak ────────────────────────────────────────────────────
    [_R,
     ('Interval',          50, 8, '4-5'),
     ('Easy Run',          50, 3, '2'),
     ('Tempo Run',         45, 6, '3-4'),
     ('Easy Run',          40, 3, '2'),
     ('Long Run',         100, 4, '2'),
     _R],
    # ── WEEK 10 Peak  (race-pace sharpener) ─────────────────────────────
    [_R,
     ('Interval',          45, 8, '4-5'),
     ('Easy Run',          50, 3, '2'),
     ('Race-Pace Tempo',   40, 7, '4'),
     ('Easy Run',          40, 3, '2'),
     ('Long Run',          90, 4, '2'),
     _R],
    # ── WEEK 11 Taper ───────────────────────────────────────────────────
    [_R,
     ('Easy Run',          40, 3, '1-2'),
     ('Tempo Run',         25, 6, '3-4'),
     ('Easy Run',          35, 3, '2'),
     _R,
     ('Medium Long Run',   60, 4, '2'),
     _R],
    # ── WEEK 12 Race Week ───────────────────────────────────────────────
    [_R,
     ('Easy Run',          30, 3, '1-2'),
     ('Easy + Strides',    20, 4, '2-3'),
     _R,
     ('Shakeout Run',      15, 2, '1'),
     ('RACE DAY',           0, 0, '4-5'),   # duration=0 so it doesn't inflate load
     _R],
]

_DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']


def _build_week(raw_week: list, cap_scale: float) -> tuple[list, float]:
    sessions = []
    for day, (stype, dur, rpe, zone) in zip(_DAYS, raw_week):
        scaled_dur = int(dur * cap_scale) if dur > 0 else 0
        sessions.append({
            'day':          day,
            'type':         stype,
            'duration_min': scaled_dur,
            'rpe':          rpe,
            'zone':         zone,
        })
    load = sum(s['rpe'] * s['duration_min'] for s in sessions)
    return sessions, load


def _capacity_label(score: float) -> str:
    if score < 40:
        return 'low'
    if score < 70:
        return 'medium'
    return 'high'


def _session_load(session: dict) -> float:
    return session['rpe'] * session['duration_min']


def generate_plan(target_distance: str, capacity_score: float, predicted_time_min: float) -> dict:
    """Returns week-1 plan for non-Half distances (used by demo.py)."""
    label    = _capacity_label(capacity_score)
    phases   = PHASE_SCHEDULE[target_distance]
    sessions = copy.deepcopy(_BASE_SESSIONS[label])
    mult     = PHASE_MULTIPLIER[phases[0]]
    for s in sessions:
        s['duration_min'] = int(s['duration_min'] * mult)
    load = sum(_session_load(s) for s in sessions)
    return {
        'target_distance':         target_distance,
        'predicted_goal_time_min': predicted_time_min,
        'num_weeks':               PLAN_WEEKS[target_distance],
        'week_1': {
            'phase':           phases[0],
            'capacity_label':  label,
            'sessions':        sessions,
            'planned_load_au': load,
        },
    }


def generate_full_plan(capacity_score: float, predicted_half_time_min: float) -> dict:
    """
    Returns a full 12-week Half Marathon training plan.
    Capacity score (0-100) from the fuzzy engine scales session durations.
    """
    label     = _capacity_label(capacity_score)
    cap_scale = _CAPACITY_SCALE[label]
    phases    = PHASE_SCHEDULE['Half']

    weeks = []
    for i, (raw_week, phase) in enumerate(zip(_HALF_PLAN_12W, phases), start=1):
        sessions, load = _build_week(raw_week, cap_scale)
        weeks.append({
            'week':            i,
            'phase':           phase,
            'sessions':        sessions,
            'planned_load_au': load,
        })

    return {
        'target_distance':         'Half Marathon',
        'predicted_goal_time_min': predicted_half_time_min,
        'num_weeks':               12,
        'capacity_label':          label,
        'capacity_score':          capacity_score,
        'weeks':                   weeks,
    }
