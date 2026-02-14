# Q3RTX M4 Lighting and PBR Shading MVP

Last updated: 2026-02-14  
Scope: `rendererrtx` Milestone 4 implementation (`RTX-M4-001` through `RTX-M4-008`).

## Summary

Milestone 4 introduces a physically based RT shading pass over M3 geometry/material ingestion:

1. direct lighting from scene dynamic lights plus directional sun
2. hard/soft shadow ray queries
3. GGX/Smith/Schlick BRDF
4. one-bounce indirect diffuse approximation
5. roughness-aware specular reflection response
6. sky/environment integration in miss and reflection paths
7. translucent/refractive material strategy
8. expanded debug overlays for light/material inspection

## Task Mapping

1. `RTX-M4-001` Direct lighting (static + dynamic)
   - Dynamic lights ingested from `backEnd.refdef.dlights` into RT light buffer each frame.
   - Directional sun light ingested from `tr.sunLight` + `tr.sunDirection`.
   - Implemented in:
     - `vk_rt_update_light_buffer` (`code/rendererrtx/vk.c`)
     - `rt_main.rchit` direct light loop (`code/rendererrtx/shaders/rt_main.rchit`)

2. `RTX-M4-002` Hard/soft shadow ray queries
   - Hard shadow: terminate-on-first-hit + skip-closest-hit query.
   - Soft shadow: cone-jittered shadow direction sampling.
   - Implemented in:
     - `rt_shadow.rmiss` (`code/rendererrtx/shaders/rt_shadow.rmiss`)
     - shadow policy in `rt_main.rchit` (`trace_shadow_visibility`)
   - Runtime controls:
     - `rtx_rt_shadow_mode`
     - `rtx_rt_shadow_softness`

3. `RTX-M4-003` BRDF core (GGX/Smith/Schlick)
   - Cook-Torrance microfacet BRDF with:
     - GGX NDF
     - Schlick-GGX geometry terms
     - Schlick Fresnel
   - Implemented in `rt_main.rchit`.

4. `RTX-M4-004` Indirect diffuse bounce
   - One-sample cosine-hemisphere indirect diffuse approximation.
   - Optional visibility query for sampled indirect direction.
   - Implemented in `rt_main.rchit`.
   - Runtime controls:
     - `rtx_rt_indirect_bounce`
     - `rtx_rt_indirect_strength`

5. `RTX-M4-005` Specular reflections + roughness response
   - Reflection vector with roughness-driven cone perturbation.
   - Environment response scales with roughness and Fresnel.
   - Implemented in `rt_main.rchit`.
   - Runtime control:
     - `rtx_rt_reflection_strength`

6. `RTX-M4-006` Sky/environment lighting integration
   - Miss shader evaluates sky gradient + sun disk.
   - Same environment function used by reflection and indirect paths.
   - Implemented in:
     - `rt_main.rmiss`
     - `rt_main.rchit`
   - Runtime controls:
     - `rtx_rt_sky_intensity`
     - `rtx_rt_sun_intensity`

7. `RTX-M4-007` Transparent/refractive strategy
   - Strategy defined and implemented for `TRANSLUCENT` materials:
     - mode 0: treat as opaque
     - mode 1: transmission blend
     - mode 2: IOR-based refractive direction with Fresnel blend
   - Implemented in `rt_main.rchit`.
   - Runtime controls:
     - `rtx_rt_refractive_mode`
     - `rtx_rt_refractive_ior`

8. `RTX-M4-008` Light/material debug overlays
   - `rtx_rt_debug_visualizer` expanded to modes:
     - `0` shaded
     - `1` instance ID
     - `2` barycentrics
     - `3` normal
     - `4` albedo
     - `5` roughness
     - `6` emissive
     - `7` light-count heatmap
     - `8` metallic
   - Implemented in `rt_main.rchit` + cvar registration in `tr_init.c`.

## Runtime Tuning Cvars

```cfg
seta rtx_rt_shadow_mode 2
seta rtx_rt_shadow_softness 0.25
seta rtx_rt_indirect_bounce 1
seta rtx_rt_indirect_strength 0.35
seta rtx_rt_reflection_strength 1.0
seta rtx_rt_sky_intensity 1.0
seta rtx_rt_sun_intensity 1.0
seta rtx_rt_refractive_mode 1
seta rtx_rt_refractive_ior 1.33
seta rtx_rt_max_lights 64
```

## Build Notes

Shader artifacts were regenerated after shader changes:

1. `code/rendererrtx/shaders/spirv/shader_data.c`
2. `code/rendererrtx/shaders/spirv/shader_reflection.json`
