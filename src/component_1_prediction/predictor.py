import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

_FEATURES = ['vo2max', 'weekly_mileage_km', 'age', 'experience_months', 'long_run_km', 'resting_hr']


def _generate_synthetic_data(n=800, seed=42):
    rng = np.random.default_rng(seed)

    vo2max            = rng.uniform(35, 65, n)
    weekly_mileage_km = rng.uniform(20, 90, n)
    age               = rng.uniform(20, 60, n)
    experience_months = rng.uniform(0, 120, n)
    long_run_km       = weekly_mileage_km * rng.uniform(0.25, 0.40, n)
    resting_hr        = rng.uniform(45, 80, n)

    finish_time = (
        490
        - 4.5  * vo2max
        + 1.2  * (65 - weekly_mileage_km)
        + 0.4  * age
        - 0.3  * (experience_months / 12)
        - 0.4  * long_run_km
        + 0.1  * resting_hr
        + rng.normal(0, 12, n)
    )
    finish_time = np.clip(finish_time, 120, 420)

    X = np.column_stack([vo2max, weekly_mileage_km, age, experience_months, long_run_km, resting_hr])
    return X, finish_time


def train_model():
    X, y = _generate_synthetic_data()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)

    mae = mean_absolute_error(y_test, model.predict(X_test))
    print(f"  [C1] Model trained on {len(X_train)} synthetic samples | test MAE = {mae:.1f} min")
    return model


def predict_marathon_time(model, user_dict):
    features = np.array([[
        user_dict['vo2max'],
        user_dict['weekly_mileage_km'],
        user_dict['age'],
        user_dict['experience_months'],
        user_dict['long_run_km'],
        user_dict['resting_hr'],
    ]])
    return float(model.predict(features)[0])
