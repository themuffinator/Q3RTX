#!/usr/bin/env python3
"""
Create a packaged runtime folder for Q3RTX Meson builds and validate loader paths.

This script is intentionally conservative:
- It always stages the client executable and all renderer modules from the build dir.
- It attempts to discover dynamic dependencies and stage local runtime libraries.
- It writes a manifest and a loader validation report for CI/debugging.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple


WINDOWS_SYSTEM_DLLS = {
    "advapi32.dll",
    "bcrypt.dll",
    "cfgmgr32.dll",
    "comctl32.dll",
    "crypt32.dll",
    "d3d12.dll",
    "dbghelp.dll",
    "dwmapi.dll",
    "gdi32.dll",
    "imm32.dll",
    "iphlpapi.dll",
    "kernel32.dll",
    "msvcp140.dll",
    "msvcp140_1.dll",
    "msvcp140_2.dll",
    "ntdll.dll",
    "ole32.dll",
    "opengl32.dll",
    "powrprof.dll",
    "rpcrt4.dll",
    "secur32.dll",
    "setupapi.dll",
    "shell32.dll",
    "ucrtbase.dll",
    "user32.dll",
    "userenv.dll",
    "vcruntime140.dll",
    "vcruntime140_1.dll",
    "version.dll",
    "vulkan-1.dll",
    "winmm.dll",
    "ws2_32.dll",
    "wldap32.dll",
}


def detect_platform(requested: str) -> str:
    if requested != "auto":
        return requested
    if sys.platform.startswith("win"):
        return "windows"
    if sys.platform == "darwin":
        return "macos"
    return "linux"


def shared_ext(platform_name: str) -> str:
    if platform_name == "windows":
        return ".dll"
    if platform_name == "macos":
        return ".dylib"
    return ".so"


def run_command(cmd: List[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def find_executable(build_dir: Path, platform_name: str) -> Path:
    if platform_name == "windows":
        candidates = sorted(build_dir.glob("q3rtx*.exe"))
        if not candidates:
            raise FileNotFoundError(f"No q3rtx executable found in {build_dir}")

        preferred = ["q3rtx.x64.exe", "q3rtx.arm64.exe", "q3rtx.exe"]
        for name in preferred:
            for candidate in candidates:
                if candidate.name.lower() == name:
                    return candidate
        return candidates[0]

    exact = build_dir / "q3rtx"
    if exact.is_file():
        return exact

    candidates = sorted(p for p in build_dir.glob("q3rtx*") if p.is_file() and os.access(p, os.X_OK))
    if not candidates:
        raise FileNotFoundError(f"No q3rtx executable found in {build_dir}")
    return candidates[0]


def find_renderer_modules(build_dir: Path, platform_name: str) -> List[Path]:
    ext = shared_ext(platform_name)
    modules = sorted(build_dir.glob(f"q3rtx_rtx_*{ext}"))
    if not modules:
        raise FileNotFoundError(f"No RT renderer module found in {build_dir} (*{ext})")
    return modules


def find_all_renderer_modules(build_dir: Path, platform_name: str) -> List[Path]:
    ext = shared_ext(platform_name)
    return sorted(build_dir.glob(f"q3rtx_*_*{ext}"))


def parse_windows_dependents(binary: Path) -> Optional[List[str]]:
    dumpbin = shutil.which("dumpbin")
    if not dumpbin:
        return None

    proc = run_command([dumpbin, "/DEPENDENTS", str(binary)])
    text = proc.stdout + "\n" + proc.stderr
    if proc.returncode != 0:
        return []

    deps: List[str] = []
    in_list = False
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if "Image has the following dependencies" in line:
            in_list = True
            continue
        if in_list:
            if not line.strip():
                # End after first blank line once parsing started.
                if deps:
                    break
                continue
            match = re.match(r"^\s*([A-Za-z0-9._-]+\.dll)\s*$", line, flags=re.IGNORECASE)
            if match:
                deps.append(match.group(1))
    return deps


def parse_linux_dependents(binary: Path) -> List[Tuple[str, Optional[str], bool]]:
    proc = run_command(["ldd", str(binary)])
    text = proc.stdout + "\n" + proc.stderr
    if proc.returncode != 0:
        return []

    deps: List[Tuple[str, Optional[str], bool]] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        if "=>" in line:
            left, right = line.split("=>", 1)
            dep_name = left.strip()
            rhs = right.strip()
            if rhs.startswith("not found"):
                deps.append((dep_name, None, False))
                continue
            dep_path = rhs.split("(", 1)[0].strip()
            deps.append((dep_name, dep_path, True))
            continue

        # ldd may emit absolute loader path lines without '=>'
        if line.startswith("/"):
            dep_path = line.split("(", 1)[0].strip()
            deps.append((Path(dep_path).name, dep_path, True))

    return deps


def parse_macos_dependents(binary: Path) -> List[str]:
    proc = run_command(["otool", "-L", str(binary)])
    text = proc.stdout + "\n" + proc.stderr
    if proc.returncode != 0:
        return []

    deps: List[str] = []
    lines = text.splitlines()
    for raw_line in lines[1:]:
        line = raw_line.strip()
        if not line:
            continue
        deps.append(line.split(" (", 1)[0].strip())
    return deps


def resolve_dependency(dep: str, search_dirs: Iterable[Path]) -> Optional[Path]:
    dep_path = Path(dep)
    if dep_path.is_absolute() and dep_path.is_file():
        return dep_path

    dep_name = dep_path.name
    for directory in search_dirs:
        candidate = directory / dep_name
        if candidate.is_file():
            return candidate

    return None


def is_local_windows_dependency(dep: str) -> bool:
    dep_l = dep.lower()
    if dep_l in WINDOWS_SYSTEM_DLLS:
        return False
    return dep_l.startswith("q3rtx_") or dep_l.startswith("sdl2") or dep_l.startswith("vulkan")


def stage_copy(src: Path, output_dir: Path, copied: Dict[str, str]) -> Path:
    dst = output_dir / src.name
    if dst.name not in copied:
        shutil.copy2(src, dst)
        copied[dst.name] = str(src.resolve())
    return dst


def validate_loader_path(output_dir: Path, renderer_module: Path) -> Tuple[bool, str]:
    expected = output_dir / renderer_module.name
    ok = expected.is_file()
    report_lines = [
        f"Expected renderer module probe path: {expected}",
        f"Module present: {'yes' if ok else 'no'}",
        "",
        "Notes:",
        "- FS_LoadLibrary probes Sys_Pwd() first, then static search paths.",
        "- Packaging keeps renderer modules alongside the executable to satisfy first-probe load.",
    ]
    return ok, "\n".join(report_lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Package Q3RTX runtime outputs and validate loader paths.")
    parser.add_argument("--build-dir", required=True, type=Path, help="Meson build output directory")
    parser.add_argument("--output-dir", required=True, type=Path, help="Package output directory")
    parser.add_argument(
        "--platform",
        default="auto",
        choices=["auto", "windows", "linux", "macos"],
        help="Target platform override",
    )
    parser.add_argument(
        "--extra-runtime-dir",
        action="append",
        default=[],
        help="Additional directory to search for runtime dependencies",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail when unresolved local dependencies are detected",
    )
    args = parser.parse_args()

    build_dir = args.build_dir.resolve()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    platform_name = detect_platform(args.platform)
    exe = find_executable(build_dir, platform_name)
    renderer_modules = find_renderer_modules(build_dir, platform_name)
    extra_modules = find_all_renderer_modules(build_dir, platform_name)

    copied: Dict[str, str] = {}
    staged_queue: List[Path] = []
    staged_seen: Set[str] = set()
    dep_graph: Dict[str, List[str]] = {}
    unresolved: Set[str] = set()
    scanner_notes: List[str] = []

    def stage(src: Path) -> Path:
        dst = stage_copy(src.resolve(), output_dir, copied)
        key = dst.name.lower()
        if key not in staged_seen:
            staged_seen.add(key)
            staged_queue.append(dst)
        return dst

    staged_exe = stage(exe)
    for module in extra_modules:
        stage(module)

    search_dirs = [build_dir, output_dir] + [Path(p).resolve() for p in args.extra_runtime_dir]

    while staged_queue:
        binary = staged_queue.pop(0)
        bin_key = binary.name

        if platform_name == "windows":
            deps = parse_windows_dependents(binary)
            if deps is None:
                scanner_notes.append(f"{bin_key}: dumpbin not available; dependency scan skipped")
                continue
            dep_graph[bin_key] = deps

            for dep in deps:
                resolved = resolve_dependency(dep, search_dirs)
                if resolved:
                    stage(resolved)
                elif is_local_windows_dependency(dep):
                    unresolved.add(dep)
            continue

        if platform_name == "linux":
            deps = parse_linux_dependents(binary)
            dep_graph[bin_key] = []
            for dep_name, dep_path, found in deps:
                dep_graph[bin_key].append(dep_name if not dep_path else f"{dep_name} => {dep_path}")
                if not found:
                    unresolved.add(dep_name)
                    continue

                if dep_path:
                    resolved = resolve_dependency(dep_path, search_dirs)
                    if resolved and resolved.parent in search_dirs:
                        stage(resolved)
            continue

        # macOS
        deps = parse_macos_dependents(binary)
        dep_graph[bin_key] = deps
        for dep in deps:
            resolved = resolve_dependency(dep, search_dirs)
            if resolved and resolved.parent in search_dirs:
                stage(resolved)

    loader_ok, loader_report = validate_loader_path(output_dir, renderer_modules[0])

    manifest = {
        "platform": platform_name,
        "build_dir": str(build_dir),
        "output_dir": str(output_dir),
        "executable": staged_exe.name,
        "renderer_modules": [m.name for m in renderer_modules],
        "copied_files": sorted(copied.keys()),
        "copied_from": copied,
        "dependencies": dep_graph,
        "unresolved_local_dependencies": sorted(unresolved),
        "scanner_notes": scanner_notes,
        "loader_validation_ok": loader_ok,
    }

    manifest_path = output_dir / "package-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (output_dir / "loader-validation.txt").write_text(loader_report + "\n", encoding="utf-8")

    print(f"Packaged executable: {staged_exe.name}")
    print(f"Packaged renderer modules: {', '.join(sorted({m.name for m in renderer_modules}))}")
    print(f"Copied files: {len(copied)}")
    if unresolved:
        print("Unresolved local dependencies:")
        for dep in sorted(unresolved):
            print(f"  - {dep}")

    if not loader_ok:
        print("ERROR: Loader-path validation failed (renderer module missing from package).", file=sys.stderr)
        return 1

    if args.strict and unresolved:
        print("ERROR: Strict packaging mode failed due to unresolved local dependencies.", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
