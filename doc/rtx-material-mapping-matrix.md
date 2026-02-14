# Q3RTX Material Mapping Matrix (`rendererrtx`)

Last updated: 2026-02-14  
Scope: M3 translation of Quake III shader/script inputs into RT material metadata.

## Translation Order

1. Start from default material values.
2. Apply shader-level flags and naming heuristics.
3. Apply per-stage and per-image heuristics.
4. Apply explicit override cvars (final authority).

## Base Defaults

| Field | Default |
|---|---|
| `baseColor` | `(1, 1, 1, 1)` |
| `roughness` | `0.85` |
| `metallic` | `0.0` |
| `emissiveColor` | `(0, 0, 0)` |
| `emissiveScale` | `rtx_rt_emissive_scale` |
| `alphaCutoff` | `0.0` |
| Flags | none |

## Shader and Stage Mapping

| Source signal | Mapping result | Notes |
|---|---|---|
| `shader->cullType == CT_TWO_SIDED` | add `TWO_SIDED` flag | two-sided RT classification |
| `shader->sort > SS_OPAQUE` | add `TRANSLUCENT` flag | non-opaque sorted materials |
| `shader->isSky` or `SURF_SKY` | add `SKY` + `EMISSIVE`; raise emissive scale | sky treated as emissive contributor |
| `SURF_METALSTEPS` | increase `metallic`, lower `roughness` | hard-surface heuristic |
| `SURF_SLICK` | lower `roughness` | glossy/slippery hint |
| shader name contains `metal` | increase `metallic`, lower `roughness` | naming heuristic |
| shader name contains `glass` | mark `TRANSLUCENT`, lower `roughness` | transparent-like heuristic |
| shader name contains `grate/fence/foliage` | mark `MASKED`, set cutoff baseline | masked heuristic |
| stage alpha test (`GLS_ATEST_*`) | mark `MASKED`, set/raise cutoff | alpha-test-derived mask cutoff |
| additive stage blend (`ONE, ONE`) | mark `EMISSIVE`, raise emissive scale | glow/additive stages |
| `rgbGen == CGEN_CONST` | set `baseColor` from stage constant color | constant color passthrough |
| image name contains `_n` or `normal` | set normal map colorspace to data path; slightly reduce roughness | normal-map hint |
| image name contains `metal` or `_m` | raise `metallic` | metallic map hint |
| image name contains `rough` or `gloss` | lower `roughness` | roughness/gloss hint |
| image name contains `glow/emissive/light` | mark `EMISSIVE`, raise emissive color/scale | emissive keyword boost uses `rtx_rt_emissive_keyword_boost` |

## Color-Space Policy

| Channel | Policy |
|---|---|
| Albedo | default `sRGB`; `IMGFLAG_LIGHTMAP` forced `linear`; `.hdr/.exr` treated as `HDR` |
| Normal/data maps | default `linear`; `.hdr/.exr` treated as `HDR` |
| Emissive | inherits albedo image policy when available, otherwise `sRGB` |

## Override Controls

| Cvar | Effect |
|---|---|
| `rtx_rt_material_override` | preset mode: disabled/clay/chrome/emissive-debug |
| `rtx_rt_material_roughness_override` | force all translated roughness values |
| `rtx_rt_material_metallic_override` | force all translated metallic values |
| `rtx_rt_material_emissive_override` | force global emissive scale for all translated materials |
| `rtx_rt_masked_mode` | force masked off or honor masked metadata |
| `rtx_rt_masked_cutoff` | override derived alpha cutoff (`-1` keeps derived cutoff) |
