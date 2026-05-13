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

import yaml
from deepdiff import DeepDiff

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
                    "target_val": str(list(diff["iterable_item_removed"].values()))[:100],
                }
            )

    return result


def _collect_files(root: str) -> dict[str, str]:
    """Return {relative_path: absolute_path} for all JSON/YAML files under root."""
    files = {}
    for dirpath, _, filenames in os.walk(root):
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

    return parser


def start(args=None):
    if args is None:
        args = get_parser(include_help=True).parse_args()

    extra_keys = set(args.exclude_keys) if args.exclude_keys else None

    print(f"Comparing:\n  source: {args.source}\n  target: {args.target}\n")

    result = compare(args.source, args.target, extra_keys)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print(f"{'=' * 80}")
    if result["missing_in_target"]:
        print(f"In source but not in target ({len(result['missing_in_target'])}):")
        for p in result["missing_in_target"]:
            print(f"  + {p}")

    if result["missing_in_source"]:
        print(f"In target but not in source ({len(result['missing_in_source'])}):")
        for p in result["missing_in_source"]:
            print(f"  - {p}")

    if result["changes"]:
        print(f"\nConfigurations with differences ({len(result['changes'])}):")
        for change in result["changes"]:
            print(f"\n  [{change['config_type']}] {change['name']} ({change['file']})")
            for diff in change["diffs"]:
                print(
                    f"    setting: {diff['setting']}"
                    f"  |  source: {diff['source_val']}"
                    f"  |  target: {diff['target_val']}"
                )

    print(f"\nTotal diffs: {result['diff_count']}")
    print(f"Summary written to: {args.output}")


if __name__ == "__main__":
    start()
