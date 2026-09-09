# Repository Guide

## Environment and Commands

- Use Python 3.11 for development; `.python-version`, both Conda environments, and release CI agree on it. `setup.py` permits Python 3.9+ for package consumers.
- `conda env create` creates the editable `oranchada` environment from `environment.yml`; `conda env create -f environment-dev.yml` instead installs ramanchada2 from its Git repository.
- For an existing environment, install this package with `pip install -e .`. Run the add-on with `orange-canvas`, and restart Orange after source changes because widgets are not hot-reloaded.
- Release CI only builds the distribution: install `build`, then run `python -m build`. Publishing is triggered by a published GitHub release.
- No working automated test, typecheck, or pre-commit workflow is configured. The lone `src/orangecontrib/oranchada/tests/process_spectra_test.py` is stale, is not named for default `unittest` discovery, and does not match the current widget API.
- `.flake8` sets a 120-character line limit and ignores `F401`/`F403` in `__init__.py`, but flake8 is not installed by the repository environments or run in CI.

## Package Architecture

- This is one setuptools `src`-layout Orange add-on. `setup.py` is the source of truth for the version, dependencies, and Orange entry points.
- Orange discovers the `Oranchada Easy` and `Oranchada Pro` categories from `widgets_easy/` and `widgets_pro/`; widget modules define their displayed metadata and Orange `Inputs`/`Outputs`.
- `base_widget/` supplies the shared GUI/process/plot flow. Most processing widgets exchange `RC2Spectra`, the list-like signal type in `base_widget/types.py`, rather than an Orange `Table`; `BaseWidget` optionally converts outputs to a table.
- `processings/` contains callable processing controls bound to parent widget settings, not an independent processing service layer.
- The Ploomber YAML, environment templates, and task scripts under `widgets_easy/ploomber/` are loaded at runtime via paths relative to widget modules. Keep widget changes, pipeline parameters, and these resources synchronized.

## Packaging and Verification

- `MANIFEST.in` includes widget PNG/SVG assets and grafts `widgets_easy/ploomber/`; update it when adding a new runtime resource type or location.
- `dist/`, `build/`, package metadata, caches, and `*.log` files are generated/ignored artifacts, not source files.
- For widget behavior changes, perform a focused GUI check in `orange-canvas`; only a handful of modules contain standalone `WidgetPreview` launchers. State explicitly when GUI verification was not possible.
