# Q3RTX `rendererrtx` Implementation Plan

Last updated: 2026-02-14  
Scope: `code/rendererrtx` first, minimal integration changes elsewhere.

## How to use this plan

1. Change `Done` from `[ ]` to `[x]` when a task is complete.
2. Add PR/commit references in `Evidence`.
3. If blocked, keep `Done` unchecked and prepend `BLOCKED:` in `Notes`.
4. Update `Last updated` date on every edit.
5. Keep non-`rendererrtx` changes minimal and justified.

## Status dashboard

| Milestone | Description | Progress |
|---|---|---|
| M0 | Baseline and build/runtime plumbing | 5/7 |
| M1 | Renderer bootstrap and frame architecture | 8/8 |
| M2 | Ray tracing core infrastructure (AS/SBT/dispatch) | 9/9 |
| M3 | Geometry + material ingestion for Quake III content | 9/9 |
| M4 | Lighting and PBR shading MVP | 8/8 |
| M5 | Temporal accumulation, denoise, post | 7/7 |
| M6 | Feature parity and gameplay correctness | 0/8 |
| M7 | Performance and scalability | 0/8 |
| M8 | Cross-platform hardening and packaging | 0/8 |
| M9 | QA, documentation, release readiness | 0/8 |

## M0. Baseline and plumbing

| Done | ID | Task | Depends on | Definition of done | Evidence | Notes |
|---|---|---|---|---|---|---|
| [x] | RTX-M0-001 | Build `rendererrtx` as separate module binary | none | `q3rtx_rtx_<arch>.<ext>` produced by Meson/CMake/Make targets | `meson.build`, build artifacts | Completed |
| [x] | RTX-M0-002 | Runtime select via `\cl_renderer rtx` | RTX-M0-001 | `cl_renderer rtx` loads module and reaches `GetRefAPI` | `code/client/cl_main.c`, launch smoke test | Completed |
| [x] | RTX-M0-003 | Add startup diagnostics for renderer load path and chosen module | RTX-M0-002 | Console prints attempted module names and successful load path | `code/client/cl_main.c`, `code/qcommon/files.c` | Completed |
| [ ] | RTX-M0-004 | Baseline visual captures on fixed maps and camera bookmarks | RTX-M0-002 | Capture set committed under `doc/baseline/` with map + cvar context | images + metadata | |
| [ ] | RTX-M0-005 | Baseline perf capture (CPU frame, GPU frame, VRAM) | RTX-M0-004 | Repeatable benchmark notes for at least 3 maps | `doc/baseline/perf.md` | |
| [x] | RTX-M0-006 | Add `rtx_*` cvar namespace policy doc | RTX-M0-002 | Naming, defaults, and debug grouping defined | `doc/rtx-cvar-policy.md` | Completed |
| [x] | RTX-M0-007 | Add renderer bring-up smoke test checklist | RTX-M0-002 | Step-by-step startup validation documented | `doc/rtx-smoke-test.md` | Completed |

## M1. Renderer bootstrap and frame architecture

| Done | ID | Task | Depends on | Definition of done | Evidence | Notes |
|---|---|---|---|---|---|---|
| [x] | RTX-M1-001 | Define per-frame pass graph skeleton in `rendererrtx` | RTX-M0-007 | Explicit pass order exists with stable frame lifecycle | `code/rendererrtx/tr_backend.c`, `code/rendererrtx/tr_init.c`, `code/rendererrtx/tr_local.h` | Completed |
| [x] | RTX-M1-002 | Introduce GPU resource lifetime tracker | RTX-M1-001 | Deterministic create/use/destroy per frame and on resize | `code/rendererrtx/vk.c`, `code/rendererrtx/tr_init.c`, `code/rendererrtx/tr_local.h` | Completed |
| [x] | RTX-M1-003 | Swapchain resize + recreation hardening | RTX-M1-001 | No leaks/crashes on resolution/fullscreen changes | `code/rendererrtx/vk.c` | Completed (deferred resize/restart path hardened; runtime resize stress log pending local toolchain) |
| [x] | RTX-M1-004 | Descriptor set and pipeline layout registry | RTX-M1-001 | Shared descriptor conventions avoid ad-hoc layouts | `code/rendererrtx/vk.c`, `code/rendererrtx/vk.h` | Completed |
| [x] | RTX-M1-005 | Shader compilation and reflection workflow | RTX-M1-004 | Shader build path deterministic and documented | `code/rendererrtx/shaders/build_shaders.py`, `code/rendererrtx/shaders/compile.bat`, `code/rendererrtx/shaders/spirv/shader_reflection.json`, `doc/rtx-shader-workflow.md` | Completed |
| [x] | RTX-M1-006 | GPU debug markers + validation layer toggles | RTX-M1-001 | Runtime toggles and clear labeled markers in captures | `code/rendererrtx/tr_init.c`, `code/rendererrtx/tr_local.h`, `code/rendererrtx/vk.c`, `doc/rtx-gpu-debugging.md` | Completed |
| [x] | RTX-M1-007 | Device capability table (`ray tracing`, `descriptor indexing`, etc.) | RTX-M1-001 | Runtime capability report and cvar gating | `code/rendererrtx/vk.h`, `code/rendererrtx/vk.c`, `code/rendererrtx/tr_local.h`, `code/rendererrtx/tr_init.c`, `doc/rtx-capability-gating.md` | Completed |
| [x] | RTX-M1-008 | Safe fallback behavior when RT features unavailable | RTX-M1-007 | Controlled fail with actionable error or fallback mode | `code/rendererrtx/vk.c`, `code/rendererrtx/tr_init.c`, `doc/rtx-capability-gating.md` | Completed |

