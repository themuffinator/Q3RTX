# AGENTS.md

This file defines how to work in this repository.

## Project Context

Q3RTX starts from unmodified Quake3e and aims to add a fully ray-traced renderer inspired by NVIDIA Quake II RTX architecture and development style.

Treat this as an engine evolution project:

* keep baseline behavior stable
* ship in phases
* avoid large unreviewable changes

## Repository Map

Core engine and game code:

* `code/client` - client lifecycle, renderer init, front-end orchestration
* `code/server` - server runtime
* `code/qcommon` - shared engine systems
* `code/game`, `code/cgame`, `code/ui` - VM/gameplay layers

Renderers:

* `code/renderer` - legacy OpenGL renderer
* `code/renderer2` - alternate modernized OpenGL path
* `code/renderervk` - Vulkan renderer
* `code/rendererrtx` - ray-tracing/PBR development renderer (active work target)
* `code/renderercommon` - shared renderer code/utilities
* `code/renderercommon/vulkan` - bundled Vulkan headers

Build and docs:

* `BUILD.md` - canonical build instructions
* `meson.build` / `meson_options.txt` - primary modern build entry points (Windows/Linux/macOS)
* `scripts/vcxproj_sources.py` - source list extraction used by Meson setup
* `CMakeLists.txt`, `Makefile` - build config entry points
* `doc/legacy` - historical docs, useful for behavior references

## First Files to Read for Renderer Work

1. `README.md` (project goals and milestones)
2. `BUILD.md` (build flags, renderer selection)
3. `code/client/cl_main.c` (renderer load/init flow such as `CL_InitRef`)
4. `code/rendererrtx/*` and `code/renderercommon/*` (active renderer + shared patterns)

## Hard Rule: Renderer Ownership

* `code/renderervk` is baseline reference and must remain untouched for RT/PBR feature work.
* All new ray-tracing and physically based rendering implementation work must go into `code/rendererrtx`.
* Changes outside `code/rendererrtx` must be minimal and only for required integration plumbing.
* If a change can be isolated to `code/rendererrtx`, do not modify other directories.
* `rendererrtx` must ship as its own renderer module binary (`q3rtx_rtx_<arch>`), selectable with `\cl_renderer rtx`.

## Quake II RTX-Inspired Direction

Use Q2RTX as architectural inspiration for:

* full-scene ray tracing instead of raster lighting hacks
* physically based material interpretation
* emissive/dynamic lights integrated into ray-traced shading
* temporal accumulation and denoising for real-time results
* explicit GPU resource lifetime and clear frame graph/pass ownership

Do not directly copy code across projects without validating license/compatibility implications.

## Implementation Guardrails

* Prefer isolated changes to a dedicated ray-tracing renderer path.
* Avoid regressions in `renderer`, `renderer2`, and existing `renderervk` behavior.
* Keep non-`rendererrtx` edits narrowly scoped to interfaces, build wiring, or bug fixes required for integration.
* Keep shared-header edits minimal and justified.
* Add debug cvars/logging where they unblock bring-up, then trim noisy output.
* Land vertical slices: compile -> render -> validate, before broad refactors.

## Suggested Work Sequence

1. Baseline capture
   Build and run current engine; capture reference screenshots/perf on fixed maps.
2. Renderer bootstrap
   Add new renderer module plumbing, runtime selection, init/shutdown, and swapchain/frame loop.
3. Geometry ingestion
   Convert world/model data into RT-friendly buffers and acceleration structures.
4. Lighting/material MVP
   Implement first bounce + direct lights with a minimal PBR material model.
5. Denoise/accumulate
   Add temporal history, motion-aware accumulation, and denoiser integration.
6. Compatibility/perf
   Address visual parity gaps, optimize update paths, and document cvars.

## Validation Checklist for Each PR

* Builds cleanly on at least one primary target platform.
* Renderer selection still works (`\cl_renderer` or static default path).
* No startup regression when loading standard Quake III content.
* New cvars/features are documented.
* Visual or performance claims include reproducible test context.

## Working Style

* Keep patches narrow and reviewable.
* Prefer explicit assumptions and measurable outcomes.
* When blocked, document current behavior, expected behavior, and evidence from logs or captures.
