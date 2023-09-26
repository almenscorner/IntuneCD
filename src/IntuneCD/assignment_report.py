#!/usr/bin/env python3

"""
This module creates a report of all groups found and their assginment.
"""

import os
import platform

from .save_output import save_output
from .check_file import check_file
from .load_file import load_file


def get_group_report(path, output):
    """
    This function is used to get a report of all groups and what they are assigned to.

    Args:
        path (str): Path to save the report to
        output (str): Output format for the report
    """

    report_path = f"{path}/Assignment Report/"

    def process_file(path, name, payload_type, groups):
        file_check = check_file(path, name)
        if file_check:
            with open(os.path.join(path, name), "r") as f:
                data = load_file(name, f)
                if type(data) is dict and data.get("assignments"):
                    for assignment in data["assignments"]:
                        if assignment["target"].get("groupName"):
                            if data.get("displayName"):
                                name = data["displayName"]
                            elif data.get("name"):
                                name = data["name"]
                            data = {
                                "groupName": assignment["target"]["groupName"],
                                "groupType": assignment["target"].get("groupType"),
                                "membershipRule": assignment["target"].get("membershipRule", None),
                                "assignedTo": {},
                            }

                            payload_added = False  # flag to track whether payload_type has been added

                            if not groups:
                                groups.append(data)
                                data["assignedTo"][payload_type] = [name]
                                payload_added = True
                            else:
                                for item in groups:
                                    if item["groupName"] == data["groupName"]:
                                        if not payload_added and item["assignedTo"].get(payload_type):
                                            item["assignedTo"][payload_type].append(name)
                                            payload_added = True
                                        elif not payload_added and not item["assignedTo"].get(payload_type):
                                            item["assignedTo"][payload_type] = [name]
                                            payload_added = True

                                if not payload_added:
                                    data["assignedTo"][payload_type] = [name]
                                    groups.append(data)

    def collect_groups(path):
        exclude = set(
            [
                "__archive__",
            ]
        )
        groups = []
        slash = "/"
        run_os = platform.uname().system
        if run_os == "Windows":
            slash = "\\"
        abs_path = os.path.abspath(path)
        for root, dirs, files in os.walk(path, topdown=True):
            dirs[:] = [d for d in dirs if d not in exclude]
            abs_root = os.path.abspath(root)
            for file in files:
                os.path.abspath(root)
                payload_type = abs_root.replace(abs_path, "").split(slash)
                if len(payload_type) > 1:
                    payload_type = payload_type[1]
                process_file(
                    str(root),
                    file,
                    payload_type,
                    groups,
                )
        return groups

    groups = collect_groups(path)

    if groups:
        save_output(output, report_path, "report", groups)
