#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Offline drift/compare tool.

Compares two local IntuneCD backup directories without making any API calls.
Useful when you want to check for drift between two environments (e.g. dev vs
prod backups) or between a backup and a known-good baseline, without needing
any write permissions.
"""

import argparse
import json
import os
import re
import sys

import yaml
from deepdiff import DeepDiff


def _color_enabled() -> bool:
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("FORCE_COLOR"):
        return True
    return sys.stdout.isatty()


class _C:
    """ANSI color codes. All empty strings when color is disabled."""

    RESET = ""
    BOLD = ""
    DIM = ""
    RED = ""
    GREEN = ""
    YELLOW = ""
    CYAN = ""
    MAGENTA = ""

    @classmethod
    def enable(cls):
        cls.RESET = "\033[0m"
        cls.BOLD = "\033[1m"
        cls.DIM = "\033[2m"
        cls.RED = "\033[31m"
        cls.GREEN = "\033[32m"
        cls.YELLOW = "\033[33m"
        cls.CYAN = "\033[36m"
        cls.MAGENTA = "\033[35m"


# Keys that are Intune-generated metadata and should not affect drift results.
# Mirrors the logic in IntuneCDBase.remove_keys().
_METADATA_KEYS = {
    "id",
    "version",
    "topicIdentifier",
    "certificate",
    "createdDateTime",
    "lastModifiedDateTime",
    "isAssigned",
    "@odata.context",
    "scheduledActionConfigurations@odata.context",
    "scheduledActionsForRule@odata.context",
    "sourceId",
    "supportsScopeTags",
    "companyCodes",
    "isGlobalScript",
    "highestAvailableVersion",
    "token",
    "lastSyncDateTime",
    "isReadOnly",
    "secretReferenceValueId",
    "isEncrypted",
    "modifiedDateTime",
    "deployedAppCount",
    "intunecd_name",
    "deviceHealthScriptType",
}


def _strip_keys(data: dict, extra_keys: set = None) -> dict:
    """Recursively remove metadata-only keys from a dict."""
    keys_to_remove = _METADATA_KEYS | (extra_keys or set())
    if isinstance(data, dict):
        return {
            k: _strip_keys(v, extra_keys)
            for k, v in data.items()
            if k not in keys_to_remove
        }
    if isinstance(data, list):
        return [_strip_keys(item, extra_keys) for item in data]
    return data


def _load_file(path: str) -> dict | None:
    """Load a JSON or YAML backup file."""
    try:
        with open(path, encoding="utf-8") as f:
            if path.endswith(".yaml"):
                return json.loads(json.dumps(yaml.safe_load(f)))
            return json.load(f)
    except Exception as e:
        print(f"[WARNING] Could not load {path}: {e}")
        return None


def _process_diffs(diff: dict) -> list:
    """Convert a DeepDiff result into a simple list of change dicts."""
    result = []

    def _setting(key: str) -> str:
        match = re.search(r"\[(.+)\]", key)
        return (
            match.group(1).split("[")[-1].replace("'", "").replace('"', "")
            if match
            else key
        )

    if "values_changed" in diff:
        for key, val in diff["values_changed"].items():
            result.append(
                {
                    "setting": _setting(key),
                    "source_val": str(val["new_value"])[:100],
                    "target_val": str(val["old_value"])[:100],
                }
            )

    if "type_changes" in diff:
        for key, val in diff["type_changes"].items():
            result.append(
                {
                    "setting": _setting(key),
                    "source_val": str(val["new_value"])[:100],
                    "target_val": str(val["old_value"])[:100],
                }
            )

    if "iterable_item_added" in diff:
        for key in diff["iterable_item_added"]:
            result.append(
                {
                    "setting": _setting(key),
                    "source_val": str(list(diff["iterable_item_added"].values()))[:100],
                    "target_val": "",
                }
            )

    if "iterable_item_removed" in diff:
        for key in diff["iterable_item_removed"]:
            result.append(
                {
                    "setting": _setting(key),
                    "source_val": "",
                    "target_val": str(list(diff["iterable_item_removed"].values()))[
                        :100
                    ],
                }
            )

    return result


def _collect_files(root: str) -> dict[str, str]:
    """Return {relative_path: absolute_path} for all JSON/YAML files under root."""
    files = {}
    skip_dirs = {"__archive__"}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in skip_dirs]
        for filename in filenames:
            if filename.endswith((".json", ".yaml")):
                abs_path = os.path.join(dirpath, filename)
                rel_path = os.path.relpath(abs_path, root)
                files[rel_path] = abs_path
    return files


def _config_type_from_path(rel_path: str) -> str:
    """Derive a human-readable config type from the relative file path."""
    parts = rel_path.replace("\\", "/").split("/")
    return parts[0] if len(parts) > 1 else "Unknown"


def compare(source: str, target: str, extra_keys: set = None) -> dict:
    """
    Compare two backup directories.

    Args:
        source: Path to the source backup (e.g. dev).
        target: Path to the target backup (e.g. prod).
        extra_keys: Additional keys to strip before comparing.

    Returns:
        A summary dict with diff_count, changes, missing_in_target, missing_in_source.
    """
    source_files = _collect_files(source)
    target_files = _collect_files(target)

    source_keys = set(source_files)
    target_keys = set(target_files)

    missing_in_target = sorted(source_keys - target_keys)
    missing_in_source = sorted(target_keys - source_keys)
    common = source_keys & target_keys

    diff_count = len(missing_in_target) + len(missing_in_source)
    changes = []

    for rel_path in sorted(common):
        source_data = _load_file(source_files[rel_path])
        target_data = _load_file(target_files[rel_path])

        if source_data is None or target_data is None:
            continue

        source_clean = _strip_keys(source_data, extra_keys)
        target_clean = _strip_keys(target_data, extra_keys)

        raw_diff = DeepDiff(target_clean, source_clean, ignore_order=True)
        if not raw_diff:
            continue

        diffs = _process_diffs(raw_diff)
        if not diffs:
            continue

        config_type = _config_type_from_path(rel_path)
        name_source = source_data[0] if isinstance(source_data, list) else source_data
        name = (
            (name_source.get("displayName") or name_source.get("name"))
            if isinstance(name_source, dict)
            else None
        ) or os.path.splitext(os.path.basename(rel_path))[0]

        diff_count += len(diffs)
        changes.append(
            {
                "file": rel_path,
                "config_type": config_type,
                "name": name,
                "diffs": diffs,
            }
        )

    return {
        "type": "compare_summary",
        "source": source,
        "target": target,
        "diff_count": diff_count,
        "missing_in_target": missing_in_target,
        "missing_in_source": missing_in_source,
        "changes": changes,
    }


def get_parser(include_help=True):
    parser = argparse.ArgumentParser(
        description=(
            "Compare two IntuneCD backup directories for drift. "
            "No API calls are made — works entirely on local files."
        ),
        add_help=include_help,
    )
    parser.add_argument(
        "-s",
        "--source",
        help="Path to the source backup directory (e.g. dev backup)",
        required=True,
    )
    parser.add_argument(
        "-t",
        "--target",
        help="Path to the target backup directory (e.g. prod backup)",
        required=True,
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Path to write the JSON comparison summary. Defaults to compare_summary.json in the current directory.",
        default="compare_summary.json",
    )
    parser.add_argument(
        "--exclude-keys",
        help="Additional keys to strip before comparing, separated by space.",
        nargs="+",
    )
    parser.add_argument(
        "--no-color",
        help="Disable colored output. Color is also disabled when stdout is not a TTY or NO_COLOR is set.",
        action="store_true",
    )
    parser.add_argument(
        "--html",
        help=(
            "Also write a self-contained HTML report alongside the JSON output. "
            "The HTML file uses the same path as -o with a .html extension."
        ),
        action="store_true",
    )

    return parser


def start(args=None):
    if args is None:
        args = get_parser(include_help=True).parse_args()

    extra_keys = set(args.exclude_keys) if args.exclude_keys else None

    use_color = False if getattr(args, "no_color", False) else _color_enabled()
    if use_color:
        _C.enable()

    print(
        f"Comparing:\n  {_C.BOLD}source:{_C.RESET} {args.source}\n"
        f"  {_C.BOLD}target:{_C.RESET} {args.target}\n"
    )

    result = compare(args.source, args.target, extra_keys)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    html_path = None
    if getattr(args, "html", False):
        from .intunecdlib.compare_html import render_html

        base, _ = os.path.splitext(args.output)
        html_path = f"{base}.html"
        with open(html_path, "w", encoding="utf-8") as f:
            _ = f.write(render_html(result))

    print(f"{_C.DIM}{'=' * 80}{_C.RESET}")
    if result["missing_in_target"]:
        print(
            f"{_C.BOLD}In source but not in target "
            f"({len(result['missing_in_target'])}):{_C.RESET}"
        )
        for p in result["missing_in_target"]:
            print(f"  {_C.GREEN}+ {p}{_C.RESET}")

    if result["missing_in_source"]:
        print(
            f"{_C.BOLD}In target but not in source "
            f"({len(result['missing_in_source'])}):{_C.RESET}"
        )
        for p in result["missing_in_source"]:
            print(f"  {_C.RED}- {p}{_C.RESET}")

    if result["changes"]:
        print(
            f"\n{_C.BOLD}Configurations with differences "
            f"({len(result['changes'])}):{_C.RESET}"
        )
        for change in result["changes"]:
            print(
                f"\n  {_C.CYAN}[{change['config_type']}]{_C.RESET} "
                f"{_C.BOLD}{change['name']}{_C.RESET} "
                f"{_C.DIM}({change['file']}){_C.RESET}"
            )
            for diff in change["diffs"]:
                print(
                    f"    {_C.DIM}setting:{_C.RESET} {_C.YELLOW}{diff['setting']}{_C.RESET}"
                    f"  {_C.DIM}|{_C.RESET}  {_C.DIM}source:{_C.RESET} {_C.GREEN}{diff['source_val']}{_C.RESET}"
                    f"  {_C.DIM}|{_C.RESET}  {_C.DIM}target:{_C.RESET} {_C.RED}{diff['target_val']}{_C.RESET}"
                )

    total_color = _C.GREEN if result["diff_count"] == 0 else _C.YELLOW
    print(
        f"\n{_C.BOLD}Total diffs:{_C.RESET} {total_color}{result['diff_count']}{_C.RESET}"
    )
    print(f"{_C.BOLD}Summary written to:{_C.RESET} {args.output}")
    if html_path:
        print(f"{_C.BOLD}HTML report written to:{_C.RESET} {html_path}")


if __name__ == "__main__":
    start()