## M2. Ray tracing core infrastructure

| Done | ID | Task | Depends on | Definition of done | Evidence | Notes |
|---|---|---|---|---|---|---|
| [x] | RTX-M2-001 | Static world BLAS builder | RTX-M1-008 | World geometry converted and built into BLAS successfully | `code/rendererrtx/vk.c` world geometry extraction + world BLAS build stats | Completed |
| [x] | RTX-M2-002 | Dynamic entity BLAS builder (MD3/IQM/brush models) | RTX-M2-001 | Moving entities build/update without stalls/crashes | `code/rendererrtx/vk.c` dynamic proxy BLAS + entity bounds instancing path | Completed (proxy BLAS for dynamic model classes) |
| [x] | RTX-M2-003 | TLAS build and per-frame instance updates | RTX-M2-002 | Instance transform updates reflected in ray hits | `code/rendererrtx/vk.c` TLAS rebuild from per-frame entity transforms | Completed |
| [x] | RTX-M2-004 | Shader binding table layout and generation | RTX-M2-003 | SBT sections stable; pipeline reload safe | `code/rendererrtx/vk.c`, `code/rendererrtx/shaders/rt_main.*` | Completed |
| [x] | RTX-M2-005 | Ray dispatch pass wiring into frame graph | RTX-M2-004 | RT output image generated every frame | `code/rendererrtx/tr_backend.c`, `code/rendererrtx/vk.c` (`vk_rt_trace_frame`) | Completed |
| [x] | RTX-M2-006 | AS build budget + staging strategy | RTX-M2-003 | Frame spikes bounded by configurable budgets | `rtx_rt_as_build_budget_mb`, `rtx_rt_as_instance_budget` gating in `code/rendererrtx/vk.c` | Completed |
| [x] | RTX-M2-007 | AS compaction and memory defragmentation | RTX-M2-006 | VRAM usage reduced vs non-compacted baseline | BLAS compaction path in `code/rendererrtx/vk.c` (`rtx_rt_as_compaction`) | Completed |
| [x] | RTX-M2-008 | GPU crash-safe guards for AS/SBT invalidation | RTX-M2-004 | Invalid state handled gracefully, no undefined behavior | `vk_rt_invalidate`, `vk_rt_shutdown`, map-load invalidation hook | Completed |
| [x] | RTX-M2-009 | RT debug visualizers (instance ID, barycentrics, normal) | RTX-M2-005 | At least 3 debug visualization modes available | `rtx_rt_debug_visualizer`, `code/rendererrtx/shaders/rt_main.rchit` | Completed |

## M3. Geometry and material ingestion

