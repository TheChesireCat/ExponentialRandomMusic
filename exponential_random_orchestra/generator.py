"""Sequence generation and MIDI serialization."""

from collections.abc import Sequence

import numpy as np
import pretty_midi

from .config import A_PC, PITCH_MAX, PITCH_MIN
from .harmony import harmonic_weight, memory_score, tonal_center_score
from .instruments import build_interaction_matrix


def sample_softmax(candidates: Sequence[int], scores: Sequence[float], temperature: float, rng) -> int:
    if temperature <= 0:
        raise ValueError("temperature must be positive")
    score_array = np.asarray(scores, dtype=float)
    logits = score_array / temperature
    logits -= np.max(logits)
    probabilities = np.exp(logits)
    probabilities /= probabilities.sum()
    return int(rng.choice(candidates, p=probabilities))


def sample_duration(rng) -> float:
    durations = np.array([0.25, 0.5, 1.0, 1.5, 2.0])
    probabilities = np.array([0.10, 0.20, 0.35, 0.25, 0.10])
    return float(rng.choice(durations, p=probabilities))


def sample_velocity(instrument, rng) -> int:
    velocity = rng.normal(instrument["volume_mean"], instrument["volume_std"])
    return int(np.clip(round(velocity), 25, 100))


def _candidate_pitches(instrument, use_instrument_ranges: bool):
    if use_instrument_ranges:
        return list(range(instrument["pitch_min"], instrument["pitch_max"] + 1))
    return list(range(PITCH_MIN, PITCH_MAX + 1))


def _initial_pitch(instrument, use_instrument_ranges: bool, rng) -> int:
    candidates = _candidate_pitches(instrument, use_instrument_ranges)
    return int(rng.choice(candidates))


def generate_sequence(instruments, params, total_time=30.0, dt=0.25, seed=None):
    if total_time <= 0 or dt <= 0:
        raise ValueError("total_time and dt must be positive")

    rng = np.random.default_rng(seed)
    interaction_matrix = build_interaction_matrix(instruments)
    use_ranges = params.get("use_instrument_ranges", True)
    current_pitches = [
        _initial_pitch(instrument, use_ranges, rng) for instrument in instruments
    ]
    sounding_until = np.full(len(instruments), -np.inf)
    last_event_indexes = [None] * len(instruments)

    events = []
    state_history = []
    num_steps = int(np.ceil(total_time / dt))

    for step in range(num_steps):
        current_time = step * dt
        for i, instrument in enumerate(instruments):
            if rng.random() > instrument["activity_rate"]:
                continue

            candidates = _candidate_pitches(instrument, use_ranges)
            scores = []
            for candidate in candidates:
                move = harmonic_weight(current_pitches[i], candidate)
                social = sum(
                    interaction_matrix[i, j] * harmonic_weight(candidate, current_pitches[j])
                    for j in range(len(instruments))
                    if j != i
                )
                tuning = tonal_center_score(candidate, target_pc=A_PC)
                memory = memory_score(candidate, current_pitches[i], sigma=params["sigma"])
                scores.append(
                    params["beta_move"] * move
                    + params["beta_social"] * social
                    + params["beta_tuning"] * tuning
                    + params["beta_memory"] * memory
                )

            selected_pitch = sample_softmax(
                candidates, scores, params["temperature"], rng
            )
            duration = sample_duration(rng)
            previous_event_index = last_event_indexes[i]
            if previous_event_index is not None:
                previous_event = events[previous_event_index]
                if previous_event["end"] > current_time:
                    previous_event["end"] = current_time

            events.append({
                "instrument_id": i,
                "instrument_name": instrument["name"],
                "pitch": selected_pitch,
                "start": current_time,
                "end": min(current_time + duration, total_time),
                "velocity": sample_velocity(instrument, rng),
            })
            last_event_indexes[i] = len(events) - 1
            current_pitches[i] = selected_pitch
            sounding_until[i] = min(current_time + duration, total_time)

        active_pitches = [
            current_pitches[i] if sounding_until[i] > current_time else None
            for i in range(len(instruments))
        ]
        state_history.append(active_pitches)

    return events, state_history


def write_midi(events, instruments, output_path) -> None:
    midi = pretty_midi.PrettyMIDI()
    tracks = {}

    for i, instrument in enumerate(instruments):
        track = pretty_midi.Instrument(
            program=instrument["program"], name=instrument["name"]
        )
        tracks[i] = track
        midi.instruments.append(track)

    for event in events:
        note = pretty_midi.Note(
            velocity=event["velocity"],
            pitch=event["pitch"],
            start=event["start"],
            end=max(event["end"], event["start"] + 0.01),
        )
        tracks[event["instrument_id"]].notes.append(note)

    midi.write(str(output_path))
