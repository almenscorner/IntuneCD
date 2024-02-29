#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module is used to update all group policy configurations in Intune.
"""

import json
import os

from deepdiff import DeepDiff

from ...intunecdlib.check_file import check_file
from ...intunecdlib.diff_summary import DiffSummary
from ...intunecdlib.graph_batch import batch_assignment, get_object_assignment
from ...intunecdlib.graph_request import (
    makeapirequest,
    makeapirequestDelete,
    makeapirequestPatch,
    makeapirequestPost,
)
from ...intunecdlib.load_file import load_file
from ...intunecdlib.process_scope_tags import get_scope_tags_id
from ...intunecdlib.remove_keys import remove_keys
from .update_assignment import post_assignment_update, update_assignment

# Set MS Graph endpoint
ENDPOINT = "https://graph.microsoft.com/beta/deviceManagement/groupPolicyConfigurations"
definition_odata_bind = (
    "https://graph.microsoft.com/beta/deviceManagement/groupPolicyDefinitions('{id}')"
)
presentation_odata_bind = "https://graph.microsoft.com/beta/deviceManagement/groupPolicyDefinitions('{id}')/presentations('{pid}')"


class definition_values_json:
    """Class for creating json for definition values."""

    def __init__(self, definition: dict, presentation: dict):
        self.definition = definition
        self.presentation = presentation
        self.request_json = self.request_json = {
            "added": [],
            "updated": [],
            "deletedIds": [],
        }

    def modify_definition(self, scenario, mem_def_id):
        """
        Create the json for the definition values.

        Args:
            scenario (str): The scenario to which the definition value is added.
            mem_def_id (str): The id of the definition value.
        Returns:
            dict: The json for the definition value.
        """
        d_id = self.definition["definition"]["id"]

        presentation_values = []

        for presentation in self.definition["presentationValues"]:
            if presentation["presentation"].get("required", False) is True:
                default_presentation = {
                    "@odata.type": presentation["@odata.type"],
                    "value": presentation["value"],
                    "presentation@odata.bind": presentation_odata_bind.replace(
                        "{id}", d_id
                    ).replace("{pid}", presentation["presentation"]["id"]),
                }

                presentation_values.append(default_presentation)

        self.request_json[f"{scenario}"].append(
            {
                "enabled": self.definition["enabled"],
                "definition@odata.bind": definition_odata_bind.replace("{id}", d_id),
                "presentationValues": presentation_values,
            }
        )

        if mem_def_id:
            self.request_json[f"{scenario}"][0]["id"] = mem_def_id

        return self.request_json

    def modify_presentation(self, scenario, defval_id, pid):
        """
        Create the json for the presentation values.

        Args:
            scenario (str): The scenario to which the presentation value is added.
            defval_id (str): The id of the definition value.
            pid (str): The id of the presentation value.

        Returns:
            dict: The json for the presentation value.
        """
        d_id = self.definition["definition"]["id"]
        pvid = self.presentation["presentation"]["id"]

        self.request_json[f"{scenario}"].append(
            {
                "id": defval_id,
                "enabled": self.definition["enabled"],
                "definition@odata.bind": definition_odata_bind.replace("{id}", d_id),
                "presentationValues": [
                    {
                        "@odata.type": self.presentation["@odata.type"],
                        "presentation@odata.bind": presentation_odata_bind.replace(
                            "{id}", d_id
                        ).replace("{pid}", pvid),
                    }
                ],
            }
        )

        if pid:
            self.request_json[f"{scenario}"][0]["presentationValues"][0]["id"] = pid
        if self.presentation.get("values"):
            self.request_json[f"{scenario}"][0]["presentationValues"][0][
                "values"
            ] = self.presentation["values"]
        if self.presentation.get("value"):
            self.request_json[f"{scenario}"][0]["presentationValues"][0][
                "value"
            ] = self.presentation["value"]

        return self.request_json


def custom_ingestion_match(data, token):
    """Match definitions from custom ingestion to definitions in Intune."""

    match = 0
    categories = makeapirequest(
        "https://graph.microsoft.com/beta/deviceManagement/groupPolicyCategories?$expand=definitions($select=id, displayName, categoryPath, classType)&$select=id, displayName&$filter=ingestionSource eq 'custom'",
        token,
    )
    # Go through each definition in repo data and compare to Intune data
    for definition in data["definitionValues"]:
        definition["definition"].pop("groupPolicyCategoryId", None)
        # Create string to compare
        repo_def_str = f'{definition["definition"]["classType"]}:{definition["definition"]["displayName"]}:{definition["definition"]["categoryPath"]}'
        # Go through each category and definition in Intune data
        for mem_definition in categories["value"]:
            for mem_def in mem_definition["definitions"]:
                # Create string to compare
                mem_def_str = f'{mem_def["classType"]}:{mem_def["displayName"]}:{mem_def["categoryPath"]}'
                # If the strings match, add the Intune definition id to the repo data
                if repo_def_str == mem_def_str:
                    definition["definition"]["id"] = mem_def["id"]
                    # If the definition id was found, add 1 to match
                    match += 1

    if match == len(data["definitionValues"]):
        return data

    return False


def find_matching_presentations(repo_data, data):
    """Search for matching presentation values in repo data and Intune data."""
    for repo_def in repo_data.get("definitionValues", []):
        for mem_def in data.get("definitionValues", []):
            for repo_pres in repo_def.get("presentationValues", []):
                for mem_pres in mem_def.get("presentationValues", []):
                    repo_label = repo_pres.get("presentation", {}).get("label")
                    mem_label = mem_pres.get("presentation", {}).get("label")
                    if repo_label == mem_label:
                        repo_pres["id"] = mem_pres["id"]
                        repo_pres["presentation"]["id"] = mem_pres["presentation"]["id"]

    return repo_data


def post_presentation_values(definition, presentation, mem_id, scenario, pid, token):
    """
    Post presentation values to a group policy configuration

    Args:
        definition (dict): Definition values from repo
        presentation (dict): Presentation values from repo
        mem_id (str): Group policy configuration ID in Intune
        scenario (str): Scenario to use for API request
        pid (str): Presentation ID in Intune
        token (str): Access token for API requests
    """
    defval_id = None

    # Get definition values from API
    def_vals = makeapirequest(
        f"{ENDPOINT}/{mem_id}/definitionValues?$expand=definition", token
    )

    # Find the matching definition value
    for def_val in def_vals["value"]:
        if def_val["definition"]["id"] == definition["definition"]["id"]:
            defval_id = def_val["id"]
            break

    # If no matching definition value is found, print a message and return
    if defval_id is None:
        label = presentation.get("presentation", {}).get("label", "None")
        print(
            f"No matching definition found for presentation value '{label}'. Skipping..."
        )
        return

    # Prepare definition values data for API request
    j = definition_values_json(definition=definition, presentation=presentation)
    j.modify_presentation(scenario=scenario, defval_id=defval_id, pid=pid)
    request_data = json.dumps(j.request_json)

    # Make API request to update definition values
    makeapirequestPost(
        f"{ENDPOINT}/{mem_id}/updateDefinitionValues", token, None, request_data, 204
    )


def post_definition_values(definition, mem_id, scenario, mem_def_id, token):
    """
    Post definition values to a group policy configuration

    Args:
        definition (dict): Definition values from repo
        mem_id (str): Group policy configuration ID in Intune
        scenario (str): Scenario to use for API request
        mem_def_id (str): Definition ID in Intune
        token (str): Access token for API requests
    """
    # Prepare definition values data for API request
    j = definition_values_json(definition=definition, presentation=None)
    j.modify_definition(scenario=scenario, mem_def_id=mem_def_id)
    request_data = json.dumps(j.request_json)

    # Make API request to update definition values
    makeapirequestPost(
        f"{ENDPOINT}/{mem_id}/updateDefinitionValues/", token, None, request_data, 204
    )


def update_definition(repo_data, data, mem_id, mem_def_ids, token, report=False):
    """
    Update definition and presentation values in a group policy configuration

    Args:
        repo_data (dict): Group policy configuration data from repo
        data (dict): Group policy configuration data from Intune
        mem_id (str): Group policy configuration ID in Intune
        mem_def_ids (str): Definition IDs in Intune
        token (str): Access token for API requests
        report (bool, optional): Run IntuneCD in report mode. Defaults to False.
    """

    diff_summary = {"diffs": [], "count": 0}

    # Go through each definition value in repo data
    for definition in repo_data.get("definitionValues", []):
        def_id = definition["definition"]["id"]
        # If definition does not exist in data or not in mem_def_ids, add it
        if not data.get("definitionValues") or def_id not in mem_def_ids:
            print("Adding definition values")
            if report is False:
                post_definition_values(definition, mem_id, "added", None, token)
            for presentation in definition.get("presentationValues", []):
                if presentation["presentation"].get("required", False) is False:
                    print("Adding presentation values")
                    if report is False:
                        post_presentation_values(
                            definition, presentation, mem_id, "updated", None, token
                        )

        # Go through each definition value in data
        for mem_definition in data.get("definitionValues", []):
            mem_def_id = mem_definition["id"]
            # If definition exists in data, compare and update if necessary
            if definition["definition"]["id"] == mem_definition["definition"]["id"]:
                definition = remove_keys(definition)
                definition_diff = DeepDiff(
                    mem_definition,
                    definition,
                    ignore_order=True,
                    exclude_paths="root['presentationValues']",
                ).get("values_changed", {})

                definition_diff_summary = DiffSummary(
                    data=definition_diff,
                    name=definition["definition"]["displayName"],
                    type="Definition Values",
                )

                diff_summary["diffs"] += definition_diff_summary.diffs
                diff_summary["count"] += definition_diff_summary.count

                # If there are differences, update the definition
                if definition_diff and report is False:
                    post_definition_values(
                        definition, mem_id, "updated", mem_def_id, token
                    )

                for presentation in definition.get("presentationValues", []):
                    for mem_presentation in mem_definition.get(
                        "presentationValues", []
                    ):
                        pid = mem_presentation["id"]
                        if (
                            presentation["presentation"]["id"]
                            == mem_presentation["presentation"]["id"]
                        ):
                            presentation["presentation"].pop(
                                "lastModifiedDateTime", None
                            )
                            presentation["presentation"].pop("createdDateTime", None)
                            presentation.pop("lastModifiedDateTime", None)
                            presentation.pop("createdDateTime", None)
                            presentation.pop("id", None)

                            presentation_diff = DeepDiff(
                                mem_presentation, presentation, ignore_order=True
                            ).get("values_changed", {})

                            presentation_diff_summary = DiffSummary(
                                data=presentation_diff,
                                name=presentation["presentation"]["label"],
                                type="Presentation Values",
                            )

                            diff_summary["diffs"] += presentation_diff_summary.diffs
                            diff_summary["count"] += presentation_diff_summary.count

                            # If there are differences, update the presentation value
                            if presentation_diff and report is False:
                                post_presentation_values(
                                    definition,
                                    presentation,
                                    mem_id,
                                    "updated",
                                    pid,
                                    token,
                                )

                        elif (
                            definition["definition"]["id"]
                            == mem_definition["definition"]["id"]
                            and mem_definition["presentationValues"] is None
                        ):
                            print("Adding presentation values")
                            if report is False:
                                post_presentation_values(
                                    definition,
                                    presentation,
                                    mem_id,
                                    "added",
                                    None,
                                    token,
                                )

    return diff_summary


def update(
    path,
    token,
    assignment=False,
    report=False,
    create_groups=False,
    remove=False,
    scope_tags=None,
):
    """
    This function updates all Group Policy configurations in Intune,
    if the configuration in Intune differs from the JSON/YAML file.

    :param path: Path to where the backup is saved
    :param token: Token to use for authenticating the request
    :param assignment: Boolean to determine if assignments should be updated
    :param report: Boolean to determine if IntuneCD is running in report mode
    """

    # Set config path
    configpath = f"{path}/Group Policy Configurations/"
    diff_summary = []

    if os.path.exists(configpath):
        # Get Group Policy Configurations
        mem_data = makeapirequest(ENDPOINT, token)
        mem_configs = []

        # Get assignments for Group Policy Configurations
        mem_assignments = batch_assignment(
            mem_data,
            "deviceManagement/groupPolicyConfigurations/",
            "/assignments",
            token,
        )

        # Get definitions and presentation values for Group Policy Configurations
        for profile in mem_data["value"]:
            definition_endpoint = (
                f"{ENDPOINT}/{profile['id']}/definitionValues?$expand=definition"
            )
            definitions = makeapirequest(definition_endpoint, token)

            if not definitions:
                continue

            profile["definitionValues"] = definitions["value"]

            for definition in profile["definitionValues"]:
                presentation_endpoint = (
                    f"{ENDPOINT}/{profile['id']}/definitionValues/{definition['id']}/"
                    f"presentationValues?$expand=presentation "
                )
                presentation = makeapirequest(presentation_endpoint, token)
                definition["presentationValues"] = presentation["value"]

            mem_configs.append(profile)

        for filename in os.listdir(configpath):
            data = None
            file = check_file(configpath, filename)
            if file is False:
                continue

            with open(file, encoding="utf-8") as f:
                repo_data = load_file(filename, f)

            assign_obj = {}
            # If assignments exist in repo data, save them and remove them from repo data
            if "assignments" in repo_data:
                assign_obj = repo_data["assignments"]
            repo_data.pop("assignments", None)

            if scope_tags:
                repo_data = get_scope_tags_id(repo_data, scope_tags)

            # If configurations was found in Intune, continue
            if mem_configs:
                for val in mem_configs[:]:
                    # If display name and type matches, add Intune data to data variable
                    if (
                        repo_data["displayName"] == val["displayName"]
                        and repo_data["policyConfigurationIngestionType"]
                        == val["policyConfigurationIngestionType"]
                    ):
                        data = val
                        mem_configs.remove(val)

            # If data was found, continue
            if data:
                print("-" * 90)
                mem_id = data["id"]
                data = remove_keys(data)

                profile_diff = DeepDiff(
                    data,
                    repo_data,
                    ignore_order=True,
                    exclude_paths="root['definitionValues']",
                ).get("values_changed", {})

                diff_profile = DiffSummary(
                    data=profile_diff,
                    name=repo_data["displayName"],
                    type="Group Policy Configuration",
                )

                # If any differences were found on the profile, push them to Intune
                if profile_diff and report is False:
                    request_data = json.dumps(
                        {
                            "displayName": repo_data["displayName"],
                            "description": repo_data["description"],
                            "roleScopeTagIds": repo_data["roleScopeTagIds"],
                        }
                    )

                    q_param = None
                    makeapirequestPatch(
                        f"{ENDPOINT}/{mem_id}",
                        token,
                        q_param,
                        request_data,
                        status_code=200,
                    )

                # Go through each definition in repo data and compare to Intune data
                # If any differences are found, push them to Intune
                mem_def_ids = [
                    val
                    for val in data["definitionValues"]
                    for key, val in val["definition"].items()
                    if key == "id"
                ]

                if repo_data["policyConfigurationIngestionType"] == "custom":
                    repo_data = custom_ingestion_match(repo_data, token)
                    repo_data = find_matching_presentations(repo_data, data)

                diffs = update_definition(
                    repo_data, data, mem_id, mem_def_ids, token, report
                )

                diff_profile.diffs += diffs["diffs"]
                diff_profile.count += diffs["count"]

                # Add diffs to diff_summary
                diff_summary.append(diff_profile)

                # If assignments should be updated, look for updates and push them to Intune
                if assignment and report is False:
                    mem_assign_obj = get_object_assignment(mem_id, mem_assignments)
                    assignment_update = update_assignment(
                        assign_obj, mem_assign_obj, token, create_groups
                    )
                    if assignment_update is not None:
                        request_data = {"assignments": assignment_update}
                        post_assignment_update(
                            request_data,
                            mem_id,
                            "deviceManagement/groupPolicyConfigurations/",
                            "assign",
                            token,
                        )

            else:
                print("-" * 90)
                print(
                    "Group Policy Configuration not found, creating Policy: "
                    + repo_data["displayName"]
                )

                if report is False:
                    # If the configuration is a custom configuration, get all categories and definitions
                    if repo_data["policyConfigurationIngestionType"] == "custom":
                        repo_data = custom_ingestion_match(repo_data, token)
                        if not repo_data:
                            print(
                                "Some definitions was not found, import custom ADMX files to Intune first."
                            )
                            continue

                        for definition in repo_data.get("definitionValues", []):
                            definition["presentationValues"] = []

                    request_data = json.dumps(repo_data)
                    q_param = None
                    post_request = makeapirequestPost(
                        ENDPOINT,
                        token,
                        q_param,
                        request_data,
                        status_code=201,
                    )

                    for definition in repo_data["definitionValues"]:
                        post_definition_values(
                            definition, post_request["id"], "added", None, token
                        )

                        for presentation in definition["presentationValues"]:
                            if (
                                presentation["presentation"].get("required", False)
                                is False
                            ):
                                post_presentation_values(
                                    definition,
                                    presentation,
                                    post_request["id"],
                                    "updated",
                                    None,
                                    token,
                                )

                    mem_assign_obj = []
                    assignment = update_assignment(
                        assign_obj, mem_assign_obj, token, create_groups
                    )

                    if assignment is not None:
                        request_data = {"assignments": assignment}
                        post_assignment_update(
                            request_data,
                            post_request["id"],
                            "deviceManagement/groupPolicyConfigurations/",
                            "assign",
                            token,
                        )
                    print(
                        "Group Policy Configuration created with id: "
                        + post_request["id"]
                    )

        # If any Group Policy Configuration are left in mem_configs, remove them from Intune as they are not in the repo
        if mem_configs is not None and remove is True:
            for val in mem_configs:
                print("-" * 90)
                print(
                    "Removing Group Policy Configuration from Intune: "
                    + val["displayName"]
                )
                if report is False:
                    makeapirequestDelete(
                        f"{ENDPOINT}/{val['id']}", token, status_code=204
                    )

    return diff_summary
