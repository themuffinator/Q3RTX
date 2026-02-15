# Q3RTX Known Issues And Workarounds

Last updated: 2026-02-15  
Scope: user-visible `rendererrtx` issues and practical mitigations.

## Active issues

| ID | Severity | Issue | Affected environments | Workaround | Status |
|---|---|---|---|---|---|
| KI-001 | S1 | Dynamic BLAS submission can trigger `VK_ERROR_DEVICE_LOST` under heavy dynamic-scene updates. | Windows + NVIDIA (observed on RTX 4060 laptop, 591.74) | `seta rtx_rt_dynamic_blas 0`; reduce dynamic effect pressure (`rtx_rt_dynamic_effects 1`) | Open |
| KI-002 | S2 | RT startup smoke in CI requires external Quake III data path and may be skipped on hosted runners. | CI Linux hosted runners without configured data | Configure `Q3RTX_BASEPATH` in workflow vars to enable full startup checks | Open |
| KI-003 | S3 | GPU debug marker extension (`VK_EXT_debug_marker`) is unavailable on some Vulkan stacks, so pass markers are disabled. | Some modern Vulkan drivers | No action required; rely on validation/perf logs and framegraph diagnostics | Open |
| KI-004 | S3 | Integrated/non-RT-capable adapters cannot run RT mode 2. | Integrated GPUs, software adapters | Use `seta rtx_rt_require 0` for fallback or `seta cl_renderer vulkan` | Open |
| KI-005 | S3 | Full baseline screenshot/perf capture set is not yet published in `doc/baseline/`. | All | Use `doc/rtx-test-matrix.md` procedure until baseline pack is published | Open |

## Issue submission checklist

1. Include OS, GPU, driver/runtime, and build hash.
2. Include launch args and `rtx_*` overrides.
3. Attach `qconsole.log`.
4. Attach screenshot/video for visual issues.
5. Reference matching test case ID from `doc/rtx-test-matrix.md` when possible.

## Short-term mitigation defaults

Use these when stability is prioritized over feature completeness:

```cfg
seta rtx_rt_require 0
seta rtx_rt_dynamic_blas 0
seta rtx_rt_quality_preset 2
seta rtx_rt_dynamic_resolution 1
seta rtx_rt_adaptive_budget 1
```
