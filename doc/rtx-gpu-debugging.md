# Q3RTX GPU Debugging (`rendererrtx`)

Last updated: 2026-02-14
Scope: `code/rendererrtx` Vulkan diagnostics and capture labels.

## Runtime Toggles

All toggles below are renderer cvars and require `vid_restart` after change.

1. `rtx_debug_vk_validation`
   - `0`: disable Vulkan validation layers.
   - `1`: request Vulkan validation layers at instance creation.
2. `rtx_debug_gpu_markers`
   - `0`: disable debug-marker extension usage.
   - `1`: enable Vulkan object naming only.
   - `2`: enable object naming plus command-buffer render-pass markers.

## Notes

1. Validation layer support depends on build configuration and installed Vulkan layers.
2. If `rtx_debug_vk_validation 1` is set but unavailable, startup logs will report fallback to non-validation mode.
3. If debug markers are requested but unsupported by the selected GPU/driver, startup logs will report it.

## Capture Expectations

With `rtx_debug_gpu_markers 2`, RenderDoc (or similar tools) should show pass labels like:

1. `RTX Pass: main`
2. `RTX Pass: post_bloom`
3. `RTX Pass: bloom_extract`
4. `RTX Pass: blur N`
5. `RTX Pass: capture`
6. `RTX Pass: gamma`
7. `RTX Pass: screenmap`

These labels are emitted at Vulkan render-pass boundaries and are intended to make frame capture navigation deterministic and readable.
