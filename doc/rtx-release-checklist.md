# Q3RTX Alpha Release Checklist

Last updated: 2026-02-15  
Scope: alpha milestone readiness for `rendererrtx` branch validation.

## Build and packaging gates

| Check | Status | Evidence |
|---|---|---|
| Windows Meson debug build | [x] | local `build/meson-debug` build on 2026-02-15 |
| Renderer module artifact produced (`q3rtx_rtx_<arch>`) | [x] | `build/meson-debug/q3rtx_rtx_x86_64.dll` |
| Packaging script stages executable + modules | [x] | `scripts/rtx_package.py` |
| Loader-path validation report generated | [x] | `build/package-local-m8/loader-validation.txt` |
| Cross-platform packaging workflow defined | [x] | `.github/workflows/rtx-meson-hardening.yml` |

## Runtime and regression gates

| Check | Status | Evidence |
|---|---|---|
| `cl_renderer rtx` startup diagnostics are actionable | [x] | `code/client/cl_main.c`, `code/qcommon/files.c` |
| Capability fallback/strict-fail controls documented | [x] | `doc/rtx-capability-gating.md` |
| Smoke harness for RT startup exists | [x] | `scripts/rtx_smoke_test.py` |
| Non-RT renderer startup gates exist (`opengl`, `opengl2`, `vulkan`) | [x] | `scripts/rtx_smoke_test.py`, workflow smoke step |
| Known issues/workarounds documented | [x] | `doc/rtx-known-issues.md` |

## QA/documentation gates

| Check | Status | Evidence |
|---|---|---|
| Manual matrix documented | [x] | `doc/rtx-test-matrix.md` |
| Triage severity/label rubric documented | [x] | `doc/rtx-triage.md` |
| User cvar guide published | [x] | `doc/rtx-cvars.md` |
| Developer architecture overview published | [x] | `doc/rtx-architecture.md` |
| Driver compatibility matrix published | [x] | `doc/rtx-driver-matrix.md` |
| Performance target document published | [x] | `doc/rtx-performance-targets.md` |
| Beta go/no-go gates documented | [x] | `doc/rtx-beta-gates.md` |

## Alpha disposition

`GO` for controlled alpha validation with documented known issues and mitigations.

## Sign-off

| Role | Decision | Name | Date |
|---|---|---|---|
| Rendering engineering | approved | Codex implementation pass | 2026-02-15 |
| QA process/doc readiness | approved | Codex implementation pass | 2026-02-15 |
