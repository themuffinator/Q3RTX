# Q3RTX Driver Compatibility Matrix

Last updated: 2026-02-15  
Scope: `rendererrtx` startup + map-load behavior, with focus on Vulkan and RT capability gates.

## Matrix

| Platform | GPU | Driver / Runtime | RT mode | Status | Notes / Workaround |
|---|---|---|---|---|---|
| Windows 11 23H2 | NVIDIA GeForce RTX 4060 Laptop GPU | NVIDIA 591.74 (Vulkan 1.4.325) | `rtx_rt_mode 2` | Known-good | Loads renderer module, reaches map load and RT path. |
| Windows 11 23H2 | NVIDIA GeForce RTX 4060 Laptop GPU | NVIDIA 591.74 (Vulkan 1.4.325) | `rtx_rt_mode 2` with dynamic BLAS stress | Known-bad | Observed `VK_ERROR_DEVICE_LOST` during dynamic BLAS submission. Temporary workaround: `rtx_rt_dynamic_blas 0`. |
| Windows 11 23H2 | Intel Iris Xe (integrated) | Intel D3D12 Vulkan translation path (reported by runtime device list) | `rtx_rt_mode 2` | Unsupported (expected) | Capability gate should fall back (`rtx_rt_require 0`) or fail with actionable message (`rtx_rt_require 1`). |
| Windows 11 23H2 | Microsoft Basic Render Driver | CPU software adapter | `rtx_rt_mode 2` | Unsupported (expected) | Not a target for RT mode; keep fallback behavior enabled. |

## Validation policy

1. Record exact GPU + driver version + Vulkan runtime reported by `gfxinfo`.
2. Record launch args (`cl_renderer`, `rtx_rt_mode`, `rtx_rt_require`, map).
3. Classify as `Known-good`, `Known-bad`, or `Unsupported (expected)`.
4. For `Known-bad`, include a deterministic workaround when available.

## Open entries

- Linux (Mesa RADV/NVIDIA proprietary) validation pending CI path with external game-data mount.
- macOS (MoltenVK) validation pending CI path with external game-data mount.
