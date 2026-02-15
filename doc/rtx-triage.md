# Q3RTX Bug Triage Guide

Last updated: 2026-02-15  
Scope: issue labeling, severity scoring, and response workflow for `rendererrtx` and integration paths.

## Label taxonomy

### Area labels

- `area:rendererrtx`
- `area:renderer-integration`
- `area:vulkan-loader`
- `area:materials`
- `area:lighting`
- `area:temporal-denoise`
- `area:performance`
- `area:packaging-ci`
- `area:docs`

### Platform labels

- `platform:windows`
- `platform:linux`
- `platform:macos`
- `platform:all`

### Type labels

- `type:crash`
- `type:visual-regression`
- `type:performance-regression`
- `type:compatibility`
- `type:gameplay-readability`
- `type:build-break`
- `type:test-gap`

### Severity labels

- `severity:S0`
- `severity:S1`
- `severity:S2`
- `severity:S3`
- `severity:S4`

### Lifecycle labels

- `state:needs-repro`
- `state:triaged`
- `state:in-progress`
- `state:blocked`
- `state:ready-for-verify`
- `state:verified`
- `state:wont-fix`

### Release impact labels

- `release:alpha-blocker`
- `release:beta-blocker`
- `release:post-beta`

## Severity rubric

| Severity | Definition | Examples | Target response |
|---|---|---|---|
| S0 | Engine unusable or data loss risk | startup crash on supported primary environment, corrupted save/config output | same day |
| S1 | Major feature broken, no acceptable workaround | consistent `VK_ERROR_DEVICE_LOST` on default path, severe gameplay readability failure | 1 business day |
| S2 | Significant degradation with workaround | major visual artifact with cvar workaround, large perf regression on one tier | 3 business days |
| S3 | Moderate issue, limited impact | isolated map artifact, non-default feature misbehavior | 1 week |
| S4 | Minor polish/doc/tooling | typo, low-impact logging issue, optional UI cleanup | backlog |

## Priority mapping

| Priority | Rule |
|---|---|
| P0 | `severity:S0` or any `release:*blocker` in current milestone |
| P1 | `severity:S1` |
| P2 | `severity:S2` |
| P3 | `severity:S3` |
| P4 | `severity:S4` |

## Triage workflow

1. Intake
   - Require reproduction steps, build identifier, platform/GPU/driver, launch args, and logs/screenshots.
2. Repro pass
   - Set `state:needs-repro` until behavior is reproduced on at least one environment from `doc/rtx-test-matrix.md`.
3. Classification
   - Assign exactly one area label, one type label, one severity label, and one platform label.
4. Milestone assignment
   - Add `release:*` impact label if it can block alpha/beta gates.
5. Ownership
   - Assign an owner and link the corresponding matrix case IDs.
6. Verification
   - On fix, move to `state:ready-for-verify`; close only after evidence is attached.

## Required issue fields

1. Build ID or commit hash.
2. Environment (OS, GPU, driver/runtime).
3. Command line and relevant cvars.
4. Expected vs actual behavior.
5. Repro frequency (`always`, `intermittent`, `%`).
6. Artifacts (`qconsole.log`, screenshot/video, crash dump if available).

## Triage meeting cadence

1. Daily quick triage for `S0/S1`.
2. Twice-weekly full backlog triage.
3. Pre-release gate review for all open `release:*blocker` items.
