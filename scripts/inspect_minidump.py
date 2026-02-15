#!/usr/bin/env python3
"""
Lightweight minidump inspection for Q3RTX crash triage.

Requires the `minidump` Python package (already present in this environment).
"""

from __future__ import annotations

import argparse
import json
import logging
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def _find_latest_dump(search_roots: List[Path]) -> Optional[Path]:
    dumps: List[Path] = []
    for root in search_roots:
        if root.is_file() and root.suffix.lower() == ".dmp":
            dumps.append(root)
            continue
        if root.is_dir():
            dumps.extend(root.rglob("*.dmp"))
    if not dumps:
        return None
    dumps.sort(key=lambda p: p.stat().st_mtime)
    return dumps[-1]


def _module_for_address(modules: List[Any], addr: int) -> Tuple[Optional[str], Optional[int]]:
    for mod in modules:
        start = int(mod.baseaddress)
        end = int(mod.endaddress)
        if start <= addr < end:
            return mod.name, addr - start
    return None, None


def _enum_value(value: Any) -> Any:
    return getattr(value, "value", value)


@dataclass
class ThreadSummary:
    thread_id: int
    rip: Optional[int]
    module: Optional[str]
    offset: Optional[int]


@dataclass
class DumpSummary:
    dump_path: str
    exception_thread_id: Optional[int]
    exception_code: Optional[int]
    exception_code_name: Optional[str]
    exception_address: Optional[int]
    exception_module: Optional[str]
    exception_offset: Optional[int]
    access_type: Optional[str]
    access_address: Optional[int]
    module_count: int
    thread_count: int
    threads: List[ThreadSummary]


def inspect_dump(path: Path) -> DumpSummary:
    logging.getLogger().setLevel(logging.CRITICAL)

    from minidump.minidumpfile import MinidumpFile

    mdmp = MinidumpFile.parse(str(path))
    modules = mdmp.modules.modules if mdmp.modules else []
    threads = mdmp.threads.threads if mdmp.threads else []

    exc_thread_id: Optional[int] = None
    exc_code: Optional[int] = None
    exc_code_name: Optional[str] = None
    exc_addr: Optional[int] = None
    exc_module: Optional[str] = None
    exc_offset: Optional[int] = None
    access_type: Optional[str] = None
    access_addr: Optional[int] = None

    if mdmp.exception and mdmp.exception.exception_records:
        rec = mdmp.exception.exception_records[0]
        er = rec.ExceptionRecord
        exc_thread_id = int(rec.ThreadId)
        exc_code_obj = er.ExceptionCode
        exc_code = int(_enum_value(exc_code_obj))
        exc_code_name = str(exc_code_obj)
        exc_addr = int(er.ExceptionAddress)
        exc_module, exc_offset = _module_for_address(modules, exc_addr)

        info = list(getattr(er, "ExceptionInformation", []) or [])
        if info and exc_code == 0xC0000005:
            access_kind = int(info[0]) if len(info) >= 1 else -1
            if access_kind == 0:
                access_type = "read"
            elif access_kind == 1:
                access_type = "write"
            elif access_kind == 8:
                access_type = "execute"
            else:
                access_type = f"unknown({access_kind})"
            if len(info) >= 2:
                access_addr = int(info[1])

    thread_summaries: List[ThreadSummary] = []
    for t in threads:
        rip: Optional[int] = None
        mod_name: Optional[str] = None
        mod_off: Optional[int] = None
        ctx = getattr(t, "ContextObject", None)
        if ctx is not None and hasattr(ctx, "Rip"):
            rip = int(ctx.Rip)
            mod_name, mod_off = _module_for_address(modules, rip)
        thread_summaries.append(
            ThreadSummary(
                thread_id=int(t.ThreadId),
                rip=rip,
                module=mod_name,
                offset=mod_off,
            )
        )

    return DumpSummary(
        dump_path=str(path),
        exception_thread_id=exc_thread_id,
        exception_code=exc_code,
        exception_code_name=exc_code_name,
        exception_address=exc_addr,
        exception_module=exc_module,
        exception_offset=exc_offset,
        access_type=access_type,
        access_address=access_addr,
        module_count=len(modules),
        thread_count=len(threads),
        threads=thread_summaries,
    )


def _format_hex(value: Optional[int]) -> str:
    if value is None:
        return "n/a"
    return f"0x{value:016X}"


def _print_summary(summary: DumpSummary) -> None:
    print(f"Dump: {summary.dump_path}")
    print(
        f"Exception: {summary.exception_code_name} "
        f"({_format_hex(summary.exception_code)})"
    )
    print(
        f"Thread: {summary.exception_thread_id} "
        f"Address: {_format_hex(summary.exception_address)}"
    )
    if summary.exception_module:
        print(f"Module: {summary.exception_module} + 0x{summary.exception_offset:X}")
    if summary.access_type:
        print(
            f"Access: {summary.access_type} "
            f"{_format_hex(summary.access_address)}"
        )
    print(f"Modules: {summary.module_count} Threads: {summary.thread_count}")
    print("Thread RIPs:")
    for t in summary.threads:
        if t.rip is None:
            print(f"  tid={t.thread_id} rip=n/a")
        elif t.module:
            print(
                f"  tid={t.thread_id} rip={_format_hex(t.rip)} "
                f"{t.module}+0x{t.offset:X}"
            )
        else:
            print(f"  tid={t.thread_id} rip={_format_hex(t.rip)}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect a Q3RTX minidump")
    parser.add_argument("--dump", type=Path, help="Path to .dmp file")
    parser.add_argument(
        "--search-root",
        action="append",
        type=Path,
        default=[],
        help="Folder/file to search for latest dump when --dump is omitted",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()

    dump_path: Optional[Path] = args.dump
    if dump_path is None:
        roots = args.search_root or [
            Path("build/meson-debug/crashdumps"),
            Path("build/meson-release/crashdumps"),
            Path("."),
        ]
        dump_path = _find_latest_dump(roots)
        if dump_path is None:
            print("No dump file found.", flush=True)
            return 1

    if not dump_path.exists() or not dump_path.is_file():
        print(f"Dump file not found: {dump_path}", flush=True)
        return 1

    summary = inspect_dump(dump_path)
    if args.json:
        print(
            json.dumps(
                {
                    **asdict(summary),
                    "threads": [asdict(t) for t in summary.threads],
                },
                indent=2,
            )
        )
    else:
        _print_summary(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

