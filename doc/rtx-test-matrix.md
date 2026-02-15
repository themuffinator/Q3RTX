# Q3RTX Manual Test Matrix

Last updated: 2026-02-15  
Scope: manual QA coverage for `rendererrtx` startup, visual correctness, gameplay readability, and performance.

## Test environments

| Environment ID | Platform | GPU | Driver/runtime | Notes |
|---|---|---|---|---|
| ENV-WIN-NV-01 | Windows 11 23H2 | NVIDIA GeForce RTX 4060 Laptop GPU | NVIDIA 591.74 / Vulkan 1.4.325 | Primary development target |
| ENV-WIN-INT-01 | Windows 11 23H2 | Intel Iris Xe | Intel runtime path | Capability fallback validation |
| ENV-LIN-NV-01 | Ubuntu 24.04 | NVIDIA RTX class | proprietary Vulkan driver | CI candidate |
| ENV-MAC-01 | macOS 14 | Apple Silicon | MoltenVK | Compatibility target |

## Map set

| Map ID | Map | Purpose |
|---|---|---|
| MAP-01 | `q3dm1` | baseline indoor combat readability |
| MAP-02 | `q3dm7` | mixed interior/exterior, vertical combat |
| MAP-03 | `q3tourney2` | high contrast duel readability |
| MAP-04 | `q3ctf4` | large scene + light diversity |

## Execution profile

1. Per-commit smoke: `TC-BOOT-*`, `TC-REN-*`, `TC-REG-*`.
2. Milestone/full sweep: all cases below.
3. Release candidate pass: all cases on all required environments.

## Test cases

| Test ID | Area | Env | Map | Launch/command | Pass criteria | Evidence |
|---|---|---|---|---|---|---|
| TC-BOOT-001 | Renderer load | all | n/a | `+set cl_renderer rtx` | module loads, `GetRefAPI` resolves, no fatal error | `qconsole.log` |
| TC-BOOT-002 | Renderer fallback | all | n/a | `seta cl_renderer invalid; vid_restart` | fallback/reset path works with clear diagnostics | log screenshot |
| TC-BOOT-003 | Capability gate | ENV-WIN-INT-01 | n/a | `+set rtx_rt_mode 2 +set rtx_rt_require 0` | unsupported RT mode falls back cleanly | `vkinfo` + log |
| TC-BOOT-004 | Strict gate error | ENV-WIN-INT-01 | n/a | `+set rtx_rt_mode 2 +set rtx_rt_require 1` | actionable startup failure text | error screenshot |
| TC-REN-001 | World geometry ingestion | ENV-WIN-NV-01 | MAP-01 | `+set rtx_rt_debug_as_stats 1` | triangle counts stable frame-to-frame | log snippet |
| TC-REN-002 | Dynamic entities | ENV-WIN-NV-01 | MAP-02 | spectator roam | moving models update without stale BLAS artifacts | video capture |
| TC-REN-003 | Materials/PBR translation | ENV-WIN-NV-01 | MAP-03 | `+set rtx_rt_material_debug 1` | roughness/metalness/emissive look plausible | screenshot set |
| TC-REN-004 | Masked geometry | ENV-WIN-NV-01 | MAP-01 | `+set rtx_rt_masked_mode 1` | fences/grates visibility is correct | screenshot set |
| TC-LIT-001 | Direct lights | ENV-WIN-NV-01 | MAP-01 | default | dynamic and static lights contribute correctly | screenshot |
| TC-LIT-002 | Shadows | ENV-WIN-NV-01 | MAP-02 | `+set rtx_rt_shadow_mode 2` | moving entities cast stable shadows | video capture |
| TC-LIT-003 | Reflections/refraction | ENV-WIN-NV-01 | MAP-04 | `+set rtx_rt_refractive_mode 1` | roughness response and refractive path stable | screenshot |
| TC-TEMP-001 | Temporal accumulation | ENV-WIN-NV-01 | MAP-03 | `+set rtx_rt_temporal_enable 1` | reduced noise without severe ghosting | A/B capture |
| TC-TEMP-002 | History reset rules | ENV-WIN-NV-01 | MAP-01 | camera cuts/`vid_restart` | history invalidates correctly on transitions | log + video |
| TC-UI-001 | HUD/console composition | all | MAP-01 | open console/chat/HUD | UI layers remain correct over RT output | screenshot |
| TC-GAME-001 | Weapon/effects parity | ENV-WIN-NV-01 | MAP-01 | combat sequence | muzzle/projectile effects remain readable | clip |
| TC-GAME-002 | Decals/marks | ENV-WIN-NV-01 | MAP-03 | repeated impacts | marks remain visible and stable | screenshot |
| TC-PERF-001 | Preset scaling | ENV-WIN-NV-01 | MAP-04 | presets 1..4 | expected frame-time ordering low->ultra | perf log |
| TC-PERF-002 | Adaptive budget | ENV-WIN-NV-01 | MAP-04 | `+set rtx_rt_adaptive_budget 1` | frame spikes reduced versus disabled | perf compare |
| TC-PERF-003 | Dynamic resolution | ENV-WIN-NV-01 | MAP-04 | `+set rtx_rt_dynamic_resolution 1` | internal scale adapts within bounds | perf log + scale trace |
| TC-REG-001 | Non-RT renderer startup | all | n/a | `cl_renderer opengl/opengl2/vulkan` | all supported non-RT renderers boot cleanly | smoke reports |

## Run log

| Date | Build | Env | Cases run | Result | Notes |
|---|---|---|---|---|---|
| 2026-02-15 | `build/meson-debug` | ENV-WIN-NV-01 | matrix bootstrap | In progress | matrix established; full sweep pending dedicated QA pass |

## Report template

Use this for each full-sweep run:

1. Build SHA or local build directory.
2. Environment ID(s).
3. Case IDs executed.
4. Pass/fail result per case.
5. Evidence file references.
6. Linked issues for failures.
