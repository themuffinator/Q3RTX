# Q3RTX `rendererrtx` Architecture Overview

Last updated: 2026-02-15  
Scope: module boundaries, frame lifecycle, and RT data flow for developers working on `code/rendererrtx`.

## Design goals

1. Keep legacy renderers (`renderer`, `renderer2`, `renderervk`) stable.
2. Isolate RT/PBR implementation in `rendererrtx`.
3. Maintain explicit frame/pass ownership and resource lifetime.
4. Ship in incremental milestones with measurable bring-up gates.

## Runtime module boundaries

| Layer | Responsibility | Primary files |
|---|---|---|
| Engine loader | Select and load renderer module; resolve `GetRefAPI` | `code/client/cl_main.c`, `code/qcommon/files.c` |
| Renderer front-end | `refexport_t` integration, cvars, scene submission | `code/rendererrtx/tr_init.c`, `code/rendererrtx/tr_scene.c` |
| Backend orchestration | Frame pass ordering, draw command dispatch | `code/rendererrtx/tr_backend.c` |
| Vulkan RT backend | Swapchain, descriptors, AS/TLAS, SBT, dispatch, post stack | `code/rendererrtx/vk.c`, `code/rendererrtx/vk.h` |
| Shaders | raygen/miss/hit and post logic | `code/rendererrtx/shaders/*` |

## High-level data flow

```text
Client frame
  -> CL_InitRef / RE_* entrypoints
  -> tr_backend command stream
  -> vk_begin_frame
      -> world + dynamic geometry extraction
      -> BLAS/TLAS update/build
      -> light/material buffer upload
      -> vkCmdTraceRaysKHR dispatch
      -> temporal/spatial resolve
      -> bloom/gamma/UI composition
  -> vk_end_frame / present
```

## Pass graph lifecycle

Frame graph tracking in `tr_backend.c` enforces pass ordering and lifecycle diagnostics (`rtx_debug_framegraph`):

1. `draw_buffer`
2. `clear_color`
3. `clear_depth`
4. `draw_surfs`
5. `rt_trace`
6. `ui_2d`
7. `finish_bloom`
8. `swap_buffers`

## RT pipeline stages

1. Capability and mode gating
   - `rtx_rt_mode` + `rtx_rt_require` decide fallback vs strict-fail behavior.
2. Geometry ingestion
   - world: `vk_rt_extract_world_geometry`
   - dynamic entities/effects: `vk_rt_extract_dynamic_geometry`
3. Acceleration structures
   - dynamic BLAS path: `vk_rt_build_dynamic_scene_blas`
   - TLAS rebuild/update: `vk_rt_build_tlas`
4. Lighting/material upload
   - `vk_rt_update_light_buffer` and material translation/override paths.
5. Ray dispatch and resolve
   - `vk_rt_trace_frame` handles trace, temporal accumulation, denoise, and output resolve.
6. Post/composition
   - bloom and gamma passes plus UI/HUD overlay compatibility path.

## Resource lifetime model

`vk.c` tracks resource ownership across init, resize, frame use, and shutdown, with optional diagnostics:

1. Init path allocates descriptor/pipeline/state objects.
2. Resize path recreates swapchain-dependent images/framebuffers.
3. Per-frame path records command buffers and fences/semaphores.
4. Shutdown path tears down RT and Vulkan objects in dependency-safe order.

Key controls:

- `rtx_debug_resource_lifetime`
- `rtx_debug_gpu_markers`
- `rtx_debug_vk_validation`

## Key integration invariants

1. Loader invariant
   - renderer module must be discoverable by `FS_LoadLibrary` probe order.
2. Capability invariant
   - unsupported RT capabilities must either fall back or fail with actionable diagnostics.
3. Composition invariant
   - UI and console remain correct on top of RT output (`rtx_rt_ui_passthrough` path for UI-only views).
4. Regression invariant
   - non-RT renderers remain bootable (`opengl`, `opengl2`, `vulkan`).

## Observability and debugging

1. `vkinfo` for runtime capability and Vulkan device report.
2. `rtx_rt_debug_visualizer` for RT debug views.
3. `rtx_rt_perf_timing` + `rtx_rt_perf_interval` for periodic perf reporting.
4. Startup loader diagnostics from `FS_LoadLibraryDiagnostics` on module load failure.
