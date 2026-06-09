# When Does Randomness Become Music?

This project began with hearing an orchestra tune. The sound felt random, but
not like static. It was messy, but still somehow musical. The question is: what
kind of randomness has that property?

This repository builds a small generative model around that question. Each
instrument is represented as a random walker on a network of MIDI notes. The
walker is biased toward notes that are harmonically compatible with its
previous note and with the notes currently played by other instruments, near a
shared tuning center, close to its previous pitch, and playable by that
instrument. By changing the strength of these constraints, the same model moves
from unconstrained randomness to tuning-like texture, coherent harmonic
texture, and finally over-constrained lock-in.

> **In 10 seconds:** This repository generates short MIDI and MP3 clips from a
> family of stochastic note-walk models, then measures how pitch entropy,
> consonance, and tuning-center attraction change across parameter regimes. The
> main artifact is a progression of sounds and plots showing a transition from
> unconstrained randomness to structured musical texture and then to
> over-constrained lock-in.

| | |
| --- | --- |
| **Python** | 3.10+ |
| **Outputs** | MIDI, MP3, CSV, PNG |
| **Core dependencies** | NumPy, pandas, Matplotlib, pretty_midi |
| **Optional rendering** | FluidSynth, FFmpeg, General MIDI SoundFont |

```bash
python -m exponential_random_orchestra.main --render-audio
```

## What this is showing

The point is not to build a realistic orchestra simulator or an automatic
composer. The point is to make a simple mathematical idea audible:

> Randomness can sound structured when it moves through a constrained
> perceptual geometry.

The pitch network supplies the geometry. The random walkers supply
stochasticity. Social coupling and tuning-center attraction create collective
structure.

Running the project produces:

- six MIDI clips and optional MP3 renderings
- per-preset metric plots
- a temperature/coupling phase diagram
- pitch-network visualizations
- CSV and NPZ files for downstream analysis

## Listen to the progression

Each example is the same model with a different constraint preset. Listen from
free randomness toward over-constrained harmonic lock-in:

| Stage | Preset | What to listen for | MP3 |
| ---: | --- | --- | --- |
| 1 | `raw_random` | Unrestricted pitches across C2-C7 | **[Play MP3](exponential_random_orchestra/output/mp3/raw_random.mp3?raw=1)** |
| 2 | `range_random` | Each instrument enters its playable range | **[Play MP3](exponential_random_orchestra/output/mp3/range_random.mp3?raw=1)** |
| 3 | `tuning_center_only` | Notes begin gathering around A | **[Play MP3](exponential_random_orchestra/output/mp3/tuning_center_only.mp3?raw=1)** |
| 4 | `harmonic_social_tuning` | Instruments react to one another | **[Play MP3](exponential_random_orchestra/output/mp3/harmonic_social_tuning.mp3?raw=1)** |
| 5 | `ambient_harmony` | Smoother, more strongly coupled motion | **[Play MP3](exponential_random_orchestra/output/mp3/ambient_harmony.mp3?raw=1)** |
| 6 | `locked_in` | Low-temperature harmonic convergence | **[Play MP3](exponential_random_orchestra/output/mp3/locked_in.mp3?raw=1)** |

The presets are ordered by increasing constraint, not by musical quality. The
interesting region is not necessarily the most ordered one. In many runs, the
middle regimes are more texture-like, while `locked_in` is intentionally
over-constrained.

When listening, ask: does this sound random, tuning-like, musical, pleasant, or
boring?

> GitHub repository READMEs do not reliably allow embedded HTML audio controls.
> These raw-file links open the tracked MP3s in the browser's native player.

## Model in one paragraph

This is a state-dependent biased random walk. Without social coupling, each
instrument performs an independent random walk over its playable region of the
pitch network. With social coupling, its transition probabilities also depend
on the current positions of the other walkers. Harmonic compatibility,
tuning-center attraction, and melodic memory shape a local score, and the next
pitch is sampled from a temperature-controlled softmax distribution.

## Network science interpretation

You can read this project as an interacting random-walk model with a musical
state space. There are two networks:

1. **Pitch network:** nodes are MIDI notes; weighted edges encode harmonic
   compatibility.
2. **Instrument network:** nodes are instruments; directed weighted edges
   encode who listens to whom.

The walkers move on the pitch network, but their transition probabilities are
modulated by the instrument network. Every instrument listens to every other;
within-section influence is stronger than cross-section influence, and the oboe
has an additional source-weight bonus.

The central network-science question is how collective structure emerges as
temperature and coupling change. Weak coupling and high temperature produce
nearly independent walkers. Stronger coupling produces correlated harmonic
motion. Very low temperature or excessive coupling can collapse the system into
a small set of states. The parameter sweep visualizes this transition using
pitch-class entropy and average consonance as macroscopic observables.

No music-theory background is required. Start with the six recordings, then
open the phase-diagram notebook to study how temperature and social coupling
change the system-level behavior.

## Transition rule

For instrument `i`, the probability of choosing pitch `q` is

```text
P(p_i(t+1) = q) = exp(S_i(q,t) / tau) / sum_r exp(S_i(r,t) / tau)

S_i(q,t) =
    beta_move   * w(p_i(t), q)
  + beta_social * sum_{j != i} A_ij w(q, p_j(t))
  + beta_tuning * T(q)
  + beta_memory * M(q, p_i(t))
```

Where:

- `w(p, q)` is harmonic compatibility between two MIDI pitches. It is computed
  mostly from pitch-class interval, with a small penalty for large octave gaps.
- `T(q)` is the tuning-center score. It rewards A and harmonically related
  pitch classes.
- `M(q, p_i(t))` is the memory or inertia term. It penalizes large jumps from
  the instrument's previous pitch.
