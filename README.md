# When Does Randomness Become Music?

This project began with hearing an orchestra tune. The sound felt random, but
not like white noise. The question is: what kind of randomness sounds musical?

We model each instrument as a random walker on a network of MIDI notes. A
walker is biased toward notes that are harmonically compatible, near a shared
tuning center, close to its previous note, and playable by that instrument.
Changing those constraints moves the system from random noise to tuning-like
texture, coherent harmony, and finally over-constrained lock-in.

## Introduction for network science students

You can read this project as an interacting random-walk model with a musical
state space:

- MIDI pitches are nodes in a pitch network. Edge weights encode harmonic
  compatibility between pairs of notes.
- Instruments are walkers. Each walker occupies one pitch at a time and has a
  restricted set of nodes determined by the instrument's playable range.
- A second, instrument-level network controls social coupling. Its weighted
  adjacency matrix determines how strongly one instrument responds to the
  pitches currently played by the others.
- The next pitch is sampled from a softmax distribution, similar to a Gibbs
  update. Temperature controls stochasticity, while coupling, tuning, and
  memory terms shape the local energy landscape.

The central network-science question is how collective structure emerges as
these controls change. Weak coupling and high temperature produce nearly
independent walkers; stronger coupling produces correlated harmonic motion;
very low temperature or excessive coupling can collapse the system into a
small set of states. The included parameter sweep visualizes this transition
using entropy and consonance as macroscopic observables.

No music-theory background is required. Start by comparing the six presets,
then open the phase-diagram notebook to study how temperature and social
coupling change the system-level behavior.

## Model

For instrument `i`, the probability of choosing pitch `q` is

```text
P(p_i(t+1) = q) = exp(S_i(q,t) / tau) / sum_r exp(S_i(r,t) / tau)

S_i(q,t) =
    beta_move   * w(p_i(t), q)
  + beta_social * sum_{j != i} A_ij w(q, p_j(t))
  + beta_tuning * T(q)
  + beta_memory * M(q, p_i(t))
```

`tau` is temperature. High temperature produces freer motion; low temperature
makes the walkers follow the score more deterministically. Harmonic identity is
computed from pitch class while MIDI pitch preserves register and octave
distance.

## Outputs

The six presets form an intended progression:

1. `raw_random`: notes sampled across the global C2-C7 range
2. `range_random`: randomness limited to each instrument's playable range
3. `tuning_center_only`: attraction to A with light melodic memory
4. `harmonic_social_tuning`: coupled tuning-like random walkers
5. `ambient_harmony`: smoother and more strongly coupled motion
6. `locked_in`: low-temperature, over-constrained harmonic convergence

Running the project writes MIDI clips, per-step metric CSVs, metric plots, a
phase diagram, and pitch-network visualizations under
`exponential_random_orchestra/output/`.

## Setup and run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r exponential_random_orchestra/requirements.txt
python -m exponential_random_orchestra.main
```

For a faster smoke run that skips the phase sweep:

```bash
python -m exponential_random_orchestra.main --duration 5 --skip-phase-sweep
```

Run tests with:

```bash
python -m unittest discover -s tests
```

## Explore the outputs

The `notebooks/` directory contains reproducible analyses of the generated
artifacts. Install the optional notebook tools and start Jupyter from the
repository root:

```bash
pip install -r requirements-notebooks.txt
jupyter lab
```

Start with `01_preset_output_exploration.ipynb`, then use
`02_phase_diagram_exploration.ipynb` to inspect the parameter sweep.

## Metrics

- Pitch-class entropy measures variety.
- Average consonance measures pairwise harmonic compatibility.
- Average tuning score measures attraction to A and related pitch classes.
- The phase diagram uses normalized entropy times normalized consonance as a
  deliberately simple "music-like texture" score. Random noise has variety but
  low consonance; lock-in has consonance but little variety; the interesting
  region lies between them.
