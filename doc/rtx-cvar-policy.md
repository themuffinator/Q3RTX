# Q3RTX Cvar Policy (`rtx_*`)

Last updated: 2026-02-13
Scope: new ray tracing and PBR controls owned by `code/rendererrtx`.

## Goals

- Keep legacy renderer behavior stable.
- Make RT controls discoverable and consistent.
- Avoid ad-hoc names that become compatibility debt.

## Namespace Rules

- All new rendererrtx-specific controls use the `rtx_` prefix.
- Do not repurpose existing `r_*` cvars for new RT/PBR behavior.
- Existing `r_*` cvars remain compatibility controls and keep current semantics.

## Naming Convention

- Base format: `rtx_<domain>_<name>`.
- Use singular, descriptive domains:
  - `rtx_rt_*` for ray tracing/path settings.
  - `rtx_as_*` for acceleration-structure build/update controls.
  - `rtx_denoise_*` for temporal/spatial denoise controls.
  - `rtx_post_*` for tone mapping and post-processing.
  - `rtx_debug_*` for visualization and diagnostics.

## Defaults and Flags

- Shipping defaults must be safe to start and visually stable.
- Use `CVAR_ARCHIVE` for user-tunable quality settings.
- Use `CVAR_LATCH` only when the change requires expensive re-init (pipeline/swapchain/resources).
- Use `CVAR_CHEAT` and/or `CVAR_TEMP` for debug-only toggles.
- Experimental toggles default to conservative values (usually `0`/off).

## Ranges and Descriptions

- Every numeric `rtx_*` cvar must define range checks with `Cvar_CheckRange`.
- Every new cvar must include `Cvar_SetDescription` text with:
  - what it controls,
  - expected range/values,
  - restart/reload requirements if applicable.

## Logging and Grouping

- Startup diagnostics should identify active `rtx_*` values that gate renderer behavior.
- Keep noisy per-frame debug logging disabled by default.
- Group renderer-owned cvars with existing renderer grouping conventions when applicable.

## Documentation and Review Requirements

- Each new `rtx_*` cvar must be documented in the PR description.
- User-facing cvars must also be added to the future `doc/rtx-cvars.md`.
- Any deviation from this policy requires a short justification in code review.
