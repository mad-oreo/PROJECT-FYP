# Shared preprocessing for Component 1, used by notebooks 02 and 03 so both
# train models with exactly the same inputs and transformations.

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler

NUMERIC = [
    "age",
    "bmi",
    "weekly_km",
    "runs_per_week",
    "long_run_distance_km",
    "resting_heart_rate_bpm",
    "running_experience_months",
]
PB = "personal_best_minutes"
CATEGORICAL = ["gender", "course_difficulty", "injury_severity"]

COURSE_ORDER = ["Flat", "Mixed", "Hilly"]
INJURY_ORDER = ["No injury", "Minor", "Moderate", "Severe"]


def _numeric_columns(drop=None):
    if drop is not None:
        assert drop in NUMERIC, f"drop must be one of the numeric columns, got {drop!r}"
    return [c for c in NUMERIC if c != drop]


def feature_list(use_pb=True, use_injury=True, drop=None):
    columns = _numeric_columns(drop)
    if use_pb:
        columns = columns + [PB]
    columns = columns + ["gender", "course_difficulty"]
    if use_injury:
        columns = columns + ["injury_severity"]
    return columns


def build_pipeline(model, use_pb=True, use_injury=True, drop=None):
    transformers = [("num", StandardScaler(), _numeric_columns(drop))]

    if use_pb:
        # Missing PB (first-timers) -> median placeholder + a 0/1 "PB missing" flag.
        # The median is learned in fit(), so only from the training data/folds.
        pb_steps = Pipeline([
            ("impute", SimpleImputer(strategy="median", add_indicator=True)),
            ("scale", StandardScaler()),
        ])
        transformers.append(("pb", pb_steps, [PB]))

    transformers.append(("gender", OneHotEncoder(drop="first"), ["gender"]))
    transformers.append(("course", OrdinalEncoder(categories=[COURSE_ORDER]), ["course_difficulty"]))

    if use_injury:
        transformers.append(("injury", OrdinalEncoder(categories=[INJURY_ORDER]), ["injury_severity"]))

    return Pipeline([("pre", ColumnTransformer(transformers)), ("model", model)])
