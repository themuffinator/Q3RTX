# Q3RTX Capability Table And Gating

Last updated: 2026-02-14  
Scope: `code/rendererrtx` Vulkan capability detection and startup gating.

## Runtime Capability Table

`rendererrtx` now records a per-device capability table during Vulkan device extension discovery.  
The table includes:

1. swapchain support
2. dedicated allocation + memory requirements 2
3. debug marker extension availability
4. descriptor indexing extension availability
5. buffer device address extension availability
6. timeline semaphore and Vulkan memory model extension availability
7. deferred host operations extension availability
8. acceleration structure extension availability
9. ray query extension availability
10. ray tracing pipeline extension availability

## Reporting

Capability report output is controlled by:

1. `rtx_caps_report 0`: disabled
2. `rtx_caps_report 1`: compact startup capability summary
3. `rtx_caps_report 2`: verbose startup capability summary

The `vkinfo` command prints the active capability table and RT gating result.

## RT Mode Gating

Two cvars gate requested RT capability modes:

1. `rtx_rt_mode` (latched)
   - `0`: disabled
   - `1`: request ray query capability set
   - `2`: request ray tracing pipeline capability set
2. `rtx_rt_require` (latched)
   - `0`: fallback to mode `0` if requirements are unavailable
   - `1`: fail startup if requirements are unavailable

If required extensions for the requested mode are missing, startup now either:

1. logs a warning and falls back to mode `0`, or
2. fails with an actionable error when `rtx_rt_require 1` is set.
