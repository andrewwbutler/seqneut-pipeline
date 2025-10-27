#!/usr/bin/env python
"""Run a marimo notebook with snakemake parameters.

This script allows marimo notebooks to be executed by Snakemake with
parameters injected similarly to how Jupyter notebooks receive them via papermill.
"""

import json
import sys
from types import SimpleNamespace


def create_snakemake_object(config_file):
    """Create a snakemake-like object from a JSON config file."""
    with open(config_file) as f:
        config = json.load(f)

    snakemake = SimpleNamespace()

    # Convert nested dicts to SimpleNamespace recursively
    def dict_to_namespace(d):
        if isinstance(d, dict):
            return SimpleNamespace(**{k: dict_to_namespace(v) for k, v in d.items()})
        elif isinstance(d, list):
            return [dict_to_namespace(item) for item in d]
        else:
            return d

    snakemake.input = dict_to_namespace(config.get("input", {}))
    snakemake.output = dict_to_namespace(config.get("output", {}))
    snakemake.params = dict_to_namespace(config.get("params", {}))
    snakemake.log = dict_to_namespace(config.get("log", {}))

    return snakemake


def main():
    """Main entry point."""
    if len(sys.argv) != 3:
        print("Usage: run_marimo_notebook.py <notebook.py> <config.json>")
        sys.exit(1)

    notebook_path = sys.argv[1]
    config_file = sys.argv[2]

    # Create snakemake object
    snakemake = create_snakemake_object(config_file)

    # Read and execute the marimo notebook as a Python script
    # We inject the snakemake object into globals before execution
    with open(notebook_path) as f:
        notebook_code = f.read()

    # Create execution environment
    exec_globals = {"snakemake": snakemake, "__name__": "__main__"}

    # Execute the notebook
    exec(notebook_code, exec_globals)


if __name__ == "__main__":
    main()
