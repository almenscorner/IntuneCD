#!/usr/bin/env python3

"""
This module contains all functions for the documentation.
"""

import yaml
import json
import os
import glob
import re
import platform

from pytablewriter import MarkdownTableWriter


def md_file(outpath):
    """
    This function creates the markdown file.

    :param outpath: The path to save the Markdown document to
    """
    if not os.path.exists(f"{outpath}"):
        open(outpath, "w+").close()
    else:
        open(outpath, "w").close()


def write_table(data):
    """
    This function creates the markdown table.

    :param data: The data to be written to the table
    :return: The Markdown table writer
    """

    writer = MarkdownTableWriter(
        headers=["setting", "value"],
        value_matrix=data,
    )

    return writer


def assignment_table(data):
    """
    This function creates the Markdown assignments table.

    :param data: The data to be written to the table
    :return: The Markdown table writer
    """

    def write_assignment_table(data, headers):
        writer = MarkdownTableWriter(headers=headers, value_matrix=data)

        return writer

    table = ""
    if "assignments" in data:
        assignments = data["assignments"]
        assignment_list = []
        target = ""
        intent = ""
        for assignment in assignments:
            if assignment["target"]["@odata.type"] == "#microsoft.graph.allDevicesAssignmentTarget":
                target = "All Devices"
            if assignment["target"]["@odata.type"] == "#microsoft.graph.allLicensedUsersAssignmentTarget":
                target = "All Users"
            if "groupName" in assignment["target"]:
                target = assignment["target"]["groupName"]
            if "intent" in assignment:
                intent = assignment["intent"]
                headers = ["intent", "target", "filter type", "filter name"]
            else:
                headers = ["target", "filter type", "filter name"]
            if intent:
                assignment_list.append(
                    [
                        intent,
                        target,
                        assignment["target"]["deviceAndAppManagementAssignmentFilterType"],
                        assignment["target"]["deviceAndAppManagementAssignmentFilterId"],
                    ]
                )
            else:
                assignment_list.append(
                    [
                        target,
                        assignment["target"]["deviceAndAppManagementAssignmentFilterType"],
                        assignment["target"]["deviceAndAppManagementAssignmentFilterId"],
                    ]
                )

            table = write_assignment_table(assignment_list, headers)

    return table


def remove_characters(string):
    """
    This function removes characters from the string.
    :param string: The string to be cleaned
    :return: The cleaned string
    """

    remove_chars = '#@}{]["'
    for char in remove_chars:
        string = string.replace(char, "")

    return string


def clean_list(data):
    """
    This function returns a list with strings to be used in a table.
    :param data: The data to be cleaned
    :return: The list of strings
    """

    def list_to_string(l) -> str:
        string = ""
        for i in l:
            if isinstance(i, (str, int, bool)):
                string += f"<li> {i} </li>"
            elif isinstance(i, dict):
                string += dict_to_string(i)
            else:
                string += i

        return string

    def dict_to_string(d) -> str:
        string = ""
        for key, val in d.items():
            if isinstance(val, list):
                string += f"**{key}:** <ul>"
                string += list_to_string(val)
                string += "</ul>"
            elif isinstance(val, dict):
                string += f"**{key}:** <ul>"
                for k, v in val.items():
                    if isinstance(v, list):
                        string += list_to_string(v)
                    elif isinstance(v, dict):
                        for k2, v2 in v.items():
                            if isinstance(v2, list):
                                string += f"**{k2}:** <ul>"
                                string += list_to_string(v2)
                                string += "</ul>"
                            elif isinstance(v2, (str, bool, int)):
                                string += f"**{k2}:** {v2}</br>"
                            else:
                                string += f"**{k2}:** {v2}</br>"
                    else:
                        string += f"**{k}:** {v}</br>"
                string += "</ul>"
            else:
                string += f"**{key}:** {val}<br/>"

        string += "<br/>"

        return string

    def dict_to_table(d) -> str:
        string = ""
        for key, val in d.items():
            if isinstance(val, list) and val:
                string += f"**{key}:** <ul>"
                string += list_to_string(val)
                string += "</ul>"
            elif isinstance(val, dict) and val:
                for k, v in val.items():
                    if isinstance(v, list) and v:
                        string += f"{k} <ul>"
                        string += list_to_string(v)
                        string += "</ul>"
                    elif isinstance(v, dict):
                        string += f"**{k}** <ul>"
                        string += dict_to_string(v)
                        string += "</ul>"
                    else:
                        string += f"**{k}:** {v}</br>"
            else:
                string += f"**{key}:** {val}</br>"

        return string

    def list_string(l) -> str:
        string = ""
        for i in l:
            if isinstance(i, (str, int, bool)):
                string += f"{i}<br/>"
            if isinstance(i, list):
                string += list_to_string(i)
            if isinstance(i, dict):
                string += dict_to_string(i)

        return string

    def string(s) -> str:
        if len(s) > 200:
            string = f"<details><summary>Click to expand...</summary>{item}</details>"
        else:
            string = item

        return string

    values = []

    for item in data:
        if isinstance(item, list):
            values.append(list_string(item))
        elif isinstance(item, dict):
            values.append(dict_to_table(item))
        elif isinstance(item, str):
            values.append(string(item))
        elif isinstance(item, (bool, int)):
            values.append(item)
        else:
            values.append(item)

    return values


