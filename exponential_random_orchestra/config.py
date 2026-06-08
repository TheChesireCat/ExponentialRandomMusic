"""Shared configuration for the random orchestra."""

from pathlib import Path

PITCH_MIN = 36  # C2
PITCH_MAX = 96  # C7
PITCHES = list(range(PITCH_MIN, PITCH_MAX + 1))
A_PC = 9

DEFAULT_TOTAL_TIME = 30.0
DEFAULT_DT = 0.25
DEFAULT_SEED = 2026

PACKAGE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = PACKAGE_DIR / "output"
MIDI_DIR = OUTPUT_DIR / "midi"
PLOTS_DIR = OUTPUT_DIR / "plots"
DATA_DIR = OUTPUT_DIR / "data"


def ensure_output_directories() -> None:
    for directory in (MIDI_DIR, PLOTS_DIR, DATA_DIR):
        directory.mkdir(parents=True, exist_ok=True)

