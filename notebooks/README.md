# Exploration notebooks

Run the generator before opening these notebooks so the ignored output files
exist locally:

```bash
python -m exponential_random_orchestra.main
```

The notebooks are intentionally read-only with respect to generated outputs.
They load artifacts from `exponential_random_orchestra/output/` and build
figures in memory.

- `01_preset_output_exploration.ipynb` compares the six preset clips, their
  metric distributions, and their MIDI note content.
- `02_phase_diagram_exploration.ipynb` studies the social-coupling/temperature
  sweep and locates regions that balance entropy and consonance.

