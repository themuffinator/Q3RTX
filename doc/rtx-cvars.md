# Q3RTX `rendererrtx` Cvar Guide

Last updated: 2026-02-15  
Scope: user-facing `rtx_*` controls for quality, stability, performance, and debug workflows.

## Quick start profiles

### Stable high quality (recommended default)

```cfg
seta cl_renderer rtx
seta rtx_rt_mode 2
seta rtx_rt_require 0
seta rtx_rt_quality_preset 3
seta rtx_rt_dynamic_resolution 1
seta rtx_rt_adaptive_budget 1
```

### Lower-end GPU profile

```cfg
seta cl_renderer rtx
seta rtx_rt_mode 2
seta rtx_rt_quality_preset 1
seta rtx_rt_dynamic_resolution 1
seta rtx_rt_temporal_enable 1
seta rtx_rt_spatial_denoise 1
```

### Debug validation profile

```cfg
seta cl_renderer rtx
seta rtx_debug_vk_validation 1
seta rtx_debug_framegraph 1
seta rtx_rt_perf_timing 1
seta rtx_rt_debug_visualizer 1
```

## Preset behavior (`rtx_rt_quality_preset`)

Preset values from `code/rendererrtx/vk.c` runtime scaling tables:

| Preset | Name | Target frame ms | Dynres min/max | AS build budget (MB) | Instance budget | Max lights |
|---|---|---|---|---|---|---|
| `1` | low | 16.6 | 0.55 / 0.85 | 48 | 384 | 24 |
| `2` | medium | 13.8 | 0.65 / 0.95 | 96 | 768 | 48 |
| `3` | high | 11.1 | 0.75 / 1.00 | 160 | 1536 | 64 |
| `4` | ultra | 8.3 | 0.85 / 1.00 | 256 | 3072 | 96 |

`0` means custom mode: explicit cvar values are used directly.

## Usage notes by category

1. Startup/capability
   - `rtx_rt_mode` and `rtx_rt_require` define hard/soft capability gating.
2. Performance and scaling
   - Use `rtx_rt_quality_preset` first, then override specific budgets only if needed.
   - Keep `rtx_rt_dynamic_resolution` and `rtx_rt_adaptive_budget` enabled for better frame-time stability.
3. Temporal/denoise/post
   - `rtx_rt_temporal_alpha`, `rtx_rt_temporal_clamp`, and denoise sigma values are the primary noise/ghosting controls.
4. Lighting/material
   - `rtx_rt_shadow_*`, `rtx_rt_indirect_*`, `rtx_rt_reflection_strength`, and emissive controls are the main look-development knobs.
5. Gameplay readability
   - `rtx_rt_readability_*` provides a targeted visibility tuning layer without changing map assets.
6. Debug
   - `rtx_rt_debug_visualizer`, `rtx_rt_material_debug`, `rtx_rt_perf_timing`, and `rtx_debug_*` are intended for diagnostics, not shipping defaults.

## Full reference (defaults and ranges)

Source of truth: `code/rendererrtx/tr_init.c`.