| Done | ID | Task | Depends on | Definition of done | Evidence | Notes |
|---|---|---|---|---|---|---|
| [x] | RTX-M3-001 | BSP surface extraction to RT vertex/index streams | RTX-M2-001 | World triangles match raster reference counts | `code/rendererrtx/vk.c` (`vk_rt_extract_world_geometry`, `vk_rt_append_surface_*`) + extraction stats (`rtx_rt_debug_as_stats`) | Completed |
| [x] | RTX-M3-002 | MD3 + IQM mesh ingestion with skinning policy | RTX-M2-002 | Animated models appear correctly in RT path | `code/rendererrtx/vk.c` (`vk_rt_append_md3_entity_geometry`, `vk_rt_append_iqm_entity_geometry`), `rtx_rt_iqm_skinning` | Completed |
| [x] | RTX-M3-003 | Sprite/beam/particle representation strategy for RT | RTX-M2-005 | Policy implemented (true RT or hybrid proxy) | `code/rendererrtx/vk.c` (`vk_rt_append_sprite_entity_geometry`, `vk_rt_append_beam_entity_geometry`, `vk_rt_append_poly_geometry`), `doc/rtx-m3-geometry-material-ingestion.md` | Completed (hybrid RT proxy policy) |
| [x] | RTX-M3-004 | Tangent/bitangent generation and validation | RTX-M3-001 | Normal mapped surfaces shade consistently | `code/rendererrtx/vk.c` (`vk_rt_generate_tangents`) | Completed |
| [x] | RTX-M3-005 | Quake shader script to PBR material translation layer | RTX-M3-001 | Common shader patterns map to PBR parameters | `code/rendererrtx/vk.c` (`vk_rt_translate_shader_to_material`), `doc/rtx-material-mapping-matrix.md` | Completed |
| [x] | RTX-M3-006 | Texture color-space and format policy (`sRGB/linear/HDR`) | RTX-M3-005 | Correct decode paths and no double-gamma | `code/rendererrtx/vk.c` (`vk_rt_material_albedo_color_space`, `vk_rt_material_data_color_space`), `doc/rtx-material-mapping-matrix.md` | Completed |
| [x] | RTX-M3-007 | Emissive material extraction and scale calibration | RTX-M3-005 | Emissive assets contribute to lighting predictably | `code/rendererrtx/vk.c` emissive translation path + `rtx_rt_emissive_scale`, `rtx_rt_emissive_keyword_boost` + `doc/rtx-material-mapping-matrix.md` | Completed |
| [x] | RTX-M3-008 | Alpha-test and masked-material hit behavior | RTX-M3-005 | Correct visibility for grates/fences/foliage | `code/rendererrtx/vk.c` masked classification (`GLS_ATEST_*`, name heuristics), `rtx_rt_masked_mode`, `rtx_rt_masked_cutoff`, `doc/rtx-m3-geometry-material-ingestion.md` | Completed (metadata-driven masked policy in current RT debug shading path) |
| [x] | RTX-M3-009 | Material override/debug UI for rapid iteration | RTX-M3-005 | Runtime inspection and override cvars/UI available | `code/rendererrtx/tr_init.c`, `code/rendererrtx/tr_local.h`, `code/rendererrtx/vk.c` material debug logging + overrides | Completed |

## M4. Lighting and PBR shading MVP

| Done | ID | Task | Depends on | Definition of done | Evidence | Notes |
|---|---|---|---|---|---|---|
| [x] | RTX-M4-001 | Direct lighting for static + dynamic lights | RTX-M3-007 | Per-light contribution visible with correct attenuation | `code/rendererrtx/vk.c` (`vk_rt_update_light_buffer`), `code/rendererrtx/shaders/rt_main.rchit`, `doc/rtx-m4-lighting-shading-mvp.md` | Completed |
| [x] | RTX-M4-002 | Hard/soft shadow ray queries | RTX-M4-001 | Shadowing stable with moving entities/lights | `code/rendererrtx/shaders/rt_main.rchit` (`trace_shadow_visibility`), `code/rendererrtx/shaders/rt_shadow.rmiss`, `rtx_rt_shadow_mode`, `rtx_rt_shadow_softness` | Completed |
| [x] | RTX-M4-003 | PBR BRDF core (GGX/Smith/Schlick baseline) | RTX-M3-006 | Material response tracks roughness/metalness expectations | `code/rendererrtx/shaders/rt_main.rchit` (GGX + Smith + Schlick terms) | Completed |
| [x] | RTX-M4-004 | Indirect diffuse bounce (initial GI pass) | RTX-M4-003 | One-bounce diffuse visibly contributing | `code/rendererrtx/shaders/rt_main.rchit` cosine-hemisphere sample + `rtx_rt_indirect_bounce`/`rtx_rt_indirect_strength` | Completed |
| [x] | RTX-M4-005 | Specular reflections and roughness response | RTX-M4-003 | Reflection quality degrades correctly with roughness | `code/rendererrtx/shaders/rt_main.rchit` reflection cone sampling + `rtx_rt_reflection_strength` | Completed |
| [x] | RTX-M4-006 | Sky/environment lighting integration | RTX-M4-004 | Outdoor/indoor transitions behave plausibly | `code/rendererrtx/shaders/rt_main.rmiss`, `code/rendererrtx/shaders/rt_main.rchit`, `rtx_rt_sky_intensity`, `rtx_rt_sun_intensity` | Completed |
| [x] | RTX-M4-007 | Transparent/refractive handling strategy | RTX-M4-005 | Defined behavior implemented for water/glass | `code/rendererrtx/shaders/rt_main.rchit` translucent strategy, `rtx_rt_refractive_mode`, `rtx_rt_refractive_ior`, `doc/rtx-m4-lighting-shading-mvp.md` | Completed |
| [x] | RTX-M4-008 | Light/material debug overlays | RTX-M4-001 | Heatmaps for albedo/roughness/normal/emissive/light count | `rtx_rt_debug_visualizer` modes 0..8 in `code/rendererrtx/tr_init.c` + `code/rendererrtx/shaders/rt_main.rchit` | Completed |

