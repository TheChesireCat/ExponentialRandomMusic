"""Render General MIDI files with sampled SoundFont instruments."""

from pathlib import Path
import shutil
import subprocess
import tempfile


DEFAULT_SOUNDFONT_PATHS = (
    Path("/usr/share/sounds/sf2/default-GM.sf2"),
    Path("/usr/share/sounds/sf2/FluidR3_GM.sf2"),
    Path("/usr/share/soundfonts/FluidR3_GM.sf2"),
)


def find_soundfont(requested_path=None) -> Path:
    """Return an explicit or commonly installed General MIDI SoundFont."""
    if requested_path is not None:
        path = Path(requested_path).expanduser()
        if not path.is_file():
            raise FileNotFoundError(f"SoundFont not found: {path}")
        return path

    for path in DEFAULT_SOUNDFONT_PATHS:
        if path.is_file():
            return path

    raise FileNotFoundError(
        "No General MIDI SoundFont found. Install fluid-soundfont-gm or pass "
        "--soundfont /path/to/file.sf2."
    )


def _require_command(command: str) -> str:
    executable = shutil.which(command)
    if executable is None:
        raise RuntimeError(
            f"Required command '{command}' was not found. "
            "Install FluidSynth and FFmpeg before rendering audio."
        )
    return executable


def render_midi_to_mp3(
    midi_path,
    mp3_path,
    soundfont_path=None,
    sample_rate=44_100,
    bitrate="192k",
) -> None:
    """Render a MIDI file to MP3 using its General MIDI instrument programs."""
    midi_path = Path(midi_path)
    mp3_path = Path(mp3_path)
    if not midi_path.is_file():
        raise FileNotFoundError(f"MIDI file not found: {midi_path}")

    soundfont_path = find_soundfont(soundfont_path)
    fluidsynth = _require_command("fluidsynth")
    ffmpeg = _require_command("ffmpeg")
    mp3_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="random-orchestra-") as temp_dir:
        wav_path = Path(temp_dir) / "render.wav"
        subprocess.run(
            [
                fluidsynth,
                "-ni",
                "-F",
                str(wav_path),
                "-r",
                str(sample_rate),
                "-g",
                "0.7",
                str(soundfont_path),
                str(midi_path),
            ],
            check=True,
        )
        subprocess.run(
            [
                ffmpeg,
                "-y",
                "-loglevel",
                "error",
                "-i",
                str(wav_path),
                "-codec:a",
                "libmp3lame",
                "-b:a",
                bitrate,
                str(mp3_path),
            ],
            check=True,
        )
