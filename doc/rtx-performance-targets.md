# Q3RTX Performance Targets By Preset

Last updated: 2026-02-15  
Scope: release-facing frame-time goals for `rendererrtx` presets (`low`, `medium`, `high`, `ultra`).

## Measurement method

1. Resolution: `1920x1080` windowed, `r_fullscreen 0`.
2. Map set: `q3dm1`, `q3dm7`, `q3ctf4`.
3. Run length: 90 seconds per map.
4. Metrics:
   - median frame time
   - 95th percentile frame time
   - worst 1% frame-time spikes
5. Required runtime settings:
   - `rtx_rt_dynamic_resolution 1`
   - `rtx_rt_adaptive_budget 1`
   - preset under test (`rtx_rt_quality_preset`)

## GPU tiers

| Tier | Representative hardware | Use in targets |
|---|---|---|
| Tier-1 | RTX 4080+/RX 7900 XTX class | Enthusiast target |
| Tier-2 | RTX 3060/4060/RX 6700 XT class | Mainstream target |
| Tier-3 | RTX 2060/3050/RX 6600 class | Entry RT-capable target |

## Preset targets (95th percentile frame time)

| Preset | Internal adaptive target (`vk.c`) | Tier-1 goal | Tier-2 goal | Tier-3 goal |
|---|---:|---:|---:|---:|
| low (`1`) | 16.6 ms | <= 12 ms | <= 16.6 ms | <= 22 ms |
| medium (`2`) | 13.8 ms | <= 11 ms | <= 15 ms | <= 20 ms |
| high (`3`) | 11.1 ms | <= 10 ms | <= 14 ms | <= 18 ms |
| ultra (`4`) | 8.3 ms | <= 11 ms | <= 16 ms | <= 22 ms |

## Hard fail thresholds

Any preset/tier combination is `fail` if either condition is true:

1. 95th percentile frame time exceeds target by >20%.
2. Worst 1% spikes exceed 2.2x target for >5 consecutive seconds.

## Stability targets

1. No `VK_ERROR_DEVICE_LOST` during test run.
2. No progressive memory growth beyond 10% after warm-up.
3. No sustained oscillation of dynamic resolution at clamp bounds for >30 seconds.

## Reporting template

| Date | Build | Preset | Tier/env | Map | Median ms | P95 ms | 1% worst ms | Pass/fail |
|---|---|---|---|---|---:|---:|---:|---|
| 2026-02-15 | `build/meson-debug` | high | Tier-2 (ENV-WIN-NV-01) | `q3dm1` | pending | pending | pending | pending |