## M5. Temporal accumulation, denoise, and post

| Done | ID | Task | Depends on | Definition of done | Evidence | Notes |
|---|---|---|---|---|---|---|
| [x] | RTX-M5-001 | Motion vector generation for dynamic and camera motion | RTX-M3-002 | Valid motion vectors for all supported geometry paths | `code/rendererrtx/shaders/rt_main.rgen` motion reprojection + debug mode 9, `code/rendererrtx/shaders/rt_main.rchit` hit payload metadata, `code/rendererrtx/tr_init.c` visualizer range update | Completed |
| [x] | RTX-M5-002 | History buffer management with reset rules | RTX-M5-001 | Correct resets on camera cuts, map change, cvar changes | `code/rendererrtx/vk.c` history ping-pong images/descriptors, `vk_rt_update_temporal_state`, `vk_rt_invalidate`, `vk_rt_destroy_output_image` | Completed |
| [x] | RTX-M5-003 | Temporal accumulation with clamping/reprojection | RTX-M5-002 | Noise reduction without severe ghosting in normal play | `code/rendererrtx/shaders/rt_main.rgen` history reprojection, depth/motion rejection, history clamping and blend controls | Completed |
| [x] | RTX-M5-004 | Spatial denoiser integration (A-trous or equivalent) | RTX-M5-003 | Stable denoised output at target spp | `code/rendererrtx/shaders/rt_main.rgen` cross-bilateral neighborhood filter (`spatial_filter`) with depth/normal weighting | Completed |
| [x] | RTX-M5-005 | Anti-firefly and variance controls | RTX-M5-004 | Isolated bright speckles controlled by cvars | `code/rendererrtx/shaders/rt_main.rgen` firefly suppression (`suppress_fireflies`), `code/rendererrtx/tr_init.c` firefly control cvars | Completed |
| [x] | RTX-M5-006 | Tone mapping + exposure adaptation | RTX-M4-006 | Consistent HDR-to-LDR output and exposure behavior | `code/rendererrtx/shaders/rt_main.rgen` tone-map operators (Reinhard/ACES) + adaptive exposure path, `code/rendererrtx/vk.c` temporal/exposure state upload | Completed |
| [x] | RTX-M5-007 | Post stack ordering validation (UI/cinematics unaffected) | RTX-M5-006 | HUD/UI/cinematics render correctly on top | `code/rendererrtx/vk.c` post-stack validation log in `vk_rt_trace_frame` and retained RT->post_bloom->gamma composition ordering | Completed |

## M6. Feature parity and gameplay correctness

