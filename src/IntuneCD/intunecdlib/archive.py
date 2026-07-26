#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module moves files to archive during backup if they have been removed from Intune.
"""

import os
import shutil

from datetime import datetime, timedelta, timezone
from .BaseBackupModule import BaseBackupModule
from .process_audit_data import ProcessAuditData


class Archive(BaseBackupModule):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.exclude = {
            "Management Intents",
            "archive",
            "__archive__",
            "Assignment Report",
            "Autopilot Devices",
            "Activation Lock Bypass Codes",
        }
        self.date_tag = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.process_audit_data = ProcessAuditData()
        self.audit_endpoint = (
            "https://graph.microsoft.com/beta/deviceManagement/auditEvents"
        )
        if self.append_id and self.audit:
            self.audit_data = self._get_audit_delete_events()

    def archive_file(self, file, root):
        archive_path = os.path.join(self.path, "__archive__", self.date_tag)
        if not os.path.exists(archive_path):
            os.makedirs(archive_path)

        src = os.path.join(root, file)
        dst = os.path.join(archive_path, file)
        shutil.move(src, dst)

        if self.audit_data:
            self._handle_audit_commit(file, dst, archive_path, src)

    def _get_audit_delete_events(self) -> list:
        """Gets all delete events from the audit log from the last 24h

        Returns:
            list: A list of all delete events
        """
        if not os.getenv("AUDIT_DAYS_BACK"):
            days_back = 1
        else:
            days_back = int(os.getenv("AUDIT_DAYS_BACK"))
        start_date = (
            datetime.now(timezone.utc) - timedelta(days=days_back)
        ).isoformat()
        end_date = datetime.now(timezone.utc).isoformat()

        q_params = {
            "$filter": (
                f"activityOperationType eq 'Delete' and "
                f"activityDateTime gt {start_date} and "
                f"activityDateTime le {end_date}"
            ),
            "$select": "actor,activityDateTime,activityType,activityOperationType,activityResult,resources",
            "$orderby": "activityDateTime desc",
        }

        audit_data = self.graph.make_graph_request(
            self.audit_endpoint, params=q_params, method="GET"
        )

        return audit_data

    def _handle_audit_commit(self, filename, filepath, archive_path, source_file):
        """Handles the audit commit for the file

        Args:
            filename: The name of the file
            filepath: The path to the file
            archive_path: The path to the archive
        """
        resource_id = filename.split("__")[-1].replace(".json", "").replace(".yaml", "")

        if self.audit_data:
            audit_data_record = next(
                (
                    item
                    for item in self.audit_data.get("value", [])
                    if resource_id
                    in [res.get("resourceId") for res in item.get("resources", [])]
                ),
                None,
            )

        if audit_data_record:
            if audit_data_record["actor"]["auditActorType"] == "ItPro":
                actor = audit_data_record["actor"].get("userPrincipalName")
            else:
                actor = audit_data_record["actor"].get("applicationDisplayName")

            audit_data_record = {
                "resourceId": audit_data_record["resources"][0]["resourceId"],
                "auditResourceType": audit_data_record["resources"][0][
                    "auditResourceType"
                ],
                "actor": actor,
                "activityDateTime": audit_data_record["activityDateTime"],
                "activityType": audit_data_record["activityType"],
                "activityOperationType": audit_data_record["activityOperationType"],
                "activityResult": audit_data_record["activityResult"],
            }

            self.filename = os.path.splitext(os.path.basename(filepath))[0]
            # process audit and check for deleted files
            self.process_audit_data.process_audit_data(
                audit_data_record,
                None,
                archive_path,
                filepath,
                get_record=False,
                record=audit_data_record,
                source_file=source_file,
            )
            # process audit and check for archived files
            self.process_audit_data.process_audit_data(
                audit_data_record,
                None,
                archive_path,
                filepath,
                get_record=False,
                record=audit_data_record,
            )

    def move_to_archive(self, created_files):
        if not os.path.exists(os.path.join(self.path, "__archive__")):
            os.makedirs(os.path.join(self.path, "__archive__"))

        for root, dirs, files in os.walk(self.path, topdown=True):
            dirs[:] = [d for d in dirs if d not in self.exclude]
            for file in files:
                if file.endswith((".yaml", ".json")):
                    if root == self.path and file.endswith(".json"):
                        continue
                    if file.replace(f".{self.filetype}", "") not in created_files:
                        self.archive_file(file, root)

        mgmt_path = os.path.join(self.path, "Management Intents")
        if os.path.exists(mgmt_path):
            for root, dirs, files in os.walk(mgmt_path, topdown=True):
                for file in files:
                    if file.endswith((".yaml", ".json")):
                        if file.replace(f".{self.filetype}", "") not in created_files:
                            self.archive_file(file, root)
