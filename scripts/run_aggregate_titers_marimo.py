"""Snakemake wrapper script to run aggregate_titers marimo notebook.

This script is called by Snakemake and creates a JSON config file
with the snakemake object contents, then executes the marimo notebook.
"""

import json
import subprocess
import sys
from pathlib import Path


def prepare_snakemake_config(snakemake, config_path):
    """Prepare a JSON config file with snakemake parameters."""
    config = {
        "input": {
            "pickles": snakemake.input.pickles,
            "titers": snakemake.input.titers,
        },
        "output": {
            "pickles": snakemake.output.pickles,
            "titers": snakemake.output.titers,
            "titers_chart": snakemake.output.titers_chart,
        },
        "params": {
            "viral_strain_plot_order": snakemake.params.viral_strain_plot_order,
            "groups_sera": snakemake.params.groups_sera,
            "groups": snakemake.params.groups,
        },
        "log": {},
    }

    # Write config to file
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)

    return config_path


def main(snakemake):
    """Main entry point called by Snakemake."""
    # Ensure output directory exists
    output_dir = Path(snakemake.output.titers_chart).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    # Prepare config file
    config_path = snakemake.output.config
    prepare_snakemake_config(snakemake, config_path)

    # Get path to marimo notebook and runner script
    pipeline_dir = Path(__file__).parent.parent
    notebook_path = pipeline_dir / "notebooks" / "aggregate_titers_marimo.py"
    runner_path = pipeline_dir / "scripts" / "run_marimo_notebook.py"

    # Run the marimo notebook
    cmd = [sys.executable, str(runner_path), str(notebook_path), config_path]

    print(f"Running marimo notebook: {' '.join(cmd)}")
    with open(snakemake.log[0], "w") as log_file:
        result = subprocess.run(
            cmd,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            text=True,
        )

    if result.returncode != 0:
        print(f"Error running marimo notebook. Check log: {snakemake.log[0]}")
        sys.exit(result.returncode)

    print("Marimo notebook executed successfully")


# Snakemake wrapper scripts expect this pattern
if __name__ == "__main__":
    main(snakemake)
