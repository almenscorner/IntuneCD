# -*- coding: utf-8 -*-
import json
import os
import plistlib
import re
from datetime import datetime

from deepdiff import DeepDiff

from .BaseGraphModule import BaseGraphModule
from .process_scope_tags import ProcessScopeTags


class BaseUpdateModule(BaseGraphModule):
    """This class is the base class for all update modules. It contains methods for updating downstream data."""

    def __init__(
        self,
        token: str = None,
        path: str = None,
        filetype: str = None,
        exclude: list = None,
        scope_tags: dict = None,
        create_groups: bool = False,
        report: bool = False,
        remove: bool = False,
        azure_token: str = None,
        handle_assignment: bool = False,
    ):
        """Initializes the BaseBackupModule class

        Args:
            token (str, optional): The token to use, defaults to None.
            path (str, optional): The path to use, defaults to None.
            filetype (str, optional): The filetype to use, defaults to None.
            exclude (list, optional): The list of paths to exclude from the diff, defaults to None.
            scope_tags (dict, optional): The scope tags to use, defaults to None.
            create_groups (bool, optional): If groups should be created, defaults to False.
            report (bool, optional): If a report should be created, defaults to False.
            remove (bool, optional): If the data should be removed, defaults to False.
            azure_token (str, optional): The Azure token to use, defaults to None.
        """
        self.endpoint = "https://graph.microsoft.com"
        # Variables set from the update run
        self.token = token
        self.azure_token = azure_token
        self.path = path
        self.filetype = filetype
        self.exclude = exclude
        self.scope_tags = scope_tags
        self.create_groups = create_groups
        self.report = report
        self.remove = remove
        self.handle_assignment = handle_assignment
        # Default variables, can be overridden in child classes
        self.assignment_endpoint = None
        self.assignment_extra_url = None
        self.assignment_responses = None
        self.create_request = None
        self.exclude_paths = None
        self.message = None
        self.notify = True
        self.get_match = True
        self.url_append_id = True
        self.handle_iterable_assignment = False
        self.create_config = True
        self.azure_update = False
        self.config_type = None
        self.match_info = None
        self.config_endpoint = None
        self.downstream_assignments = None
        self.create_request = None
        self.assignment_status_code = 200
        self.post_status_code = 201
        self.remove_status_code = 200
        self.assignment_key = "assignments"
        self.params = {}
        self.diff_summary = []
        self.diffs = []
        self.diff_count = 0

    def get_diffs(
        self, repo_data: dict, intune_data: dict, exclude_paths: list = None
    ) -> list:
        """Gets the differences between the data and the memory data

        Args:
            repo_data (dict): The data to compare
            intune_data (dict): The memory data to compare

        Returns:
            list: The differences between the data and the memory data
        """
        diffs = []
        diff = self._get_deep_diff(repo_data, intune_data, exclude_paths)
        if diff:
            diffs = self._process_diffs(diff)
        else:
            if self.notify is True:
                self.log(msg=f"No changes found for {self.config_type}: {self.name}")
        return diffs

    def _get_deep_diff(
        self, repo_data: dict, intune_data: dict, exclude_paths: list
    ) -> dict[str, any]:
        """Gets the deep diff between the data and the intune data

        Args:
            repo_data (dict): The data stored in the repository
            intune_data (dict): The data stored in Intune
            exclude_paths (list): Paths to exclude from the diff

        Returns:
            dict[str, any]: The deep diff between the data and the intune data
        """
        if isinstance(repo_data, (list, dict)):
            if exclude_paths:
                return DeepDiff(
                    intune_data,
                    repo_data,
                    exclude_paths=exclude_paths,
                    ignore_order=True,
                )

            return DeepDiff(intune_data, repo_data, ignore_order=True)

        if isinstance(repo_data, str):
            return DeepDiff(intune_data, repo_data)

    def _process_diffs(self, diff: dict) -> list:
        """Processes the differences between the data and the intune data

        Args:
            diff (dict): The differences between the data and the intune data

        Returns:
            list: The differences between the data and the intune data
        """
        diffs = []
        if "values_changed" in diff:
            diffs.extend(self._process_value_changes(diff))
        if "iterable_item_added" in diff or "iterable_item_removed" in diff:
            diffs.extend(self._process_iterable_changes(diff))
        if "type_changes" in diff:
            diffs.extend(self._process_type_changes(diff))

        return diffs

    def _process_value_changes(self, diff: dict) -> list:
        """Processes the value changes

        Args:
            diff (dict): The differences between the data and the intune data

        Returns:
            list: The differences between the data and the intune data
        """
        diffs = []
        for key, value in diff["values_changed"].items():
            vals = self._get_diff_values(key, value)
            diffs.append(vals)
        self._log_diffs(diffs, "values changed")

        return diffs

    def _process_iterable_changes(self, diff: dict) -> list:
        """Processes the iterable changes

        Args:
            diff (dict): The differences between the data and the intune data

        Returns:
            list: The differences between the data and the intune data
        """
        diffs = []

        def get_setting(key: str) -> str:
            setting = re.search("\\[(.*)\\]", key)
            return setting[1].split("[")[0] if setting else key

        def get_value(value: dict) -> str:
            val = list(value.values())
            return val or "Unknown"

        def set_vals(setting: str, new_val: str, old_val: str) -> dict:
            return {
                "setting": setting.replace("'", "").replace('"', "").replace("]", ""),
                "new_val": new_val,
                "old_val": old_val,
            }

        if "iterable_item_added" in diff:
            for key, _ in diff["iterable_item_added"].items():
                setting = get_setting(key)
                new_val = get_value(diff["iterable_item_added"])
                vals = set_vals(setting, new_val, "")
                diffs.append(vals)
        if "iterable_item_removed" in diff:
            for key, _ in diff["iterable_item_removed"].items():
                setting = get_setting(key)
                old_val = get_value(diff["iterable_item_removed"])
                vals = set_vals(setting, "", old_val)
                diffs.append(vals)

        self._log_diffs(diffs, "list changes")

        return diffs

    def _process_type_changes(self, diff: dict) -> list:
        """Processes the type changes

        Args:
            diff (dict): The differences between the data and the intune data

        Returns:
            list: The differences between the data and the intune data
        """
        diffs = []
        for key, value in diff["type_changes"].items():
            vals = self._get_diff_values(key, value)
            diffs.append(vals)
            self._log_diffs(diffs, "type changed")
        return diffs

    def _get_diff_values(self, key: str, value: dict) -> dict:
        """Gets the values for the differences

        Args:
            key (str): The key to use
            value (dict): The value to use

        Returns:
            dict: The values for the differences
        """
        max_length = 100
        vals = {}
        setting = re.search("\\[(.*)\\]", key)
        if setting:
            setting = setting.group(1).split("[")[-1]
        vals["setting"] = str(setting).replace("'", "").replace('"', "")
        vals["new_val"] = (
            str(value["new_value"]).replace("'", "").replace('"', "")[:max_length]
        )
        vals["old_val"] = (
            str(value["old_value"]).replace("'", "").replace('"', "")[:max_length]
        )
        vals["change_date"] = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        return vals

    def _log_diffs(self, diffs: list, change_type: str) -> None:
        """Logs the differences

        Args:
            diffs (list): The differences to log
            change_type (str): The type of change
        """
        if diffs and not self.message:
            if self.name:
                self.log(
                    msg=f"Updating {self.config_type}: {self.name}, {change_type}:"
                )
            else:
                self.log(msg=f"Updating {self.config_type}, {change_type}:")
            for item in diffs:
                if change_type in {"values changed", "type changed"}:
                    self.log(
                        msg=f"Setting: {item['setting']}, New Value: {item['new_val']}, Old Value: {item['old_val']}"
                    )
                if change_type == "list changes":
                    self.log(
                        msg=f"Setting: {item['setting']}, Added Value: {item['new_val']}, Removed Value: {item['old_val']}"
                    )
        elif self.message:
            diffs = [self.message]
            self.log(msg=self.message)
        elif self.notify:
            self.log(msg=f"No changes found for {self.config_type}: {self.name}")
        self.count = len(diffs)

    def get_downstream_data(self, endpoint: str) -> dict:
        """Gets the memory data

        Args:
            endpoint (str): The endpoint to use
            token (str): The token to use
            query_params (dict): The query parameters to use

        Returns:
            dict: The memory data
        """

        try:
            intune_data = self.make_graph_request(
                endpoint=self.endpoint + endpoint, params=self.params
            )
        except Exception as e:
            self.log(tag="error", msg=f"Failed to get Intune data: {e}")
            return None

        return intune_data

    def update_downstream_data(
        self, config_endpoint: str, method: str, status_code: int, data: dict
    ) -> None:
        """Updates the Intune data

        Args:
            config_endpoint (str): The endpoint to use
            method (str): The method to use
            status_code (int): The status code to expect
            data (dict): The data to use
        """
        data.pop("assignments", None)
        request_data = json.dumps(data)
        if self.azure_update:
            self.make_azure_request(
                endpoint=config_endpoint,
                params=self.params,
                data=request_data,
                method=method,
                status_code=status_code,
            )
        else:
            self.make_graph_request(
                endpoint=config_endpoint,
                params=self.params,
                data=request_data,
                method=method,
                status_code=status_code,
            )

    def remove_downstream_data(
        self, config_endpoint: str, downstream_data: dict
    ) -> None:
        """Removes the Downstream data

        Args:
            config_endpoint (str): The endpoint to use
            downstream_data (dict): The data to remove
            status_code (int): The status code to expect
        """
        if self.remove:
            for item in downstream_data:
                if "displayName" in item:
                    config_name = item["displayName"]
                elif "name" in item:
                    config_name = item["name"]
                else:
                    self.log(
                        tag="warning",
                        msg=f"Could not find name for {self.config_type}, skipping removal",
                    )

                self.log(msg=f"Removing {self.config_type}: {config_name}")
                try:
                    self.make_graph_request(
                        endpoint=self.endpoint + config_endpoint + item["id"],
                        params=self.params,
                        method="DELETE",
                        status_code=self.remove_status_code,
                    )
                except Exception as e:
                    self.log(
                        msg=f"Failed to remove {self.config_type} {config_name}: {e}"
                    )

    def create_downstream_data(
        self, config_endpoint: str, data: dict, repo_assignments: dict
    ) -> None:
        """Creates the Intune data

        Args:
            config_endpoint (str): The endpoint to use
            data (dict): The data to use
            repo_assignments (dict): The repository assignments to use
        """
        self.log(msg=f"{self.config_type} {self.name} not found, creating: {self.name}")
        data.pop("assignments", None)
        request_data = json.dumps(data)
        self.create_request = self.make_graph_request(
            endpoint=self.endpoint + config_endpoint,
            params=self.params,
            data=request_data,
            method="POST",
            status_code=self.post_status_code,
        )
        self.log(msg=f"Created with id: {self.create_request['id']}")

        if self.handle_assignment:
            if self.config_type == "Windows Enrollment Profile":
                self.handle_iterable_assignments(
                    repo_assignments,
                    [],
                    self.assignment_key,
                    self.create_request["id"],
                )
            else:
                self.handle_assignments(
                    repo_assignments, [], self.assignment_key, self.create_request["id"]
                )

    def get_match_data(self, intune_data: dict, match_info: dict) -> tuple:
        """Gets the matching data

        Args:
            intune_data (dict): The intune data
            match_info (dict): The match info from the repository

        Returns:
            tuple: The matching data
        """
        config_match_count = len(match_info)
        intune_item = None
        intune_id = None
        for item in intune_data:
            match_count = 0  # Reset match_count for each item
            for key, value in match_info.items():
                if item.get(key) == value:
                    match_count += 1
            if match_count == config_match_count:
                intune_data.remove(item)
                intune_item = dict(item)
                intune_id = item["id"]
                break  # Exit the loop once a match is found
        return intune_item, intune_id

    def handle_assignments(
        self,
        repo_assignments: dict,
        intune_assignments: dict,
        assignment_key: str,
        intune_id: str,
    ) -> None:
        """Handles the assignments

        Args:
            repo_assignments (dict): The repository assignments to use
            intune_assignments (dict): The intune assignments to compare
            intune_id (str): The intune configuration id to use
        """
        intune_assignment_data = self.get_object_assignment(
            intune_id, intune_assignments
        )
        assignment_update = self.update_assignment(
            repo_assignments, intune_assignment_data, self.create_groups
        )
        if assignment_update is not None:
            request_data = {assignment_key: assignment_update}
            self.make_graph_request(
                endpoint=self.endpoint
                + "/beta"
                + self.assignment_endpoint
                + intune_id
                + self.assignment_extra_url,
                data=json.dumps(request_data),
                method="POST",
                status_code=self.assignment_status_code,
            )

    def handle_iterable_assignments(
        self,
        repo_assignments: dict,
        intune_assignments: dict,
        assignment_key: str,
        intune_id: str,
    ) -> None:
        """Handles the iterable assignments

        Args:
            repo_assignments (dict): The repository assignments to use
            intune_assignments (dict): The intune assignments to compare
            intune_id (str): The intune configuration id to use
        """
        intune_assignment_data = self.get_object_assignment(
            intune_id, intune_assignments
        )
        assignment_update = self.update_assignment(
            repo_assignments, intune_assignment_data, self.create_groups
        )
        if assignment_update is not None:
            for assignment in assignment_update:
                request_data = {assignment_key: assignment["target"]}
                self.make_graph_request(
                    endpoint=self.endpoint
                    + "/beta"
                    + self.assignment_endpoint
                    + intune_id
                    + self.assignment_extra_url,
                    data=json.dumps(request_data),
                    method="POST",
                    status_code=self.assignment_status_code,
                )

    def path_exists(self, path: str = None) -> bool:
        """Checks if a path exists

        Args:
            path (str, optional): Path to check, defaults to None.

        Returns:
            bool: If the path exists
        """
        if path is None:
            path = self.path
        return os.path.exists(path)

    def load_repo_data(self, filename: str) -> dict:
        """Loads the repository data

        Args:
            filename (str): The filename to use
            file (str): The file to use

        Returns:
            dict: The repository data
        """

        repo_file = self.check_file(self.path, filename)
        if repo_file is False:
            return None

        with open(repo_file, encoding="utf-8") as f:
            repo_data = self.load_file(filename, f)

        if self.scope_tags:
            repo_data = ProcessScopeTags().get_scope_tags_id(repo_data, self.scope_tags)

        return repo_data

    def load_plist(self, path: str) -> dict[str, any]:
        """Loads a plist file"""
        try:
            data = {}
            with open(path, "rb") as f:
                data = plistlib.load(f)
            return data
        except Exception as e:
            self.log(tag="error", msg=f"Failed to load payload: {e}")
            return None

    def load_script_file(self, path: str) -> str:
        """Loads a script file"""
        try:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    return f.read()
            else:
                self.log(msg=f"File not found: {path}")
                return None
        except Exception as e:
            self.log(tag="error", msg=f"Failed to load script file: {e}")
            return None

    def write_temp_file(self, data: str) -> None:
        """Writes a temp file to the path"""
        try:
            with open(self.path + "temp.mobileconfig", "w", encoding="utf-8") as f:
                f.write(data)
        except Exception as e:
            self.log(tag="error", msg=f"Failed to write temp file: {e}")

    def remove_temp_file(self, path: str) -> None:
        """Removes a temp file from the path"""
        try:
            os.remove(path)
        except Exception as e:
            self.log(tag="error", msg=f"Failed to remove temp file: {e}")

    def print_config_separator(self) -> None:
        """Prints a separator for the config"""
        print("-" * 120)

    def create_diff_data(self, name: str, config_type: str) -> dict:
        """Creates the diff data dictionary"""
        diff_count = 0
        diffs = []
        return {
            "type": config_type,
            "name": name,
            "diffs": diffs,
            "count": diff_count,
        }

    def update_diff_data(self, diffs: list) -> None:
        """Updates the diff data"""
        self.diff_count += len(diffs)
        self.diffs.extend(diffs)

    def reset_diffs_and_count(self) -> None:
        """Resets the diffs and count for the diff data"""
        self.diffs = []
        self.diff_count = 0

    def set_diff_data(self, diff_data: dict) -> None:
        """Sets the diff data for the config"""
        diff_data["diffs"] = self.diffs
        diff_data["count"] = self.diff_count

    def process_update(
        self,
        downstream_data: dict,
        repo_data: dict,
        method: str,
        status_code: int,
        config_endpoint: str,
        update_data: dict = None,
        create_data: dict = None,
        repo_assignments: dict = None,
    ) -> None:
        """Processes the update for the downstream data.

        Args:
            downstream_data (dict): The intune data to use
            repo_data (dict): The repository data to use
            method (str): The method to use
            status_code (int): The status code to expect
            config_endpoint (str): The endpoint to use
            update_data (dict, optional): The data to use for the update, defaults to None.
            create_data (dict, optional): The data to use for the create, defaults to None.
            repo_assignments (dict, optional): The repository assignments to use, defaults to None.
        """
        if repo_assignments is None:
            repo_assignments = repo_data.get("assignments", {})
        if self.get_match is False:
            self.downstream_object = downstream_data
            self.downstream_id = downstream_data.get("id", "")
        else:
            self.downstream_object, self.downstream_id = self.get_match_data(
                downstream_data, self.match_info
            )

        if self.downstream_object:
            # if self.notify:
            #
            # Temporarily remove scheduledActionsForRule from the data if it exists
            repo_scheduled_actions = None
            if repo_data.get("scheduledActionsForRule"):
                repo_scheduled_actions = repo_data["scheduledActionsForRule"]
                repo_data.pop("scheduledActionsForRule")

            self.downstream_object = self.remove_keys(self.downstream_object)

            def _add_schedule_action():
                if repo_scheduled_actions:
                    repo_data["scheduledActionsForRule"] = repo_scheduled_actions

            diffs = self.get_diffs(
                repo_data, self.downstream_object, self.exclude_paths
            )
            if diffs:
                if update_data:
                    data = update_data
                else:
                    data = repo_data
                self.update_diff_data(diffs)

                if self.url_append_id:
                    config_endpoint = config_endpoint + self.downstream_id
                if self.azure_update:
                    pass
                else:
                    config_endpoint = self.endpoint + config_endpoint

                self.update_downstream_data(
                    config_endpoint=config_endpoint,
                    method=method,
                    status_code=status_code,
                    data=data,
                )

                # Add scheduledActionsForRule back to the data if it was removed
                _add_schedule_action()

            if self.handle_assignment:
                if self.config_type == "Windows Enrollment Profile":
                    self.handle_iterable_assignments(
                        repo_assignments,
                        self.downstream_assignments,
                        self.assignment_key,
                        self.downstream_id,
                    )
                else:
                    self.handle_assignments(
                        repo_assignments,
                        self.downstream_assignments,
                        self.assignment_key,
                        self.downstream_id,
                    )

                # Add scheduledActionsForRule back to the data if it was removed
                _add_schedule_action()

        else:
            data = create_data if create_data else repo_data
            if self.create_config:
                self.diff_count += 1
                self.create_downstream_data(
                    config_endpoint=config_endpoint,
                    data=data,
                    repo_assignments=repo_assignments,
                )