def document_configs(configpath, outpath, header, max_length, split, cleanup):
    """
    This function documents the configuration.

    :param configpath: The path to where the backup files are saved
    :param outpath: The path to save the Markdown document to
    :param header: Header of the configuration being documented
    :param max_length: The maximum length of the configuration to write to the Markdown document
    :param split: Split documentation into multiple files
    :param cleanup: Remove empty values from documentation
    """

    # If configurations path exists, continue
    if os.path.exists(configpath):
        if split:
            outpath = configpath + "/" + header + ".md"
            md_file(outpath)
        with open(outpath, "a") as md:
            md.write("# " + header + "\n")

        pattern = configpath + "*/*"
        for filename in sorted(glob.glob(pattern, recursive=True), key=str.casefold):
            if filename.endswith(".md") or os.path.isdir(filename) or filename == ".DS_Store":
                continue

            # Check which format the file is saved as then open file, load data and set query parameter
            with open(filename) as f:
                if filename.endswith(".yaml"):
                    data = json.dumps(yaml.safe_load(f))
                    repo_data = json.loads(data)
                elif filename.endswith(".json"):
                    f = open(filename)
                    repo_data = json.load(f)

                # Create assignments table
                assignments_table = ""
                assignments_table = assignment_table(repo_data)
                repo_data.pop("assignments", None)

                description = ""
                if "description" in repo_data:
                    if repo_data["description"] is not None:
                        description = repo_data["description"]
                        repo_data.pop("description")

                # Write configuration Markdown table
                config_table_list = []
                for key, value in zip(repo_data.keys(), clean_list(repo_data.values())):
                    if cleanup:
                        if not value and type(value) is not bool:
                            continue

                    if key == "@odata.type":
                        key = "Odata type"

                    else:
                        key = key[0].upper() + key[1:]
                        key = re.findall("[A-Z][^A-Z]*", key)
                        key = " ".join(key)

                    if max_length:
                        if value and isinstance(value, str) and len(value) > max_length:
                            value = "Value too long to display"

                    config_table_list.append([key, value])

                config_table = write_table(config_table_list)

                # Write data to file
                with open(outpath, "a") as md:
                    if "displayName" in repo_data:
                        md.write("## " + repo_data["displayName"] + "\n")
                    if "name" in repo_data:
                        md.write("## " + repo_data["name"] + "\n")
                    if description:
                        md.write(f"Description: {description} \n")
                    if assignments_table:
                        md.write("### Assignments \n")
                        md.write(str(assignments_table) + "\n")
                    md.write(str(config_table) + "\n")


