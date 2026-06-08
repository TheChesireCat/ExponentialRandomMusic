"""Parameter presets from noise through harmonic lock-in."""

RAW_RANDOM = {
    "beta_move": 0.0, "beta_social": 0.0, "beta_tuning": 0.0,
    "beta_memory": 0.0, "temperature": 10.0, "sigma": 12.0,
    "use_instrument_ranges": False,
}

RANGE_RANDOM = {
    "beta_move": 0.0, "beta_social": 0.0, "beta_tuning": 0.0,
    "beta_memory": 0.0, "temperature": 5.0, "sigma": 12.0,
    "use_instrument_ranges": True,
}

TUNING_CENTER_ONLY = {
    "beta_move": 0.2, "beta_social": 0.0, "beta_tuning": 1.5,
    "beta_memory": 0.5, "temperature": 2.0, "sigma": 7.0,
    "use_instrument_ranges": True,
}

HARMONIC_SOCIAL_TUNING = {
    "beta_move": 0.4, "beta_social": 0.8, "beta_tuning": 1.2,
    "beta_memory": 0.7, "temperature": 1.5, "sigma": 7.0,
    "use_instrument_ranges": True,
}

AMBIENT_HARMONY = {
    "beta_move": 0.6, "beta_social": 1.5, "beta_tuning": 0.8,
    "beta_memory": 1.2, "temperature": 1.0, "sigma": 6.0,
    "use_instrument_ranges": True,
}

LOCKED_IN = {
    "beta_move": 1.0, "beta_social": 4.0, "beta_tuning": 3.0,
    "beta_memory": 2.0, "temperature": 0.4, "sigma": 5.0,
    "use_instrument_ranges": True,
}

PRESETS = {
    "raw_random": RAW_RANDOM,
    "range_random": RANGE_RANDOM,
    "tuning_center_only": TUNING_CENTER_ONLY,
    "harmonic_social_tuning": HARMONIC_SOCIAL_TUNING,
    "ambient_harmony": AMBIENT_HARMONY,
    "locked_in": LOCKED_IN,
}

