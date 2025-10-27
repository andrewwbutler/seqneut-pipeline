# Marimo Notebooks in seqneut-pipeline

This document describes the initial integration of [marimo](https://marimo.io/) notebooks into the seqneut-pipeline.

## What is Marimo?

Marimo is a reactive Python notebook that:
- Stores notebooks as pure Python files (easy to version control)
- Automatically tracks dependencies between cells and re-runs them reactively
- Can be executed as scripts or run as interactive web apps
- Provides a more maintainable alternative to Jupyter notebooks

## Current Status

### Converted Notebooks

- `notebooks/aggregate_titers_marimo.py` - Marimo version of `aggregate_titers.py.ipynb`

### How to Run

The marimo notebook can be executed via Snakemake:

```bash
snakemake --snakefile your_Snakefile aggregate_titers_marimo
```

This rule:
1. Creates a JSON config file with Snakemake inputs, outputs, and params
2. Executes the marimo notebook with the injected `snakemake` object
3. Produces the same outputs as the Jupyter version in `results/aggregated_titers_marimo/`

### Running Interactively

To develop or explore the marimo notebook interactively:

```bash
marimo edit notebooks/aggregate_titers_marimo.py
```

Note: When running interactively, you'll need to manually provide the `snakemake` object or modify the notebook to use sample data.

## Architecture

The integration uses several components:

1. **`scripts/run_marimo_notebook.py`** - Generic runner that:
   - Reads a JSON config file
   - Creates a `snakemake` object from the config
   - Executes the marimo notebook with the injected object

2. **`scripts/run_aggregate_titers_marimo.py`** - Snakemake wrapper script that:
   - Receives the `snakemake` object from Snakemake
   - Serializes it to JSON
   - Calls the generic marimo runner

3. **`aggregate_titers_marimo` rule** - Snakemake rule that:
   - Defines inputs, outputs, and parameters
   - Calls the wrapper script
   - Produces outputs in a separate directory to avoid conflicts

## Conversion Process

The notebook was converted using:

```bash
marimo convert notebooks/aggregate_titers.py.ipynb -o notebooks/aggregate_titers_marimo.py
```

After conversion, minor fixes were applied:
- Fixed variable naming issue with `viral_strain_plot_order`
- Adjusted code structure for better reactivity

## Limitations and Future Work

### Current Limitations

1. **Parallel execution**: Currently only `aggregate_titers` has a marimo version
2. **Interactive development**: The `snakemake` object isn't available when editing interactively
3. **HTML export**: The marimo notebook doesn't automatically export to HTML like Jupyter notebooks do

### Future Improvements

1. **Convert remaining notebooks**:
   - `process_plate.py.ipynb`
   - `group_serum_titers.py.ipynb`
   - `aggregate_qc_drops.py.ipynb`

2. **Better interactive development**:
   - Add mock `snakemake` objects for development
   - Create development mode with sample data

3. **HTML export integration**:
   - Add marimo HTML export to the pipeline
   - Integrate marimo outputs into the docs system

4. **Replace Jupyter entirely** (optional):
   - Once all notebooks are converted and tested
   - Update documentation to use marimo
   - Remove Jupyter dependencies

## Benefits of Marimo

1. **Version control**: Notebooks are plain Python files, easier to diff and review
2. **No hidden state**: Reactive execution prevents common notebook pitfalls
3. **Maintainability**: Pure Python format makes it easier to refactor and test
4. **Reproducibility**: Guaranteed execution order based on dependencies

## Development Workflow

### Converting a New Notebook

1. Convert the Jupyter notebook:
   ```bash
   marimo convert notebooks/YOUR_NOTEBOOK.ipynb -o notebooks/YOUR_NOTEBOOK_marimo.py
   ```

2. Fix any conversion issues (variable names, etc.)

3. Create a Snakemake wrapper script in `scripts/run_YOUR_NOTEBOOK_marimo.py`

4. Add a new rule in `seqneut-pipeline.smk`

5. Test the conversion

### Testing

Test the marimo notebook by running its Snakemake rule and comparing outputs to the Jupyter version.

## Questions or Issues?

For questions about marimo integration, please open an issue on the repository.

For marimo-specific documentation, see: https://docs.marimo.io/
