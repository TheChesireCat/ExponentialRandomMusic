"""Metrics for variety, consonance, and tuning-center attraction."""

from itertools import combinations

import numpy as np
import pandas as pd

from .config import A_PC
from .harmony import harmonic_weight, tonal_center_score


def pitch_class_entropy(active_pitches) -> float:
    if not active_pitches:
        return np.nan
    pitch_classes = [pitch % 12 for pitch in active_pitches]
    counts = np.bincount(pitch_classes, minlength=12)
    probabilities = counts[counts > 0] / counts.sum()
    return float(-np.sum(probabilities * np.log(probabilities)))


def average_consonance(active_pitches) -> float:
    if len(active_pitches) < 2:
        return np.nan
    values = [harmonic_weight(a, b) for a, b in combinations(active_pitches, 2)]
    return float(np.mean(values))


def average_tuning_score(active_pitches) -> float:
    if not active_pitches:
        return np.nan
    return float(np.mean([tonal_center_score(pitch, A_PC) for pitch in active_pitches]))


def compute_metrics_over_time(state_history, dt=0.25):
    rows = []
    for step, state in enumerate(state_history):
        active = [pitch for pitch in state if pitch is not None]
        rows.append({
            "time": step * dt,
            "active_count": len(active),
            "pitch_class_entropy": pitch_class_entropy(active),
            "average_consonance": average_consonance(active),
            "average_tuning_score": average_tuning_score(active),
        })
    return pd.DataFrame(rows)


def normalize(values):
    array = np.asarray(values, dtype=float)
    finite = np.isfinite(array)
    result = np.zeros_like(array)
    if not finite.any():
        return result
    minimum = np.min(array[finite])
    maximum = np.max(array[finite])
    if np.isclose(minimum, maximum):
        result[finite] = 0.5
    else:
        result[finite] = (array[finite] - minimum) / (maximum - minimum)
    return result


def music_like_score(entropy, consonance):
    return normalize(entropy) * normalize(consonance)