def document_management_intents(configpath, outpath, header, split):
    """
    This function documents the management intents.

    :param configpath: The path to where the backup files are saved
    :param outpath: The path to save the Markdown document to
    :param header: Header of the configuration being documented
    :param split: Split documentation into multiple files
    """

    # If configurations path exists, continue
    if os.path.exists(configpath):
        if split:
            outpath = configpath + "/" + header + ".md"
            md_file(outpath)
        with open(outpath, "a") as md:
            md.write("# " + header + "\n")

        pattern = configpath + "*/*"
        for filename in sorted(glob.glob(pattern, recursive=True), key=str.casefold):
            # If path is Directory, skip
            if os.path.isdir(filename):
                continue
            # If file is .DS_Store, skip
            if filename == ".DS_Store":
                continue

            # Check which format the file is saved as then open file, load data and set query parameter
            with open(filename) as f:
                if filename.endswith(".yaml"):
                    data = json.dumps(yaml.safe_load(f))
                    repo_data = json.loads(data)
                elif filename.endswith(".json"):
                    f = open(filename)
                    repo_data = json.load(f)

                # Create assignments table
                assignments_table = ""
                assignments_table = assignment_table(repo_data)
                repo_data.pop("assignments", None)

                intent_settings_list = []
                for setting in repo_data["settingsDelta"]:
                    setting_definition = setting["definitionId"].split("_")[1]
                    setting_definition = setting_definition[0].upper() + setting_definition[1:]
                    setting_definition = re.findall("[A-Z][^A-Z]*", setting_definition)
                    setting_definition = " ".join(setting_definition)

                    vals = []
                    value = str(remove_characters(setting["valueJson"]))
                    comma = re.findall("[:][^:]*", value)
                    for v in value.split(","):
                        v = v.replace(" ", "")
                        if comma:
                            v = f'**{v.replace(":", ":** ")}'
                        vals.append(v)
                    value = ",".join(vals)
                    value = value.replace(",", "<br />")

                    intent_settings_list.append([setting_definition, value])

                repo_data.pop("settingsDelta")

                description = ""
                if "description" in repo_data:
                    if repo_data["description"] is not None:
                        description = repo_data["description"]
                        repo_data.pop("description")

                intent_table_list = []

                for key, value in zip(repo_data.keys(), clean_list(repo_data.values())):
                    key = key[0].upper() + key[1:]
                    key = re.findall("[A-Z][^A-Z]*", key)
                    key = " ".join(key)

                    if value and isinstance(value, str):
                        if len(value.split(",")) > 1:
                            vals = []
                            for v in value.split(","):
                                v = v.replace(" ", "")
                                v = f'**{v.replace(":", ":** ")}'
                                vals.append(v)
                            value = ",".join(vals)
                            value = value.replace(",", "<br />")

                    intent_table_list.append([key, value])

                table = intent_table_list + intent_settings_list

                config_table = write_table(table)
                # Write data to file
                with open(outpath, "a") as md:
                    if "displayName" in repo_data:
                        md.write("## " + repo_data["displayName"] + "\n")
                    if "name" in repo_data:
                        md.write("## " + repo_data["name"] + "\n")
                    if description:
                        md.write(f"Description: {description} \n")
                    if assignments_table:
                        md.write("### Assignments \n")
                        md.write(str(assignments_table) + "\n")
                    md.write(str(config_table) + "\n")


def get_md_files(configpath):
    """
    This function gets the Markdown files in the configpath directory.
    :return: List of Markdown files
    """
    slash = "/"
    os = platform.uname().system
    if os == "Windows":
        slash = "\\"
    md_files = []
    patterns = ["*/*.md", "*/*/*.md", "*/*/*/*.md"]
    for pattern in patterns:
        for filename in glob.glob(configpath + pattern, recursive=True):
            filepath = filename.split(slash)
            configpathname = configpath.split(slash)[-1]
            filepath = filepath[filepath.index(configpathname) :]
            filepath = "/".join(filepath[1:])

            md_files.append(f"./{filepath}")

    return md_files