| Cvar | Default | Range |
|---|---:|---|
| `rtx_debug_framegraph` | `0` | `0..2` |
| `rtx_debug_resource_lifetime` | `0` | `0..2` |
| `rtx_debug_gpu_markers` | `1` | `0..2` |
| `rtx_debug_vk_validation` | `0` | `0..1` |
| `rtx_caps_report` | `1` | `0..2` |
| `rtx_rt_mode` | `0` | `0..2` |
| `rtx_rt_require` | `0` | `0..1` |
| `rtx_rt_debug_visualizer` | `0` | `0..10` |
| `rtx_rt_as_build_budget_mb` | `96` | `0..2048` |
| `rtx_rt_as_instance_budget` | `1024` | `1..16384` |
| `rtx_rt_as_compaction` | `1` | `0..1` |
| `rtx_rt_debug_as_stats` | `0` | `0..2` |
| `rtx_rt_temporal_enable` | `1` | `0..1` |
| `rtx_rt_temporal_alpha` | `0.88` | `0..0.98` |
| `rtx_rt_temporal_clamp` | `1.25` | `0..8` |
| `rtx_rt_temporal_depth_reject` | `4.0` | `0..4096` |
| `rtx_rt_temporal_motion_reject` | `18.0` | `0..256` |
| `rtx_rt_temporal_camera_cut` | `128.0` | `0..8192` |
| `rtx_rt_spatial_denoise` | `1` | `0..1` |
| `rtx_rt_spatial_sigma_depth` | `2.5` | `0..64` |
| `rtx_rt_spatial_sigma_normal` | `24.0` | `0..128` |
| `rtx_rt_firefly_threshold` | `8.0` | `>=0` |
| `rtx_rt_firefly_strength` | `0.75` | `0..1` |
| `rtx_rt_tonemap_mode` | `2` | `0..2` |
| `rtx_rt_exposure` | `1.0` | `0.01..32` |
| `rtx_rt_auto_exposure` | `1` | `0..1` |
| `rtx_rt_exposure_speed` | `0.08` | `0..1` |
| `rtx_rt_exposure_min` | `0.2` | `0.01..32` |
| `rtx_rt_exposure_max` | `4.0` | `0.01..64` |
| `rtx_rt_motion_dynamic_scale` | `1.0` | `0..4` |
| `rtx_rt_post_validate` | `1` | `0..1` |
| `rtx_rt_perf_timing` | `0` | `0..2` |
| `rtx_rt_perf_interval` | `120` | `1..4096` |
| `rtx_rt_adaptive_budget` | `1` | `0..1` |
| `rtx_rt_target_frame_ms` | `12.0` | `4..50` |
| `rtx_rt_budget_response` | `0.18` | `0.01..1.0` |
| `rtx_rt_budget_min_scale` | `0.45` | `0.1..1.0` |
| `rtx_rt_budget_max_scale` | `1.25` | `1.0..2.0` |
| `rtx_rt_dynamic_resolution` | `1` | `0..1` |
| `rtx_rt_dynamic_resolution_min` | `0.60` | `0.25..1.0` |
| `rtx_rt_dynamic_resolution_max` | `1.00` | `0.25..1.5` |
| `rtx_rt_dynamic_resolution_rate` | `0.08` | `0.01..1.0` |
| `rtx_rt_async_overlap` | `1` | `0..1` |
| `rtx_rt_as_rebuild_interval` | `1` | `1..16` |
| `rtx_rt_as_dirty_threshold` | `6.0` | `0..4096` |
| `rtx_rt_texture_stream_budget_mb` | `96` | `0..2048` |
| `rtx_rt_texture_stream_stats` | `0` | `0..1` |
| `rtx_rt_prep_frame_stride` | `1` | `1..8` |
| `rtx_rt_quality_preset` | `3` | `0..4` |
| `rtx_rt_first_person_priority` | `1` | `0..1` |
| `rtx_rt_effect_radius_scale` | `1.2` | `0.1..4` |
| `rtx_rt_effect_emissive_boost` | `2.0` | `>=0` |
| `rtx_rt_marks_enable` | `1` | `0..1` |
| `rtx_rt_particle_volume` | `1` | `0..1` |
| `rtx_rt_ui_passthrough` | `1` | `0..1` |
| `rtx_rt_camera_mode_validate` | `1` | `0..1` |
| `rtx_rt_legacy_color_compat` | `1` | `0..1` |
| `rtx_rt_readability_lift` | `0.06` | `-1..1` |
| `rtx_rt_readability_contrast` | `1.05` | `0.2..3` |
| `rtx_rt_readability_saturation` | `1.08` | `0..3` |
| `rtx_rt_readability_shadow_floor` | `0.05` | `0..0.5` |
| `rtx_rt_dynamic_blas` | `0` | `0..1` |
| `rtx_rt_dynamic_effects` | `1` | `0..2` |
| `rtx_rt_iqm_skinning` | `1` | `0..2` |
| `rtx_rt_masked_mode` | `1` | `0..1` |
| `rtx_rt_masked_cutoff` | `-1` | `-1..1` |
| `rtx_rt_material_debug` | `0` | `0..3` |
| `rtx_rt_material_override` | `0` | `0..3` |
| `rtx_rt_material_roughness_override` | `-1` | `-1..1` |
| `rtx_rt_material_metallic_override` | `-1` | `-1..1` |
| `rtx_rt_material_emissive_override` | `-1` | `>=-1` |
| `rtx_rt_emissive_scale` | `1.0` | `>=0` |
| `rtx_rt_emissive_keyword_boost` | `2.5` | `>=0` |
| `rtx_rt_shadow_mode` | `2` | `0..2` |
| `rtx_rt_shadow_softness` | `0.25` | `0..1` |
| `rtx_rt_indirect_bounce` | `1` | `0..1` |
| `rtx_rt_indirect_strength` | `0.35` | `>=0` |
| `rtx_rt_reflection_strength` | `1.0` | `>=0` |
| `rtx_rt_sky_intensity` | `1.0` | `>=0` |
| `rtx_rt_sun_intensity` | `1.0` | `>=0` |
| `rtx_rt_refractive_mode` | `1` | `0..2` |
| `rtx_rt_refractive_ior` | `1.33` | `1.0..2.5` |
| `rtx_rt_max_lights` | `64` | `1..256` |
