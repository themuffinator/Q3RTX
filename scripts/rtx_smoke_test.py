#!/usr/bin/env python3
"""
Runtime smoke harness for Q3RTX renderer startup checks.

Designed for CI and local automation:
- launches the client for a fixed interval,
- inspects qconsole log output for expected/forbidden patterns,
- supports optional skip behavior when external game data is unavailable.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import List


DEFAULT_FORBIDDEN = [
    "fatal error occurred",
    "recursive error",
    "err_fatal",
    "server fatal crashed",
    "vk_error_device_lost",
]


def normalize_path(value: str) -> str:
    return str(Path(value).resolve())


def ensure_minimal_default_cfg(basepath: Path) -> None:
    baseq3 = basepath / "baseq3"
    baseq3.mkdir(parents=True, exist_ok=True)
    default_cfg = baseq3 / "default.cfg"
    if not default_cfg.exists():
        default_cfg.write_text("seta com_introplayed \"1\"\n", encoding="utf-8")


def terminate_process(proc: subprocess.Popen[bytes]) -> None:
    if proc.poll() is not None:
        return
    proc.terminate()
    try:
        proc.wait(timeout=5)
        return
    except subprocess.TimeoutExpired:
        pass
    proc.kill()
    proc.wait(timeout=5)


def run_single_smoke(
    binary: Path,
    renderer: str,
    basepath: Path,
    homepath: Path,
    seconds: int,
    map_name: str,
    extra_args: List[str],
) -> dict:
    home_baseq3 = homepath / "baseq3"
    home_baseq3.mkdir(parents=True, exist_ok=True)
    log_path = home_baseq3 / "qconsole.log"
    if log_path.exists():
        log_path.unlink()

    cmd: List[str] = [
        str(binary),
        "+set", "fs_basepath", normalize_path(str(basepath)),
        "+set", "fs_homepath", normalize_path(str(homepath)),
        "+set", "cl_renderer", renderer,
        "+set", "r_fullscreen", "0",
        "+set", "r_noborder", "1",
        "+set", "in_nograb", "1",
        "+set", "s_initsound", "0",
        "+set", "developer", "1",
        "+set", "com_introplayed", "1",
        "+set", "sv_pure", "0",
    ]

    if renderer == "rtx":
        cmd += [
            "+set", "rtx_rt_require", "0",
            "+set", "rtx_rt_mode", "2",
        ]

    if map_name and map_name.lower() != "none":
        cmd += ["+devmap", map_name]

    cmd += extra_args

    proc = subprocess.Popen(
        cmd,
        cwd=str(basepath),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    start = time.time()
    exited_early = False
    exit_code = None
    while time.time() - start < seconds:
        exit_code = proc.poll()
        if exit_code is not None:
            exited_early = True
            break
        time.sleep(0.2)

    terminate_process(proc)
    if exit_code is None:
        exit_code = proc.returncode

    log_text = ""
    if log_path.exists():
        try:
            log_text = log_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            log_text = ""

    return {
        "renderer": renderer,
        "command": cmd,
        "seconds": seconds,
        "exited_early": exited_early,
        "exit_code": exit_code,
        "log_path": str(log_path),
        "log_exists": log_path.exists(),
        "log_text": log_text,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Q3RTX renderer startup smoke test")
    parser.add_argument("--binary", required=True, type=Path, help="Path to q3rtx executable")
    parser.add_argument("--renderer", required=True, help="Renderer name (rtx/opengl/opengl2/vulkan)")
    parser.add_argument("--basepath", type=Path, help="Quake 3 base path containing baseq3")
    parser.add_argument("--homepath", type=Path, help="Writable home path")
    parser.add_argument("--seconds", type=int, default=10, help="Runtime interval before termination")
    parser.add_argument("--map", default="none", help="Map to devmap (or 'none')")
    parser.add_argument("--extra-arg", action="append", default=[], help="Extra command-line argument token")
    parser.add_argument("--forbid", action="append", default=[], help="Extra forbidden log pattern (case-insensitive)")
    parser.add_argument("--expect", action="append", default=[], help="Extra required log pattern (case-insensitive)")
    parser.add_argument("--report", type=Path, help="Optional JSON report path")
    parser.add_argument(
        "--skip-if-basepath-missing",
        action="store_true",
        help="Return success when basepath is missing/unusable",
    )
    args = parser.parse_args()

    def write_report(payload: dict) -> None:
        if not args.report:
            return
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    binary = args.binary.resolve()
    if not binary.is_file():
        write_report(
            {
                "renderer": args.renderer,
                "binary": str(binary),
                "status": "error",
                "failures": [f"binary not found: {binary}"],
            }
        )
        print(f"ERROR: binary not found: {binary}", file=sys.stderr)
        return 1

    if args.basepath:
        basepath = args.basepath.resolve()
    else:
        env_basepath = os.environ.get("Q3RTX_BASEPATH", "").strip()
        basepath = Path(env_basepath).resolve() if env_basepath else None

    if basepath is None or not basepath.exists():
        if args.skip_if_basepath_missing:
            write_report(
                {
                    "renderer": args.renderer,
                    "binary": str(binary),
                    "status": "skipped",
                    "reason": "basepath missing",
                }
            )
            print("SKIPPED: basepath was not provided or does not exist.")
            return 0
        write_report(
            {
                "renderer": args.renderer,
                "binary": str(binary),
                "status": "error",
                "failures": ["basepath was not provided or does not exist"],
            }
        )
        print("ERROR: basepath was not provided or does not exist.", file=sys.stderr)
        return 1

    ensure_minimal_default_cfg(basepath)
    homepath = args.homepath.resolve() if args.homepath else (basepath / ".q3rtx-smoke-home")
    homepath.mkdir(parents=True, exist_ok=True)

    result = run_single_smoke(
        binary=binary,
        renderer=args.renderer,
        basepath=basepath,
        homepath=homepath,
        seconds=max(1, args.seconds),
        map_name=args.map,
        extra_args=args.extra_arg,
    )

    log_l = result["log_text"].lower()
    required = [
        f'cl_initref: cl_renderer is "{args.renderer}"',
        "cl_initref: loaded renderer module from",
    ]
    required.extend([p.lower() for p in args.expect])
    forbidden = DEFAULT_FORBIDDEN + [p.lower() for p in args.forbid]

    failures: List[str] = []

    if not result["log_exists"]:
        failures.append(f"missing qconsole log at {result['log_path']}")

    if result["exited_early"] and result["exit_code"] not in (0, None):
        failures.append(f"process exited early with code {result['exit_code']}")

    for pattern in required:
        if pattern not in log_l:
            failures.append(f"missing expected log pattern: {pattern}")

    for pattern in forbidden:
        if pattern and pattern in log_l:
            failures.append(f"forbidden log pattern detected: {pattern}")

    report = {
        "renderer": args.renderer,
        "binary": str(binary),
        "basepath": str(basepath),
        "homepath": str(homepath),
        "seconds": args.seconds,
        "map": args.map,
        "result": {
            "exited_early": result["exited_early"],
            "exit_code": result["exit_code"],
            "log_path": result["log_path"],
        },
        "status": "failed" if failures else "passed",
        "failures": failures,
    }
    write_report(report)

    if failures:
        print("Smoke test failed:")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print(f"Smoke test passed for renderer '{args.renderer}'")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
