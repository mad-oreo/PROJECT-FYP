import numpy as np


class ProportionalController:
    """
    Closed-loop proportional controller for weekly training load adjustment.

    Adjustment polarity: easing.
      - Missed sessions (actual < planned) → scale < 1.0 → next week is easier.
      - Consistent sessions (actual >= planned) → scale >= 1.0 → next week progresses.
    This easing polarity is Naji's own design, distinct from the make-up polarity
    in Connor et al. (2022). The choice is deliberate: safer for beginner runners.

    K = 0.5 (gain), ACWR cap = 1.5 (safety ceiling from Zhou & Zhou, 2025).
    """

    def __init__(self, K: float = 0.5, acwr_cap: float = 1.5):
        self.K        = K
        self.acwr_cap = acwr_cap
        self._history: list[float] = []   # actual loads, oldest → newest

    def log_week(self, planned_load_au: float, actual_load_au: float) -> float:
        """
        Record the week's result and return the scale factor for next week's load.

        scale < 1.0 → ease
        scale = 1.0 → hold
        scale > 1.0 → progress
        """
        self._history.append(actual_load_au)

        if planned_load_au <= 0:
            return 1.0

        # Proportional adjustment
        error      = planned_load_au - actual_load_au   # positive = under-performed
        raw_scale  = 1.0 - self.K * (error / planned_load_au)
        raw_scale  = float(np.clip(raw_scale, 0.5, 1.5))

        # ACWR safety cap — only applies when we have at least 2 weeks of history
        if len(self._history) >= 2:
            window  = self._history[-4:]           # rolling 4-week window
            chronic = float(np.mean(window))
            if chronic > 0:
                proposed_next = planned_load_au * raw_scale
                acwr          = proposed_next / chronic
                if acwr > self.acwr_cap:
                    raw_scale = (self.acwr_cap * chronic) / planned_load_au

        return float(raw_scale)

    @property
    def load_history(self) -> list:
        return list(self._history)
