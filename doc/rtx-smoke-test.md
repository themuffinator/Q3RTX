# `rendererrtx` Bring-Up Smoke Test

Last updated: 2026-02-13
Scope: fast startup validation for `\cl_renderer rtx`.

## Preconditions

- Build artifacts exist for client + RT module:
  - Windows: `q3rtx.x64.exe` and `q3rtx_rtx_x86_64.dll`
  - Linux: `q3rtx` and `q3rtx_rtx_x86_64.so`
  - macOS: `q3rtx` and `q3rtx_rtx_<arch>.dylib`
- Valid Quake III game data is present (`baseq3`).
- Test from a clean config or known baseline config.

## Startup Steps

1. Launch with console enabled and renderer selection:
   - Example: `+set developer 1 +set cl_renderer rtx`
2. Confirm startup logs include renderer diagnostics:
   - `CL_InitRef: cl_renderer is "rtx"`
   - `CL_InitRef: attempting renderer module ...`
   - `CL_InitRef: loaded renderer module from ...`
3. Run `vid_restart` once and confirm renderer reinitializes without fatal errors.
4. Load a baseline map (`map q3dm1` recommended) and wait for first playable frame.
5. Open console and run `gfxinfo`; confirm renderer reports `rendererrtx` module strings.

## Pass Criteria

- Renderer module loads through `GetRefAPI`.
- No startup crash/hang.
- Main menu and in-map rendering both appear.
- `vid_restart` path is stable.
- `cl_renderer` remains `rtx` after restart.

## Quick Negative Tests

1. Set invalid renderer name, then `vid_restart`:
   - `seta cl_renderer not_a_renderer`
2. Confirm fallback behavior:
   - reset/fallback occurs without crashing,
   - diagnostics show attempted module names.
3. Restore:
   - `seta cl_renderer rtx`
   - `vid_restart`

## Capture Requirements

- Save a short console log snippet for each smoke run:
  - platform/build type,
  - selected renderer value,
  - module attempt/success diagnostics,
  - map loaded and result.
