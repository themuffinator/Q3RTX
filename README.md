# Q3RTX

Q3RTX aims to build a fully ray-traced renderer for Quake III Arena content, inspired by the overall approach of NVIDIA Quake II RTX while staying compatible with Quake III-era gameplay and content workflows.

Current state: this repository starts from unmodified Quake3e source as the baseline.

## Vision

Create a modern rendering path that replaces legacy raster lighting with physically based, ray-traced lighting while preserving engine stability and mod compatibility.

## Primary Goals

* Deliver a fully ray-traced real-time renderer for Quake III maps, models, effects, and dynamic entities.
* Support physically based materials and emissive lighting behavior suitable for path-traced shading.
* Preserve Quake3e gameplay, networking, VM behavior, and asset loading expectations.
* Keep existing renderers functional during transition (`renderer`, `renderer2`, `renderervk`) to avoid blocking development.
* Develop RT/PBR features in `code/rendererrtx` while keeping `code/renderervk` as untouched baseline.
* Build incrementally with measurable visual and performance checkpoints.

## Non-Goals (for now)

* Rewriting game logic, UI, bot AI, or networking subsystems.
* Breaking compatibility with existing Quake III data layouts as a prerequisite.
* One-shot "big bang" renderer replacement without transition milestones.

## Technical Direction

* Add a dedicated ray-tracing renderer path (expected as a new renderer module) rather than destabilizing legacy paths.
* Reuse shared engine infrastructure where it makes sense (`code/renderercommon`, client registration flow, resource management patterns).
* Start from Vulkan-first ray tracing architecture and keep OpenGL paths unaffected.
* Introduce translation layers from Quake III shader/lightmap-era content toward physically based material/light inputs.
* Use temporal accumulation + denoising as required for practical real-time path tracing.

## Milestones

1. Baseline and Instrumentation  
   Confirm clean Quake3e baseline builds and produce representative test captures/maps.
2. Renderer Skeleton  
   Add a loadable ray-tracing renderer module, cvars, init/shutdown flow, and basic frame orchestration.
3. Geometry and Acceleration Structures  
   Build BLAS/TLAS pipelines for world geometry, brush models, MD3, sprites, and particles.
4. Ray-Traced Lighting
   Implement direct + indirect lighting, shadows, emissive sources, and physically based BRDF evaluation.
5. Accumulation, Denoising, and Tone Mapping
   Add temporal reprojection, denoiser integration, and HDR output controls.
6. Content Compatibility and Optimization
   Improve shader/script translation, reduce visual mismatches, and optimize GPU/CPU cost.

Detailed, task-level tracker: `doc/rtx-renderer-implementation-plan.md`

## Build

Primary build system is Meson + Ninja with cross-platform support for Windows, Linux, and macOS.

### Windows (VS 2022 + Ninja)

Run from a Visual Studio Developer Command Prompt (`x64 Native Tools`) or call `VsDevCmd.bat` first.

Release:

```bat
meson setup build/meson-release --wipe --buildtype=release
meson compile -C build/meson-release
```

Debug:

```bat
meson setup build/meson-debug --wipe --buildtype=debug
meson compile -C build/meson-debug
```

Output binaries:

* `build/meson-release/q3rtx.x64.exe`
* `build/meson-debug/q3rtx.x64.exe`
* `build/meson-release/q3rtx_rtx_x86_64.dll`
* `build/meson-debug/q3rtx_rtx_x86_64.dll`

### Linux (GCC/Clang + Ninja)

Install build dependencies (`meson`, `ninja`, `python3`, `sdl2`, and optional `libcurl`).

Release:

```bash
meson setup build/meson-release --wipe --buildtype=release
meson compile -C build/meson-release
```

Debug:

```bash
meson setup build/meson-debug --wipe --buildtype=debug
meson compile -C build/meson-debug
```

Output binaries:

* `build/meson-release/q3rtx`
* `build/meson-debug/q3rtx`
* `build/meson-release/q3rtx_rtx_x86_64.so` (x86_64 host)
* `build/meson-debug/q3rtx_rtx_x86_64.so` (x86_64 host)

### macOS (Clang + Ninja)

Install build dependencies (`meson`, `ninja`, `python3`, `sdl2`, and optional `curl` via Homebrew or system packages).

Release:

```bash
meson setup build/meson-release --wipe --buildtype=release
meson compile -C build/meson-release
```

Debug:

```bash
meson setup build/meson-debug --wipe --buildtype=debug
meson compile -C build/meson-debug
```

Output binaries:

* `build/meson-release/q3rtx`
* `build/meson-debug/q3rtx`
* `build/meson-debug/q3rtx_rtx_x86_64.dylib` or `build/meson-release/q3rtx_rtx_x86_64.dylib` (Intel host)
* `build/meson-debug/q3rtx_rtx_aarch64.dylib` or `build/meson-release/q3rtx_rtx_aarch64.dylib` (Apple Silicon host)

Notes:

* This Meson setup targets the Vulkan/RT development flow and does not build GL renderer modules.
* `code/renderervk` remains baseline; active RT/PBR development target is `code/rendererrtx`.
* `rendererrtx` is built as a separate renderer module and is selected with `\cl_renderer rtx`.
* Runtime still requires Quake III game data (`baseq3`) outside this repository.
* Legacy instructions remain in `BUILD.md` for reference.

## Inspiration and References

* NVIDIA Quake II RTX: https://github.com/NVIDIA/Q2RTX
* Quake3e baseline engine: https://github.com/ec-/Quake3e

The goal is architectural inspiration and feature parity direction, not a direct port.
