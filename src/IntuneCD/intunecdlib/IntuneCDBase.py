# -*- coding: utf-8 -*-
import base64
import json
import os
import sys
import time

import yaml


class IntuneCDBase:
    """IntuneCDBase is the base class for the IntuneCD library."""

    def remove_keys(self, data: dict):
        """
        This function removes keys from the data.
        :param data: The data to remove keys from.
        :return: The data with removed keys.
        """

        keys = {
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

        if "VPPusedLicenseCount" in self.exclude:
            keys.add("usedLicenseCount")
        if "GPlaySyncTime" in self.exclude:
            keys.add("lastAppSyncDateTime")
        if "CompliancePartnerHeartbeat" in self.exclude:
            keys.add("lastHeartbeatDateTime")

        for k in keys:
            data.pop(k, None)

        return data

    def save_to_file(self, data: dict, filetype: str, path: str, filename: str):
        """
        This function saves the configuration to a file in JSON or YAML format.
        """

        if not os.path.exists(path):
            os.makedirs(path)

        if filetype == "yaml":
            with open(path + filename + ".yaml", "w", encoding="utf-8") as yamlFile:
                yaml.dump(data, yamlFile, sort_keys=False, default_flow_style=False)
        elif filetype == "json":
            with open(path + filename + ".json", "w", encoding="utf-8") as jsonFile:
                json.dump(data, jsonFile, indent=5)

        else:
            raise ValueError("Invalid output format")

    def decode_base64(self, data: str):
        """
        This function decodes base64 data.

        :param data: The base64 data to decode.
        :return: The decoded data.
        """

        try:
            return base64.b64decode(data).decode("utf-8")
        except (UnicodeDecodeError, json.decoder.JSONDecodeError):
            return data

    def encode_base64(self, data: str):
        """
        This function encodes data to base64.

        :param data: The data to encode.
        :return: The encoded data.
        """

        return base64.b64encode(data.encode("utf-8")).decode("utf-8")

    def load_file(self, filename: str, file: str):
        """
        This function loads a JSON or YAML file to a dictionary.
        :param filename: The name of the file.
        :param file: The file to load.
        :return: The dictionary.
        """

        if filename.endswith(".yaml"):
            data = json.dumps(yaml.safe_load(file))
            repo_data = json.loads(data)

        elif filename.endswith(".json"):
            repo_data = json.load(file)

        else:
            raise ValueError(f"{filename} is not a valid file type.")

        return repo_data

    def check_file(self, configpath: str, filename: str):
        """
        Check if file is YAML or JSON, if true return the file, if not return False.

        :param configpath: The path to the config file
        :param filename: The name of the file
        :return: The file or False
        """

        file = os.path.join(configpath, filename)
        if file.endswith(".yaml"):
            return file
        if file.endswith(".json"):
            return file
        return False

    def save_output(self, filetype: str, configpath: str, filename: str, data: dict):
        """
        This function saves the configuration to a file in JSON or YAML format.

        :param output: The format the configuration will be saved as
        :param configpath: The path to save the configuration to
        :param fname: The filename of the configuration
        :param data: The configuration data
        """

        if not os.path.exists(configpath):
            os.makedirs(configpath)

        if filetype == "yaml":
            with open(
                configpath + filename + ".yaml", "w", encoding="utf-8"
            ) as yamlFile:
                yaml.dump(data, yamlFile, sort_keys=False, default_flow_style=False)
        elif filetype == "json":
            with open(
                configpath + filename + ".json", "w", encoding="utf-8"
            ) as jsonFile:
                json.dump(data, jsonFile, indent=5)

        else:
            raise ValueError("Invalid output format")

    def log(self, function: str = None, msg: str = None, tag: str = "info"):
        """Prints a message to the console if the VERBOSE environment variable is set to True.

        Args:
            function (str): The name of the function that is calling the log function.
            msg (str): The message to print to the console.
            tag (str): The tag to use for the log message. Defaults to "info".
        """
        exit_on_error = os.getenv("EXIT_ON_ERROR")
        verbose = os.getenv("VERBOSE")
        if verbose:
            msg = (
                f"{time.asctime()} [{tag.upper()}] [{function}] - {msg}"
                if verbose and function
                else f"[{time.asctime()}] - {msg}"
            )
            print(msg)

        if function is None and not verbose:
            msg = f"{time.asctime()} [{tag.upper()}] {msg}"
            print(msg)

        if tag == "error" and exit_on_error:
            sys.exit(1)

    def get_pop_keys(self, data: dict, keys: list[str], method: str = "get") -> None:
        """A method to get or pop keys from a dictionary

        Args:
            data (dict): The dictionary to get or pop the keys from
            keys (list[str]): The keys to get or pop
            method (str, optional): The action to take. Defaults to "get".

        Returns:
            dict: The dictionary with the keys removed if the method is "pop" or the value of the key if the method is "get"
        """
        for key in keys:
            parts = key.split(".")
            sub_dict = data
            for part in parts[:-1]:
                if sub_dict is None:
                    return None
                if part in sub_dict:
                    sub_dict = sub_dict[part]
            if sub_dict is None:
                return None
            if method == "pop":
                sub_dict.pop(parts[-1], None)
            else:
                return sub_dict.get(parts[-1])
