"""Plots for the metrics, phase sweep, and pitch network."""

import os
from pathlib import Path

os.environ.setdefault(
    "MPLCONFIGDIR", str(Path(__file__).resolve().parent / "output" / ".matplotlib")
)

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from .config import PITCHES
from .harmony import harmonic_weight

PITCH_CLASS_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def plot_metrics_over_time(metrics, output_path, title):
    figure, axis_entropy = plt.subplots(figsize=(10, 5))
    axis_consonance = axis_entropy.twinx()
    axis_entropy.plot(metrics["time"], metrics["pitch_class_entropy"], color="#3366cc", label="Pitch-class entropy")
    axis_consonance.plot(metrics["time"], metrics["average_consonance"], color="#cc3333", label="Average consonance")
    axis_entropy.set(xlabel="Time (seconds)", ylabel="Pitch-class entropy", title=title)
    axis_consonance.set_ylabel("Average consonance")
    lines = axis_entropy.lines + axis_consonance.lines
    axis_entropy.legend(lines, [line.get_label() for line in lines], loc="upper right")
    figure.tight_layout()
    figure.savefig(output_path, dpi=160)
    plt.close(figure)


def plot_phase_diagram(temperatures, social_values, scores, output_path):
    figure, axis = plt.subplots(figsize=(9, 6))
    image = axis.imshow(
        scores,
        origin="lower",
        aspect="auto",
        extent=[temperatures[0], temperatures[-1], social_values[0], social_values[-1]],
        cmap="magma",
    )
    axis.set(xlabel="Temperature", ylabel="Social coupling (beta_social)", title="Music-like Texture Score")
    figure.colorbar(image, ax=axis, label="Normalized entropy x consonance")
    figure.tight_layout()
    figure.savefig(output_path, dpi=180)
    plt.close(figure)


def plot_pitch_class_circle(output_path):
    angles = np.linspace(0, 2 * np.pi, 12, endpoint=False)
    positions = np.column_stack((np.cos(angles), np.sin(angles)))
    figure, axis = plt.subplots(figsize=(8, 8))

    for i in range(12):
        for j in range(i + 1, 12):
            weight = harmonic_weight(60 + i, 60 + j, octave_penalty=0.0)
            if weight <= 1.4:
                continue
            axis.plot(
                [positions[i, 0], positions[j, 0]],
                [positions[i, 1], positions[j, 1]],
                color="#557799",
                alpha=min(0.75, weight / 4.0),
                linewidth=max(0.5, weight / 2.0),
                zorder=1,
            )

    axis.scatter(positions[:, 0], positions[:, 1], s=650, color="#f2d06b", edgecolor="#333333", zorder=2)
    for name, (x, y) in zip(PITCH_CLASS_NAMES, positions):
        axis.text(x, y, name, ha="center", va="center", zorder=3)
    axis.set(title="Pitch-Class Harmonic Network", aspect="equal")
    axis.axis("off")
    figure.tight_layout()
    figure.savefig(output_path, dpi=180)
    plt.close(figure)


def plot_pitch_spiral(output_path):
    pitches = np.asarray(PITCHES)
    theta = 2 * np.pi * (pitches % 12) / 12.0
    radius = 1 + 0.03 * (pitches - 60)
    x = radius * np.cos(theta)
    y = radius * np.sin(theta)

    figure, axis = plt.subplots(figsize=(9, 9))
    axis.plot(x, y, color="#999999", alpha=0.55, linewidth=1)
    scatter = axis.scatter(x, y, c=pitches, cmap="viridis", s=35, zorder=2)
    for pitch, px, py in zip(pitches, x, y):
        if pitch % 12 == 9:
            axis.scatter(px, py, color="#d43f3a", s=75, zorder=3)
    for pc, name in enumerate(PITCH_CLASS_NAMES):
        angle = 2 * np.pi * pc / 12.0
        axis.text(2.25 * np.cos(angle), 2.25 * np.sin(angle), name, ha="center", va="center")
    axis.set(title="MIDI Pitch Spiral: Octaves Share an Angle", aspect="equal")
    axis.axis("off")
    figure.colorbar(scatter, ax=axis, shrink=0.7, label="MIDI pitch")
    figure.tight_layout()
    figure.savefig(output_path, dpi=180)
    plt.close(figure)
