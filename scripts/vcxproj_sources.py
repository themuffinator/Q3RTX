#!/usr/bin/env python3
"""
Extract ClCompile sources from a .vcxproj with config/platform exclusion support.
Prints one workspace-relative path per line.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
import xml.etree.ElementTree as ET


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract source files from vcxproj")
    parser.add_argument("vcxproj", type=Path, help="Path to .vcxproj file")
    parser.add_argument("--config", default="Release", help="Build configuration name")
    parser.add_argument("--platform", default="x64", help="Build platform name")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Project root used to print relative paths",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="Workspace-relative file path to exclude (repeatable)",
    )
    return parser.parse_args()


def _match_condition(condition: str | None, config: str, platform: str) -> bool:
    if not condition:
        return False
    needle = f"{config}|{platform}".lower()
    return needle in condition.lower()


def _is_excluded_for_target(node: ET.Element, config: str, platform: str, ns: dict[str, str]) -> bool:
    for excluded in node.findall("ns:ExcludedFromBuild", ns):
        value = (excluded.text or "").strip().lower()
        if value not in {"true", "1"}:
            continue
        condition = excluded.get("Condition")
        if condition is None:
            return True
        if _match_condition(condition, config, platform):
            return True
    return False


def main() -> int:
    args = parse_args()

    vcxproj_path = args.vcxproj.resolve()
    if not vcxproj_path.exists():
        print(f"vcxproj not found: {vcxproj_path}", file=sys.stderr)
        return 1

    root = args.root.resolve()

    tree = ET.parse(vcxproj_path)
    doc = tree.getroot()
    if not doc.tag.startswith("{"):
        print("Unexpected vcxproj XML namespace", file=sys.stderr)
        return 1

    ns_uri = doc.tag[1 : doc.tag.find("}")]
    ns = {"ns": ns_uri}

    excludes = {Path(p).as_posix().lower() for p in args.exclude}
    seen: set[str] = set()
    out: list[str] = []

    for item in doc.findall(".//ns:ClCompile", ns):
        include = item.get("Include")
        if not include:
            continue

        if _is_excluded_for_target(item, args.config, args.platform, ns):
            continue

        abs_path = (vcxproj_path.parent / include).resolve()
        try:
            rel_path = abs_path.relative_to(root).as_posix()
        except ValueError:
            rel_path = abs_path.as_posix()

        key = rel_path.lower()
        if key in excludes:
            continue
        if key in seen:
            continue
        seen.add(key)
        out.append(rel_path)

    sys.stdout.write("\n".join(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
