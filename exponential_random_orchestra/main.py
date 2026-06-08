"""Command-line entry point for generating the complete demo."""

import argparse

import numpy as np

from .config import (
    DATA_DIR,
    DEFAULT_DT,
    DEFAULT_SEED,
    DEFAULT_TOTAL_TIME,
    MIDI_DIR,
    PLOTS_DIR,
    ensure_output_directories,
)
from .generator import generate_sequence, write_midi
from .instruments import INSTRUMENTS
from .metrics import compute_metrics_over_time, music_like_score
from .presets import HARMONIC_SOCIAL_TUNING, PRESETS
from .visualize import (
    plot_metrics_over_time,
    plot_phase_diagram,
    plot_pitch_class_circle,
    plot_pitch_spiral,
)


def run_presets(total_time, dt, seed):
    for index, (name, params) in enumerate(PRESETS.items()):
        events, history = generate_sequence(
            INSTRUMENTS, params, total_time=total_time, dt=dt, seed=seed + index
        )
        write_midi(events, INSTRUMENTS, MIDI_DIR / f"{name}.mid")
        metrics = compute_metrics_over_time(history, dt=dt)
        metrics.to_csv(DATA_DIR / f"{name}_metrics.csv", index=False)
        plot_metrics_over_time(
            metrics,
            PLOTS_DIR / f"{name}_metrics.png",
            title=name.replace("_", " ").title(),
        )
        print(f"generated {name}: {len(events)} events")


def run_phase_sweep(dt, seed, grid_size=25, duration=10.0):
    social_values = np.linspace(0.0, 3.0, grid_size)
    temperatures = np.linspace(0.3, 5.0, grid_size)
    mean_entropy = np.zeros((grid_size, grid_size))
    mean_consonance = np.zeros((grid_size, grid_size))

    for social_index, beta_social in enumerate(social_values):
        for temperature_index, temperature in enumerate(temperatures):
            params = HARMONIC_SOCIAL_TUNING.copy()
            params["beta_social"] = float(beta_social)
            params["temperature"] = float(temperature)
            _, history = generate_sequence(
                INSTRUMENTS,
                params,
                total_time=duration,
                dt=dt,
                seed=seed + social_index * grid_size + temperature_index,
            )
            metrics = compute_metrics_over_time(history, dt=dt)
            mean_entropy[social_index, temperature_index] = metrics["pitch_class_entropy"].mean()
            mean_consonance[social_index, temperature_index] = metrics["average_consonance"].mean()

    scores = music_like_score(mean_entropy, mean_consonance)
    plot_phase_diagram(
        temperatures, social_values, scores, PLOTS_DIR / "phase_diagram.png"
    )
    np.savez(
        DATA_DIR / "phase_diagram.npz",
        temperatures=temperatures,
        beta_social=social_values,
        mean_entropy=mean_entropy,
        mean_consonance=mean_consonance,
        music_like_score=scores,
    )
    print(f"generated phase diagram: {grid_size}x{grid_size} sweep")


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--duration", type=float, default=DEFAULT_TOTAL_TIME)
    parser.add_argument("--dt", type=float, default=DEFAULT_DT)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--phase-grid-size", type=int, default=25)
    parser.add_argument("--phase-duration", type=float, default=10.0)
    parser.add_argument("--skip-phase-sweep", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()
    ensure_output_directories()
    run_presets(args.duration, args.dt, args.seed)
    plot_pitch_class_circle(PLOTS_DIR / "pitch_class_circle.png")
    plot_pitch_spiral(PLOTS_DIR / "pitch_spiral.png")
    if not args.skip_phase_sweep:
        run_phase_sweep(
            args.dt, args.seed + 10_000, args.phase_grid_size, args.phase_duration
        )


if __name__ == "__main__":
    main()

