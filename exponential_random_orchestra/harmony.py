"""Harmonic and motion scoring functions."""

CONSONANCE_WEIGHTS = {
    0: 3.0,
    1: -2.0,
    2: -0.5,
    3: 1.5,
    4: 1.8,
    5: 2.5,
    6: -2.5,
}

TONAL_CENTER_WEIGHTS = {
    0: 3.0,
    1: -1.0,
    2: 0.2,
    3: 1.0,
    4: 1.2,
    5: 2.0,
    6: -2.0,
}


def interval_class(pitch_a: int, pitch_b: int) -> int:
    distance = abs(pitch_a - pitch_b) % 12
    return min(distance, 12 - distance)


def circular_pc_distance(pc_a: int, pc_b: int) -> int:
    distance = abs(pc_a - pc_b) % 12
    return min(distance, 12 - distance)


def harmonic_weight(pitch_a: int, pitch_b: int, octave_penalty: float = 0.15) -> float:
    pitch_class_score = CONSONANCE_WEIGHTS[interval_class(pitch_a, pitch_b)]
    distance_penalty = octave_penalty * (abs(pitch_a - pitch_b) / 12.0)
    return pitch_class_score - distance_penalty


def tuning_score(pitch: int, target_pc: int = 9) -> float:
    return -float(circular_pc_distance(pitch % 12, target_pc))


def tonal_center_score(pitch: int, target_pc: int = 9) -> float:
    return TONAL_CENTER_WEIGHTS[interval_class(pitch % 12, target_pc)]


def memory_score(candidate_pitch: int, current_pitch: int, sigma: float = 7.0) -> float:
    if sigma <= 0:
        raise ValueError("sigma must be positive")
    return -((candidate_pitch - current_pitch) ** 2) / (sigma ** 2)