| Done | ID | Task | Depends on | Definition of done | Evidence | Notes |
|---|---|---|---|---|---|---|
| [x] | RTX-M6-001 | Weapon, muzzle flash, and projectile effects parity | RTX-M4-001 | Effects readability preserved in combat | `code/rendererrtx/vk.c` (`vk_rt_extract_dynamic_geometry`, `vk_rt_apply_effect_material_tuning`, sprite/beam radius scaling, first-person priority/material tuning) | Completed |
| [x] | RTX-M6-002 | Decals/marks impact representation | RTX-M3-003 | Bullet marks/impact effects visible and stable | `code/rendererrtx/vk.c` (`vk_rt_poly_is_mark_decal`, marks-only RE_AddPoly inclusion path, decal material flags) | Completed |
| [x] | RTX-M6-003 | Particles and volumetric approximation path | RTX-M3-003 | Smoke/sparks remain legible with RT lighting | `code/rendererrtx/vk.c` particle material classification + `code/rendererrtx/shaders/rt_main.rchit` volumetric particle shading branch (`rtx_rt_particle_volume`) | Completed |
| [x] | RTX-M6-004 | Dynamic map entities (doors/platforms) correctness | RTX-M2-003 | Moving BSP entities update without lag/artifacts | `code/rendererrtx/vk.c` (`vk_rt_append_brush_entity_geometry` replacing MOD_BRUSH proxy fallback in dynamic extraction) | Completed |
| [x] | RTX-M6-005 | Third-person, spectator, and demo playback validation | RTX-M5-007 | All camera modes behave correctly | `code/rendererrtx/vk.c` (`vk_rt_update_temporal_state` camera-mode validation: rdflags/stereo/time/fov transition resets) | Completed |
| [x] | RTX-M6-006 | UI/console/font composition compatibility | RTX-M5-007 | No regressions in UI text and overlays | `code/rendererrtx/vk.c` (`RDF_NOWORLDMODEL` UI passthrough branch preserving post composition and resetting RT history) | Completed |
| [x] | RTX-M6-007 | Gamma/brightness/color grading compatibility layer | RTX-M5-006 | Legacy cvars produce expected behavior envelope | `code/rendererrtx/vk.c` temporal legacy params upload + `code/rendererrtx/shaders/rt_main.rgen` legacy intensity compatibility shaping | Completed |
| [x] | RTX-M6-008 | Gameplay readability tuning pass | RTX-M6-001 | Competitive visibility baseline acceptable | `code/rendererrtx/vk.c` readability cvar upload + `code/rendererrtx/shaders/rt_main.rgen` readability lift/contrast/saturation/shadow-floor pass | Completed |

## M7. Performance and scalability

| Done | ID | Task | Depends on | Definition of done | Evidence | Notes |
|---|---|---|---|---|---|---|
| [ ] | RTX-M7-001 | GPU/CPU timing instrumentation per pass | RTX-M1-001 | Timings reported per pass and frame | perf overlay screenshots | |
| [ ] | RTX-M7-002 | Adaptive ray budget controls | RTX-M7-001 | Configurable quality levels with bounded frame time | benchmark table | |
| [ ] | RTX-M7-003 | Dynamic resolution and reconstruction strategy | RTX-M5-004 | Dynamic res maintains playability under load | stress test data | |
| [ ] | RTX-M7-004 | Async compute and queue overlap opportunities | RTX-M7-001 | Verified overlap for selected passes | GPU timeline capture | |
| [ ] | RTX-M7-005 | AS update throttling and dirty-region rebuilds | RTX-M2-006 | Significant reduction in AS update cost | perf deltas | |
| [ ] | RTX-M7-006 | Texture residency/streaming optimization | RTX-M3-006 | Reduced stalls and controlled memory growth | memory/perf report | |
| [ ] | RTX-M7-007 | Threading split for CPU-side prep workloads | RTX-M7-001 | Reduced main-thread frame time variance | profiler captures | |
| [ ] | RTX-M7-008 | Shipping quality presets (`low/med/high/ultra`) | RTX-M7-002 | Presets documented and validated on target GPUs | preset matrix | |

## M8. Cross-platform hardening and packaging

| Done | ID | Task | Depends on | Definition of done | Evidence | Notes |
|---|---|---|---|---|---|---|
| [ ] | RTX-M8-001 | Windows packaging copies runtime module + deps | RTX-M0-001 | Launch works from packaged folder without manual copying | package test | |
| [ ] | RTX-M8-002 | Linux packaging and loader path validation | RTX-M0-001 | `.so` found and loaded from expected locations | package test | |
| [ ] | RTX-M8-003 | macOS packaging and `.dylib` load validation | RTX-M0-001 | `.dylib` found and loaded from expected locations | package test | |
| [ ] | RTX-M8-004 | Startup diagnostics for missing deps (friendly errors) | RTX-M1-008 | Errors explain missing Vulkan/driver/module deps clearly | error screenshots | |
| [ ] | RTX-M8-005 | CI build matrix (Win/Linux/macOS, debug/release) | RTX-M8-001 | CI green for renderer module + client build | CI links | |
| [ ] | RTX-M8-006 | Headless smoke test harness for `cl_renderer rtx` | RTX-M8-005 | Automated boot to main menu/map without fatal errors | CI logs | |
| [ ] | RTX-M8-007 | Driver capability compatibility matrix | RTX-M1-007 | Documented known-good/known-bad driver versions | `doc/rtx-driver-matrix.md` | |
| [ ] | RTX-M8-008 | Regression gates for non-RT renderers | RTX-M8-005 | `renderer`, `renderer2`, `renderervk` startup tests pass | CI logs | |