- `A_ij` is the directed instrument-level coupling weight from instrument `j`
  to instrument `i`.
- `tau` is temperature. Larger `tau` makes the walk more random; smaller `tau`
  makes it more deterministic.

Equivalently, each candidate pitch defines a local energy. Notes that are
harmonically compatible, close to the tuning center, and close to the previous
pitch have lower energy and are sampled more often. Temperature controls how
strongly the walkers obey this energy landscape.

### Pitch classes and octaves

The model uses MIDI pitch as the actual state, so `A3`, `A4`, and `A5` are
different nodes. Harmonic identity is computed mostly from pitch class, so
octave-equivalent notes remain related. This preserves register and instrument
range while treating octaves, fifths, and thirds as special harmonic
relations.

## Network at a glance

```text
              INSTRUMENT-LEVEL SOCIAL NETWORK (SCHEMATIC)

     complete directed graph: every instrument listens to every other
     same-section edges = 1.00             cross-section edges = 0.25

     +----------- STRINGS -----------+   +---------- WINDS ----------+
     | Violin 1, Violin 2, Viola,    |...| Piccolo, Flute, Oboe,     |
     | Cello, Bass                   |   | Clarinet, Bassoon         |
     +-------------------------------+   +---------------------------+
                   .                                  .
                    .                                .
              +-----+-------+                +------+------+
              |   KEYBOARD  |................|    BRASS    |
              | Grand Piano |                | Horn, Trumpet,|
              +-------------+                | Trombone, Tuba |
                                             +---------------+

                         every instrument listens more strongly
                         to the oboe: source edge bonus = +0.75

                                      |
                                      v
            PITCH NETWORK WITH INSTRUMENTS AS RANDOM WALKERS

                                      Violin 2
                                         |
                                         v
                         .---------[ E5 ]---------.
                        /             ^            \
                       /              |             \
                  [ C5 ]----------[ A4 ]----------[ C#5 ]
                    ^  \          tonal center       /  ^
                   /    \             |             /    \
     Viola, Horn --'      \            |            /      `-- Flute, Piccolo
                         [ E4 ]------[ A3 ]------[ D4 ]
                           ^           ^           ^  \
                           |           |           |   `-- Clarinet
                  Violin 1, Piano  Cello, Bassoon  Oboe, Trumpet
                                       \
                                        `----[ A2 ]
                                                ^
                                                |
                                      Bass, Trombone, Tuba

       Each [note] is a MIDI-pitch node. An instrument label marks the
       node currently occupied by that walker's sounding pitch.
```

## Metrics and phase diagram

- Pitch-class entropy measures variety.
- Average consonance measures pairwise harmonic compatibility.
- Average tuning score measures attraction to A and related pitch classes.
- The phase diagram uses normalized entropy times normalized consonance as a
  deliberately simple "music-like texture" score. Random noise has variety but
  low consonance; lock-in has consonance but little variety; the interesting
  region lies between them.

## Setup and run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r exponential_random_orchestra/requirements.txt
python -m exponential_random_orchestra.main
```

The 15 MIDI tracks preserve a General MIDI program for every instrument. To
render them as sampled instruments, install FluidSynth, FFmpeg, and a General
MIDI SoundFont. On Ubuntu/Debian:

```bash
sudo apt install fluidsynth fluid-soundfont-gm ffmpeg
python -m exponential_random_orchestra.main --render-audio
```

On other systems, pass a downloaded `.sf2` or `.sf3` file explicitly:

```bash
python -m exponential_random_orchestra.main \
  --render-audio \
  --soundfont /path/to/orchestral-general-midi.sf2
```

Use `--seed` to reproduce a run exactly. The default seed is `2026`; changing
it produces another realization of the same stochastic model.

```bash
python -m exponential_random_orchestra.main --seed 42
```

For a faster smoke run that skips the phase sweep:

```bash
python -m exponential_random_orchestra.main --duration 5 --skip-phase-sweep
```

Run tests with:

```bash
python -m unittest discover -s tests
```

## Recommended path

1. Listen to the six MP3s in order.
2. Compare the metric plots for `raw_random`, `harmonic_social_tuning`, and
   `locked_in`.
3. Open `02_phase_diagram_exploration.ipynb`.
4. Change `beta_social` and `temperature` in the presets and regenerate the
   outputs.

## Explore the outputs

Generated artifacts are stored under `exponential_random_orchestra/output/`:

- `midi/` and `mp3/`: one clip per preset
- `plots/`: per-preset metrics, the phase diagram, and pitch-network views
- `data/`: per-step metric CSVs and the phase-sweep NPZ archive

The `notebooks/` directory contains reproducible analyses of these artifacts.
Install the optional notebook tools and start Jupyter from the repository root:

```bash
pip install -r requirements-notebooks.txt
jupyter lab
```

Start with `01_preset_output_exploration.ipynb`, then use
`02_phase_diagram_exploration.ipynb` to inspect the parameter sweep.

## Limitations

This is a toy explanatory model, not a realistic model of orchestral
performance. It does not model rhythm, phrasing, score-following, room
acoustics, expressive timing, or microtonal pitch adjustment. Standard MIDI
also quantizes pitch to semitones, so the model captures note-choice structure
rather than fine-grained tuning convergence. The purpose is to illustrate
constrained stochastic dynamics, not to reproduce a real orchestra.

## Possible extensions

- Fit model parameters to existing MIDI files using conditional-logit
  likelihood.
- Infer the best-fitting tonal center instead of fixing A.
- Replace MIDI note choices with continuous pitch estimates from audio.
- Reconstruct an instrument-level influence network from observed note choices.
- Compare generated clips with human ratings of random, tuning-like, musical,
  pleasant, and boring.
- Add a null-model comparison between the full model, uniform random sampling,
  and range-only random sampling.
