# Q3RTX M3 Geometry and Material Ingestion

Last updated: 2026-02-14  
Scope: `code/rendererrtx` Milestone 3 implementation (`RTX-M3-001` to `RTX-M3-009`).

## Summary

Milestone 3 is implemented as a CPU-side ingestion pipeline that builds RT-ready world and dynamic geometry buffers, translates Quake III shader data into provisional PBR metadata, and exposes runtime controls for rapid material iteration.

## M3 Task Mapping

1. `RTX-M3-001` BSP extraction
   - Implemented in `vk_rt_extract_world_geometry` via:
     - `vk_rt_append_surface_face_geometry`
     - `vk_rt_append_surface_grid_geometry`
     - `vk_rt_append_surface_triangles_geometry`
   - World extraction now records vertices, indices, material assignment, total triangle counts, masked triangle counts, and degenerate triangle counts.
   - Extraction computes a raster-reference triangle count from BSP surfaces and warns if RT ingestion count diverges.

2. `RTX-M3-002` MD3/IQM ingestion + skinning policy
   - Implemented in:
     - `vk_rt_append_md3_entity_geometry`
     - `vk_rt_append_iqm_entity_geometry`
     - `vk_rt_extract_dynamic_geometry`
   - Runtime skinning policy cvar:
     - `rtx_rt_iqm_skinning 0`: bind/static
     - `rtx_rt_iqm_skinning 1`: full interpolated CPU skinning
     - `rtx_rt_iqm_skinning 2`: current-frame skinning only

3. `RTX-M3-003` Sprite/beam/particle strategy
   - Implemented as hybrid RT proxy geometry:
     - sprites: `vk_rt_append_sprite_entity_geometry`
     - beam-like effects: `vk_rt_append_beam_entity_geometry`
     - optional `RE_AddPoly` ingestion: `vk_rt_append_poly_geometry`
   - Runtime policy cvar:
     - `rtx_rt_dynamic_effects 0`: model-only
     - `rtx_rt_dynamic_effects 1`: model + sprite/beam
     - `rtx_rt_dynamic_effects 2`: mode 1 + polys

4. `RTX-M3-004` Tangent generation/validation
   - Implemented in `vk_rt_generate_tangents`.
   - Per-vertex tangent frame is rebuilt from triangle UV gradients with fallback for degenerate/invalid derivatives.

5. `RTX-M3-005` Shader script to PBR translation
   - Implemented in `vk_rt_translate_shader_to_material`.
   - Translation uses shader flags, stage state bits, texture-name heuristics, and optional global overrides.

6. `RTX-M3-006` Color-space policy
   - Implemented in:
     - `vk_rt_material_albedo_color_space`
     - `vk_rt_material_data_color_space`
   - Material metadata tags albedo/normal/emissive decode spaces (`linear`, `sRGB`, `HDR`).

7. `RTX-M3-007` Emissive extraction/scaling
   - Emissive classification and scaling implemented in material translation using:
     - shader/stage blend hints
     - shader/image keyword heuristics
     - sky/surface flags
   - Runtime controls:
     - `rtx_rt_emissive_scale`
     - `rtx_rt_emissive_keyword_boost`
     - `rtx_rt_material_emissive_override`

8. `RTX-M3-008` Masked/alpha-test behavior
   - Alpha-test and masked classification implemented through:
     - stage alpha-test bits (`GLS_ATEST_*`)
     - masked keyword heuristics (`grate`, `fence`, `foliage`)
     - per-material alpha cutoff metadata
   - Runtime controls:
     - `rtx_rt_masked_mode`
     - `rtx_rt_masked_cutoff`
   - Current scope note: masked handling is metadata-driven in the present debug RT shading path. Texture-sampled any-hit rejection is deferred to M4 shading integration.

9. `RTX-M3-009` Material override/debug controls
   - Implemented cvar-driven debug/override controls:
     - `rtx_rt_material_debug`
     - `rtx_rt_material_override`
     - `rtx_rt_material_roughness_override`
     - `rtx_rt_material_metallic_override`
     - `rtx_rt_material_emissive_override`
   - World/dynamic material summaries are emitted in RT extraction logs for rapid iteration.

## Validation Workflow

Use these settings to validate ingestion and diagnostics:

```cfg
seta cl_renderer rtx
seta rtx_rt_mode 2
seta rtx_rt_debug_as_stats 1
seta rtx_rt_material_debug 3
seta rtx_rt_dynamic_effects 2
seta rtx_rt_iqm_skinning 1
seta rtx_rt_masked_mode 1
vid_restart
```

Expected console output includes:

1. world extraction summary with counts (`faces/grids/triangles/materials/maskedTriangles/degenerate`)
2. dynamic extraction summary (`entities/effects/triangles/materials`)
3. optional material entry dumps when `rtx_rt_material_debug >= 2`
