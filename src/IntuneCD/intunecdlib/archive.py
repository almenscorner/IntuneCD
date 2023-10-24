#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module moves files to archive during backup if they have been removed from Intune.
"""

import os
import shutil
from datetime import datetime

# Folders to exclude from archving
exclude = set(
    [
        "Management Intents",
        "archive",
        "__archive__",
        "Assignment Report",
        "Autopilot Devices",
    ]
)
# Date tag for archive folder
date_tag = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def archive(path, file, root) -> None:
    """Moves a file to the archive folder.

    Args:
        path (_str_): path to current folder
        file (_str_): file to archive
        root (_str_): root of the file
    """
    if not os.path.exists(f"{path}/__archive__/{date_tag}"):
        os.makedirs(f"{path}/__archive__/{date_tag}")
    shutil.move(
        os.path.join(root, file),
        os.path.join(path, f"__archive__/{date_tag}", file),
    )


def move_to_archive(path, created_files, output) -> None:
    """Moves a file to the archive folder.

    Args:
        path (_str_): path to current folder
        created_files (_list_): list of created files during backup
        output (_str_): format the file is in
    """
    if not os.path.exists(f"{path}/__archive__"):
        os.makedirs(f"{path}/__archive__/")

    for root, dirs, files in os.walk(path, topdown=True):
        # Remove excluded folders from dirs
        dirs[:] = [d for d in dirs if d not in exclude]
        for file in files:
            # if json is in root, skip it and move on
            if file.endswith(".json") and root == path:
                continue
            if file.endswith(".yaml") or file.endswith(".json"):
                # if file is not in created_files, archive it
                if file.replace(f".{output}", "") not in created_files:
                    archive(path, file, root)

    # Check if Management Intents folder exists
    if os.path.exists(f"{path}/Management Intents") is True:
        for root, dirs, files in os.walk(f"{path}/Management Intents", topdown=True):
            for file in files:
                if file.endswith(".yaml") or file.endswith(".json"):
                    # if file is not in created_files, archive it
                    if file.replace(f".{output}", "") not in created_files:
                        archive(path, file, root)
