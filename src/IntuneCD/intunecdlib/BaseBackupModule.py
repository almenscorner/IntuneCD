# -*- coding: utf-8 -*-
import re

from .BaseGraphModule import BaseGraphModule
from .process_audit_data import ProcessAuditData
from .process_scope_tags import ProcessScopeTags


class BaseBackupModule(BaseGraphModule):
    """Base class for backup modules."""

    def __init__(
        self,
        path: str = None,
        filetype: str = None,
        token: str = None,
        audit: bool = False,
        append_id: bool = False,
        exclude: list = None,
        scope_tags: dict = None,
        ignore_oma_settings: bool = False,
        prefix: str = None,
        azure_token: str = None,
        platforms: list = [],
    ):
        """Initializes the BaseBackupModule class

        Args:
            path (str, optional): The path to save the backup files. Defaults to None.
            filetype (str, optional): The file type to save the data as. Defaults to None.
            token (str, optional): The token to use for the request. Defaults to None.
            audit (bool, optional): Whether to audit the data. Defaults to False.
            append_id (bool, optional): Whether to append the id to the filename. Defaults to False.
            exclude (list, optional): The keys to exclude from the data. Defaults to None.
            scope_tags (dict, optional): The scope tags to use for the data. Defaults to None.
            ignore_oma_settings (bool, optional): Whether to ignore oma settings. Defaults to False.
            prefix (str, optional): The prefix to use for the filename. Defaults to None.
            azure_token (str, optional): The azure token to use for the request. Defaults to None.
        """
        super().__init__()
        self.endpoint = "https://graph.microsoft.com"
        self.platform_keywords = {
            "mobile": ["ios", "android", "aosp"],
            "mac": ["macos"],
            "windows": ["windows"],
        }
        # Variables set from the backup run
        self.token = token
        self.azure_token = azure_token
        self.audit = audit
        self.path = path
        self.filetype = filetype
        self.append_id = append_id
        self.exclude = exclude
        self.scope_tags = scope_tags
        self.ignore_oma_settings = ignore_oma_settings
        self.prefix = prefix
        self.platforms = platforms
        # Default variables, can be overridden in child classes
        self.assignment_endpoint = None
        self.assignment_extra_url = None
        self.assignment_responses = None
        self.config_audit_data = False
        self.report = False
        self.clean_data = True
        self.audit_filter = None
        self.audit_data = None
        self.results = {"config_count": 0, "outputs": []}
        # Initialize the process audit data and process scope tags classes
        self.process_audit_data = ProcessAuditData()
        self.process_scope_tag = ProcessScopeTags()

    def _prepare_file_name(self, filename: str) -> str:
        """Removes illegal characters from the filename

        Args:
            filename (str): The filename to prepare

        Returns:
            str: The prepared filename
        """

        remove_characters = "/\\:*?<>|"
        if not isinstance(filename, str):
            filename = str(filename)
        for character in remove_characters:
            filename = filename.replace(character, "_")

        return filename

    def _handle_audit(self, compare_data: dict):
        """Handle the audit data

        Args:
            compare_data (dict): The data to compare
        """
        try:
            self.process_audit_data.process_audit_data(
                self.audit_data,
                compare_data,
                self.path,
                f"{self.path}{self.filename}.{self.filetype}",
            )
        except Exception as e:
            self.log(
                tag="error",
                msg=f"Error handling audit data for {self.filename}: {e}",
            )

    def _get_audit_data(self, audit_compare_info: dict, data: dict):
        """Perpare and process the audit data

        Args:
            audit_compare_info (dict): Information about the audit type and value key
            data (dict): The data to compare
        """
        try:
            if audit_compare_info["value_key"] not in data:
                compare_data = {
                    "type": audit_compare_info["type"],
                    "value": audit_compare_info["value_key"],
                }
            else:
                compare_data = {
                    "type": audit_compare_info["type"],
                    "value": data[audit_compare_info["value_key"]],
                }
            self._handle_audit(compare_data)
        except Exception as e:
            self.log(
                tag="error",
                msg=f"Error processing audit data for {self.filename}: {e}",
            )

    def _append_config_type(self, data: dict) -> str:
        """Append the config type to the filename

        Args:
            data (dict): The data to get the config type from

        Returns:
            str: The config type
        """
        try:
            if "@odata.type" in data:
                config_type = str(f"_{data['@odata.type'].split('.')[2]}")
            elif "technologies" in data:
                config_type = str(f"_{data['technologies']}")
            else:
                config_type = ""

            return config_type
        except Exception as e:
            self.log(
                tag="error",
                msg=f"Error appending config type for {self.filename}: {e}",
            )
            return None

    def _matches_role(self, data, platform_keywords, platforms):
        """Check if a policy matches a specific role (e.g., 'mobile', 'mac', 'windows')."""

        # Ensure @odata.type and platform exist and are strings
        odata_type = str(data.get("@odata.type", "")).lower()
        config_platform = str(data.get("platform", "")).lower()
        config_platforms = str(data.get("platforms", "")).lower()
        settings_delta = str(data.get("settingsDelta", ""))
        definition_id = ""
        if len(settings_delta) > 0:
            definition_id = str(
                data["settingsDelta"][0].get("definitionId", "")
            ).lower()

        # Get keywords for the requested role
        keywords = []
        for r in platforms:
            keywords.extend(platform_keywords.get(r, []))

        if any(
            keyword in odata_type
            or keyword in config_platform
            or keyword in definition_id
            or keyword in config_platforms
            for keyword in keywords
        ):
            return True

        return False

    def _process_single_item(
        self,
        data: dict,
        filetype: str,
        path: str,
        name_key: str,
        log_message: str,
        audit_compare_info: dict,
        assignment_responses: dict,
    ) -> dict:
        """Process a single item

        Args:
            data (dict): The data to process
            filetype (str): The file type to save the data as
            path (str): The path to save the backup files
            name_key (str): The key to use for the name
            log_message (str): The message to log
            audit_compare_info (dict): Information about the audit type and value key
            assignment_responses (dict): The responses to use for assignments

        Returns:
            dict: The results of the backup
        """
        self.filename = ""

        if self.platforms:
            result = self._matches_role(data, self.platform_keywords, self.platforms)

            if result is False:
                return {"config_count": 0, "outputs": []}

        if self.prefix:
            if name_key == "":
                return self.results
            match = self.check_prefix_match(data[f"{name_key}"], self.prefix)
            if not match:
                return self.results

        if log_message:
            self.log(msg=log_message + data[f"{name_key}"])

        try:
            if hasattr(self, "preset_filename"):
                self.filename = self._prepare_file_name(self.preset_filename)
            else:
                self.filename = f"{data[f'{name_key}']}{self._append_config_type(data)}"
                self.filename = self._prepare_file_name(self.filename)
        except Exception as e:
            self.log(
                tag="error",
                msg=f"Error preparing filename for {data[f'{name_key}']}, {e}",
            )

        try:
            if self.append_id:
                self.filename += f"__{data['id']}"
        except Exception as e:
            self.log(
                tag="error",
                msg=f"Error appending id to filename for {self.filename}, {e}",
            )

        if assignment_responses:
            assignments = self.get_object_assignment(data["id"], assignment_responses)
            if assignments:
                data["assignments"] = assignments

        if hasattr(self, "scope_tags") and self.scope_tags:
            data = self.process_scope_tag.get_scope_tags_name(data, self.scope_tags)

        audit_data = data.copy()
        if self.clean_data is True:
            data = self.remove_keys(data)

        self.save_to_file(data, filetype, path, self.filename)

        if self.audit_data:
            self._get_audit_data(audit_compare_info, audit_data)

        return {"config_count": 1, "outputs": [self.filename]}

    def _process_multiple_items(
        self,
        data: dict,
        filetype: str,
        path: str,
        name_key: str,
        log_message: str,
        audit_compare_info: dict,
        assignment_responses: dict,
    ) -> dict:
        """Process multiple items

        Args:
            data (dict): The data to process
            filetype (str): The file type to save the data as
            path (str): The path to save the backup files
            name_key (str): The key to use for the name
            log_message (str): The message to log
            audit_compare_info (dict): Information about the audit type and value key
            assignment_responses (dict): The responses to use for assignments

        Returns:
            dict: The results of the backup
        """
        results = {"config_count": 0, "outputs": []}
        for item in data:
            item_results = self._process_single_item(
                item,
                filetype,
                path,
                name_key,
                log_message,
                audit_compare_info,
                assignment_responses,
            )
            results["config_count"] += item_results["config_count"]
            results["outputs"].extend(item_results["outputs"])

        return results

    def process_data(
        self,
        data: dict,
        filetype: str,
        path: str,
        name_key: str,
        log_message: str = None,
        audit_compare_info: dict = None,
    ) -> dict:
        """Process the backup data

        Args:
            data (dict): The data to process
            filetype (str): The file type to save the data as
            path (str): The path to save the backup files
            name_key (str): The key to use for the name
            log_message (str, optional): The message to log. Defaults to None.
            audit_compare_info (dict, optional): Information about the audit type and value key. Defaults to None.

        Returns:
            dict: The results of the backup
        """
        if "assignments" not in self.exclude:
            if (
                getattr(self, "has_assignments", True) is not False
                and self.assignment_responses is None
            ):
                self.assignment_responses = self.batch_assignment(
                    data, self.assignment_endpoint, self.assignment_extra_url
                )

        if self.audit and self.config_audit_data is False:
            self.audit_data = self.make_audit_request(self.audit_filter)

        if isinstance(data, list):
            return self._process_multiple_items(
                data,
                filetype,
                path,
                name_key,
                log_message,
                audit_compare_info,
                self.assignment_responses,
            )

        if isinstance(data, dict):
            return self._process_single_item(
                data,
                filetype,
                path,
                name_key,
                log_message,
                audit_compare_info,
                self.assignment_responses,
            )

    def check_prefix_match(self, config_name: str, prefix: str) -> bool:
        """Check if the prefix matches the config name

        Args:
            config_name (str): The name of the config
            prefix (str): The prefix to check for

        Returns:
            bool: Whether the prefix matches the config name
        """
        prefix_in_name = re.search(
            r"(^|\s)" + prefix.lower() + r".*($|\s)", config_name.lower()
        )
        if not prefix_in_name:
            return False
        return True

    def update_results(self, results: dict):
        """Update the results

        Args:
            results (dict): The results to update
        """
        self.results["config_count"] += results["config_count"]
        self.results["outputs"].extend(results["outputs"])
