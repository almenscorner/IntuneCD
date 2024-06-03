#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module creates a report of all groups found and their assginment.
"""

import os
import platform

from .BaseBackupModule import BaseBackupModule


class AssignmentReport(BaseBackupModule):
    """Base class for creating a report of all groups and their assignment."""

    def __init__(self, path, filetype):
        super().__init__()
        self.path = path
        self.filetype = filetype

    def _process_file(self, path, name, payload_type, groups):
        file_check = self.check_file(path, name)
        if not file_check:
            return

        with open(os.path.join(path, name), "r", encoding="utf-8") as f:
            data = self.load_file(name, f)
            if not isinstance(data, dict) or not data.get("assignments"):
                return

        for assignment in data["assignments"]:
            if not assignment["target"].get("groupName"):
                continue

            intent_string = assignment.get("intent", "")
            config_type = ""
            if data.get("@odata.type"):
                config_type = f'{data["@odata.type"].split(".")[2]}'
            payload_name = data.get("displayName", data.get("name", ""))
            payload_data = {
                "name": payload_name,
                "type": config_type,
                "intent": intent_string,
            }

            group_data = {
                "groupName": assignment["target"]["groupName"],
                "groupType": assignment["target"].get("groupType"),
                "membershipRule": assignment["target"].get("membershipRule", None),
                "assignedTo": {},
            }

            payload_added = False  # flag to track whether payload_type has been added

            if not groups:
                groups.append(group_data)
                group_data["assignedTo"][payload_type] = [payload_data]
                payload_added = True
            else:
                for item in groups:
                    if item["groupName"] == group_data["groupName"]:
                        if not payload_added:
                            if item["assignedTo"].get(payload_type):
                                item["assignedTo"][payload_type].append(payload_data)
                            else:
                                item["assignedTo"][payload_type] = [payload_data]
                            payload_added = True
                            break

                if not payload_added:
                    group_data["assignedTo"][payload_type] = [payload_data]
                    groups.append(group_data)
                    # break

    def _collect_groups(self, path):
        exclude = set(["__archive__", "Entra"])
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
                self._process_file(
                    str(root),
                    file,
                    payload_type,
                    groups,
                )
        return groups

    def main(self):
        """
        This function is used to get a report of all groups and what they are assigned to.

        Args:
            path (str): Path to save the report to
            output (str): Output format for the report
        """

        groups = self._collect_groups(self.path)

        if groups:
            self.save_output(
                self.filetype, f"{self.path}/Assignment Report/", "report", groups
            )
