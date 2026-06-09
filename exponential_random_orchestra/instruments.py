"""Instrument definitions and social-listening relationships."""

import numpy as np

INSTRUMENTS = [
    {
        "name": "Violin 1", "section": "strings", "program": 40,
        "pitch_min": 55, "pitch_max": 96, "activity_rate": 0.35,
        "volume_mean": 65, "volume_std": 12,
    },
    {
        "name": "Violin 2", "section": "strings", "program": 40,
        "pitch_min": 55, "pitch_max": 92, "activity_rate": 0.30,
        "volume_mean": 60, "volume_std": 12,
    },
    {
        "name": "Viola", "section": "strings", "program": 41,
        "pitch_min": 48, "pitch_max": 84, "activity_rate": 0.28,
        "volume_mean": 60, "volume_std": 10,
    },
    {
        "name": "Cello", "section": "strings", "program": 42,
        "pitch_min": 36, "pitch_max": 76, "activity_rate": 0.25,
        "volume_mean": 58, "volume_std": 10,
    },
    {
        "name": "Bass", "section": "strings", "program": 43,
        "pitch_min": 28, "pitch_max": 60, "activity_rate": 0.18,
        "volume_mean": 58, "volume_std": 10,
    },
    {
        "name": "Flute", "section": "winds", "program": 73,
        "pitch_min": 60, "pitch_max": 96, "activity_rate": 0.20,
        "volume_mean": 55, "volume_std": 10,
    },
    {
        "name": "Clarinet", "section": "winds", "program": 71,
        "pitch_min": 50, "pitch_max": 88, "activity_rate": 0.22,
        "volume_mean": 58, "volume_std": 10,
    },
    {
        "name": "Oboe", "section": "winds", "program": 68,
        "pitch_min": 58, "pitch_max": 91, "activity_rate": 0.18,
        "volume_mean": 60, "volume_std": 8,
    },
    {
        "name": "Piccolo", "section": "winds", "program": 72,
        "pitch_min": 74, "pitch_max": 103, "activity_rate": 0.12,
        "volume_mean": 52, "volume_std": 8,
    },
    {
        "name": "Bassoon", "section": "winds", "program": 70,
        "pitch_min": 34, "pitch_max": 75, "activity_rate": 0.16,
        "volume_mean": 57, "volume_std": 9,
    },
    {
        "name": "French Horn", "section": "brass", "program": 60,
        "pitch_min": 41, "pitch_max": 77, "activity_rate": 0.17,
        "volume_mean": 58, "volume_std": 9,
    },
    {
        "name": "Trumpet", "section": "brass", "program": 56,
        "pitch_min": 54, "pitch_max": 82, "activity_rate": 0.14,
        "volume_mean": 60, "volume_std": 9,
    },
    {
        "name": "Trombone", "section": "brass", "program": 57,
        "pitch_min": 40, "pitch_max": 72, "activity_rate": 0.13,
        "volume_mean": 59, "volume_std": 9,
    },
    {
        "name": "Tuba", "section": "brass", "program": 58,
        "pitch_min": 28, "pitch_max": 58, "activity_rate": 0.11,
        "volume_mean": 58, "volume_std": 8,
    },
    {
        "name": "Grand Piano", "section": "keyboard", "program": 0,
        "pitch_min": 36, "pitch_max": 96, "activity_rate": 0.22,
        "volume_mean": 57, "volume_std": 10,
    },
]


def build_interaction_matrix(instruments=INSTRUMENTS):
    count = len(instruments)
    matrix = np.zeros((count, count), dtype=float)

    for i, listener in enumerate(instruments):
        for j, source in enumerate(instruments):
            if i == j:
                continue
            matrix[i, j] = 1.0 if listener["section"] == source["section"] else 0.25
            if source["name"] == "Oboe":
                matrix[i, j] += 0.75

    return matrix
