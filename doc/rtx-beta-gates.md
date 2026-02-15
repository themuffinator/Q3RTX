# Q3RTX Beta Go/No-Go Gates

Last updated: 2026-02-15  
Scope: objective criteria for promoting `rendererrtx` from alpha validation to beta branch readiness.

## Gate summary

A beta promotion decision requires all `required` gates to pass.

| Gate ID | Area | Type | Requirement |
|---|---|---|---|
| BG-001 | Build/package | required | Cross-platform build + packaging workflow green for target branch |
| BG-002 | Startup stability | required | RT and non-RT startup smoke gates pass on required environments |
| BG-003 | Crash budget | required | No open `S0`; no more than one open `S1` with approved workaround |
| BG-004 | Visual correctness | required | Core matrix cases (`TC-REN-*`, `TC-LIT-*`, `TC-UI-*`) pass on primary environment |
| BG-005 | Gameplay readability | required | `TC-GAME-*` passes with no blocking regressions |
| BG-006 | Performance | required | Preset targets in `doc/rtx-performance-targets.md` meet goals on Tier-2 |
| BG-007 | Documentation | required | M9 docs current and linked from implementation plan |
| BG-008 | Known issues | required | `doc/rtx-known-issues.md` updated and triaged |
| BG-009 | Driver coverage | required | `doc/rtx-driver-matrix.md` has current known-good/known-bad rows for shipping targets |

## Decision rubric

### Go

1. All required gates pass.
2. Open issues are `S2+` only and documented with workarounds.

### Conditional go

1. Exactly one required gate is marginal but has an approved mitigation and owner.
2. Follow-up deadline is committed before branch cut.

### No-go

1. Any required gate fails with no credible short-term mitigation.
2. Any unresolved `S0`, or multiple unresolved `S1` issues.

## Required evidence package

1. Latest CI links/artifacts for packaging and smoke jobs.
2. Manual matrix run report for primary environment.
3. Performance run report for Tier-2 target.
4. Updated known-issues list with owner/next action.
5. Signed release checklist (`doc/rtx-release-checklist.md`).

## Approval record template

| Date | Decision | Approvers | Blockers (if any) | Follow-up actions |
|---|---|---|---|---|
| 2026-02-15 | pending | pending | pending | pending |