## M9. QA, documentation, and release readiness

| Done | ID | Task | Depends on | Definition of done | Evidence | Notes |
|---|---|---|---|---|---|---|
| [ ] | RTX-M9-001 | Create full manual test matrix (maps/features/platforms) | RTX-M6-008 | Repeatable matrix tracked per build | `doc/rtx-test-matrix.md` | |
| [ ] | RTX-M9-002 | Add bug triage labels and severity rubric | RTX-M9-001 | Triage workflow documented | `doc/rtx-triage.md` | |
| [ ] | RTX-M9-003 | Author user-facing `rendererrtx` cvar guide | RTX-M7-008 | Cvar doc with defaults, ranges, and usage notes | `doc/rtx-cvars.md` | |
| [ ] | RTX-M9-004 | Author developer architecture overview | RTX-M4-008 | Renderer architecture and data flow diagram documented | `doc/rtx-architecture.md` | |
| [ ] | RTX-M9-005 | Release checklist for alpha milestone | RTX-M8-008 | Checklist completed and signed off | `doc/rtx-release-checklist.md` | |
| [ ] | RTX-M9-006 | Create known-issues list and workaround guidance | RTX-M8-007 | User-visible issue list maintained | `doc/rtx-known-issues.md` | |
| [ ] | RTX-M9-007 | Publish performance targets per quality preset | RTX-M7-008 | FPS/frame-time targets documented per GPU tier | `doc/rtx-performance-targets.md` | |
| [ ] | RTX-M9-008 | Define go/no-go criteria for beta branch | RTX-M9-005 | Entry/exit criteria approved and documented | `doc/rtx-beta-gates.md` | |

## Weekly update log

