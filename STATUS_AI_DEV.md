# Status note: AI related PyMoDAQ dev (startup context)

Written 2026-10-09 for the Project "PyMoDAQ and better agents coding". Not part of the template: do not commit it
or include it in a PR.

## Goal

Make PyMoDAQ efficient for AI-assisted development: help assistants propose PyMoDAQ, and write correct plugins,
Dashboard extensions (`CustomExt`) and standalone apps (`CustomApp`). Highest priority: plugins. The full plan
(sections: plugins P1-P7, extensions E1-E5, standalone apps A1-A4, cross-cutting C1-C6, contribution policy, roadmap
in 4 phases with 3 gates) is the exported document "AI related pymodaq dev".

## Decisions taken (by the maintainer)

1. **Instruments => `CustomExt`.** An application that drives instruments must be a Dashboard extension, because it
   relies on the Dashboard's stable mechanisms for instruments. `CustomApp` only when no instrument is needed.
2. **The word "preset" is obsolete.** The Dashboard is used through the **experiment manager** (the experiment = the
   list of instruments the Dashboard manages and controls) and the **state manager** (the state = mostly the instruments'
   settings values and the Dashboard's actuator values). Extensions must use the managers obtained from their
   `dashboard` argument (`self.experiment_manager`, `self.state_manager`), never their own.
3. **Configuration** is read through `GlobalConfig` (`pymodaq_utils.config`), a singleton wrapping all packages'
   `Config` objects. Instantiating a `Config` class directly is deprecated.
4. **`ModulesManager`** is recreated for each extension (base class `__init__`) so that each extension can handle
   different instruments. Never share it.
5. **Deprecated hooks:** `setup_docks` and `setup_menu`; use `setup_docks_and_widgets` and `setup_menus_and_toolbars`.
6. **Install workflow:** PyMoDAQ packages (`pymodaq_utils`, `pymodaq_data`, `pymodaq_gui`, `pymodaq`) in editable
   mode with `python install-packages.py -d` at the root of the PyMoDAQ repository; plugins with `pip install -e .`.
7. **Plugin extensions** differ from core extensions only by `EXTENSION_NAME` and `CLASS_NAME`. Reference `main()`:
   `load_dashboard_with_arguments(show_dashboard=False, load_extension=False)` then
   `create_extension(dashboard, Class, show_extension=True)` (no extra `win_ext.show()`). `_quit_fun` must return `True`.

## State of the branch `ai-dev/agents-md` (from `origin/5.3.x`, nothing pushed)

| Commit | Content |
| --- | --- |
| `252baba` | `AGENTS.md` first draft |
| `a14343b` | `AGENTS.md`: GlobalConfig, per-extension ModulesManager, non-deprecated hooks |
| `ab49df6` | App and extension templates updated to the current patterns |
| `3c9e2d6` | `AGENTS.md`: extension patterns (`main()`, `_quit_fun`, `ExtensionWorker`), Config registration |
| `690d394` | (maintainer) P2 start: `_epsilons`, README target version, `pyproject.toml` floors and Python versions |

Uncommitted: `pyproject.toml` floors corrected to `pymodaq>=5.3.1`, `pymodaq_utils>=5.3.1`, `pymodaq_gui>=5.3.0`,
`pymodaq_data>=5.3.0` (PyPI only has gui and data up to 5.3.0, so `>=5.3.1` for them cannot install). This file
(`STATUS_AI_DEV.md`) is untracked.

## Not verified yet

- **Nothing has been run.** `check_plugin`, `pytest` and the two updated templates were only syntax-checked. An isolated
  venv install of PyMoDAQ 5.3.1 was interrupted twice; the checks should be run in an environment with PyMoDAQ 5.3.1.
- The registered `GlobalConfig` key of a plugin's `Config` (package name without `pymodaq_plugins_`) was derived from
  reading `GlobalConfig.register`, not run.
- `AGENTS.md` statements to confirm: mandatory actuator methods (the template test's longer list was used), exact
  behaviour of `do_things_after_experiment_set`.

## Findings worth acting on

- The mock plugin (`pymodaq_plugins_mock`) still uses `_epsilon`, which `check_plugin` flags (PMQ302).
- Core extensions disagree on `main()`: `sequencer` and `ramping` also call `win_ext.show()`; `daq_scan` and `data_mixer` do not.
- About 100 "preset" occurrences remain in PyMoDAQ code and docs (plan item C4b: check and clean).
- No `llms.txt` on the docs hosts (404). Docs sample for `CustomApp` references undefined methods.
- Template CI `compatibility.yml` still lists Python 3.9; workflows appear managed by an updater.
- `check_plugin` already flags `stage_names`, `_epsilon`, `data_actuator_type`, unknown units (P5 is partly done).

## Next steps

1. Commit the `pyproject.toml` floor fix; run `check_plugin` and `pytest` with PyMoDAQ 5.3.1 and fix what shows up.
2. Finish P2: default branch on GitHub to track 5.3.x (a repository setting, maintainer's).
3. P3: one definition of the plugin contract (mandatory methods) shared by checks, template test and docs.
4. E1/E1b: fix extension docs and write the workflow/pattern page with diagrams; align core `main()` patterns.
5. P4: plugin cookbook with mock controllers; E2: small reference extension.
6. Later phases: `llms.txt`, docstrings and typing on the public API, "preset" cleanup, contribution policy.