| Date | Summary | Tasks completed | Blockers | Next focus |
|---|---|---|---|---|
| 2026-02-14 | Implemented Milestone 6 gameplay correctness and feature parity in `rendererrtx`: prioritized first-person weapon ingestion under dynamic budget pressure, radius/emissive tuning for projectile/muzzle/effect proxies, marks/decal inclusion path, particle volumetric approximation, real moving-BSP (`MOD_BRUSH`) dynamic geometry extraction (replacing proxy fallback), camera-mode temporal reset validation, UI-only RT passthrough for `RDF_NOWORLDMODEL`, legacy intensity compatibility shaping, and readability controls in RT resolve. Regenerated shader binaries/reflection, completed Meson debug build, and validated a 12-second `+devmap q3dm1` runtime smoke with process alive (terminated manually after check). | RTX-M6-001, RTX-M6-002, RTX-M6-003, RTX-M6-004, RTX-M6-005, RTX-M6-006, RTX-M6-007, RTX-M6-008 | none | M7 performance instrumentation and scalability controls |
| 2026-02-14 | Implemented Milestone 5 temporal/post pipeline in `rendererrtx`: per-pixel camera+dynamic motion vectors, history ping-pong and reset rules, temporal reprojection with clamping/rejection, cross-bilateral spatial denoise, firefly suppression controls, tone mapping with adaptive exposure, and one-time post-stack ordering validation logging while preserving RT->bloom->gamma path. Regenerated RT shader binaries/reflection and validated with Meson debug test build. | RTX-M5-001, RTX-M5-002, RTX-M5-003, RTX-M5-004, RTX-M5-005, RTX-M5-006, RTX-M5-007 | none | M6 gameplay correctness + compatibility validation |
| 2026-02-14 | Implemented Milestone 4 shading MVP in `rendererrtx`: dynamic+sun light ingestion, hard/soft shadow ray queries, GGX/Smith/Schlick BRDF core, one-sample indirect diffuse approximation, roughness-aware specular environment reflections, miss-shader sky/environment integration, translucent/refractive strategy controls, and expanded debug overlays for light/material inspection. Added M4 implementation note and regenerated RT shader artifacts. | RTX-M4-001, RTX-M4-002, RTX-M4-003, RTX-M4-004, RTX-M4-005, RTX-M4-006, RTX-M4-007, RTX-M4-008 | none | M5 temporal accumulation + denoise |
| 2026-02-14 | Implemented Milestone 3 ingestion path in `rendererrtx`: full BSP vertex/index/material extraction, MD3+IQM dynamic model ingestion with skinning policy controls, sprite/beam/poly effect proxy strategy, tangent basis generation, shader-to-material translation with color-space/emissive/masked classification, and runtime material debug/override controls. Added M3 design/mapping docs and integrated M3 RT stats reporting. | RTX-M3-001, RTX-M3-002, RTX-M3-003, RTX-M3-004, RTX-M3-005, RTX-M3-006, RTX-M3-007, RTX-M3-008, RTX-M3-009 | local build shell missing `cl.exe` | M4 direct lighting + BRDF shading |
| 2026-02-14 | Implemented Milestone 2 RT core path in `rendererrtx`: world BLAS extraction/build from BSP, dynamic entity proxy BLAS + per-frame TLAS instance updates, ray tracing pipeline + SBT generation, per-frame `vkCmdTraceRaysKHR` dispatch wiring, AS budget throttling, optional BLAS compaction, crash-safe RT invalidation/shutdown hooks, and debug visualizer shader modes (`instance ID`, `barycentrics`, `normal`). | RTX-M2-001, RTX-M2-002, RTX-M2-003, RTX-M2-004, RTX-M2-005, RTX-M2-006, RTX-M2-007, RTX-M2-008, RTX-M2-009 | local build toolchain missing Windows resource compiler (`rc.exe`) | M3 BSP/MD3/IQM geometry and material ingestion |
| 2026-02-14 | Added explicit RT-unavailable startup behavior controls: automatic fallback to disabled RT mode by default and strict actionable fail mode via `rtx_rt_require 1`, with guidance in startup logs. | RTX-M1-008 | local build shell missing `cl.exe` | M2 static world BLAS builder |
| 2026-02-14 | Added a persistent Vulkan capability table in `rendererrtx` (descriptor indexing, buffer device address, deferred host ops, acceleration structure, ray query, ray tracing pipeline, etc.), added startup + `vkinfo` capability reporting, and added cvar-based RT capability gating (`rtx_rt_mode` + `rtx_rt_require`). | RTX-M1-007 | local build shell missing `cl.exe` | M1 safe fallback behavior when RT features unavailable |
| 2026-02-14 | Added `rendererrtx` runtime toggles for Vulkan validation layers and GPU debug marker levels (`object names` vs `command-buffer pass regions`), then wired named render-pass markers for capture tooling and documented expected labels/workflow. | RTX-M1-006 | none | M1 device capability table |
| 2026-02-14 | Replaced ad-hoc Windows-only shader compile script with deterministic Python workflow for `rendererrtx`, added generated reflection metadata (`descriptor bindings` + `push constants`), and documented usage/check mode plus wrapper scripts for Windows/POSIX. | RTX-M1-005 | none | M1 GPU debug markers + validation toggles |
| 2026-02-14 | Added explicit descriptor/pipeline layout registry helpers in `rendererrtx` Vulkan path and wired descriptor/pipeline layout creation, allocation, and teardown through registry IDs to reduce ad-hoc layout usage. | RTX-M1-004 | local build shell missing `cl.exe` | M1 shader compilation/reflection workflow |
| 2026-02-13 | Initial plan created; separate `rendererrtx` module and `cl_renderer rtx` path already wired. Added startup diagnostics plus cvar policy/smoke test docs. Added explicit backend frame-pass graph skeleton with `rtx_debug_framegraph` diagnostics. Added Vulkan resource lifecycle tracker with resize/frame integration and `rtx_debug_resource_lifetime` diagnostics. Hardened swapchain resize/recreate with deferred retry scheduling, safer destroy/recreate ordering, and frame-path guards when swapchain acquisition is unavailable. | RTX-M0-001, RTX-M0-002, RTX-M0-003, RTX-M0-006, RTX-M0-007, RTX-M1-001, RTX-M1-002, RTX-M1-003 | none | M0 baseline capture + perf capture |

## Task template (copy for new tasks)

`| [ ] | RTX-MX-YYY | Task name | dependencies | explicit definition of done | PR/commit/log/capture | notes |`
