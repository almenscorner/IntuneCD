# -*- coding: utf-8 -*-
import json
import os

from ...intunecdlib.BaseUpdateModule import BaseUpdateModule


class GroupPolicyConfigurationsUpdateModule(BaseUpdateModule):
    """A class used to update Intune GroupPolicyConfigurations data

    Attributes:
        CONFIG_ENDPOINT (str): The endpoint to get the data from
        APP_ENDPOINT (str): The endpoint to get the app data from
    """

    CONFIG_ENDPOINT = "/beta/deviceManagement/groupPolicyConfigurations/"

    def __init__(self, *args, **kwargs):
        """Initializes the GroupPolicyConfigurationsUpdateModule class

        Args:
            *args: The positional arguments to pass to the base class's __init__ method.
            **kwargs: The keyword arguments to pass to the base class's __init__ method.
        """
        super().__init__(*args, **kwargs)
        self.path = f"{self.path}/Group Policy Configurations/"
        self.assignment_endpoint = "/deviceManagement/groupPolicyConfigurations/"
        self.assignment_extra_url = "/assign"
        self.exclude_paths = ["root['assignments']", "root['definitionValues']"]
        self.remove_status_code = 204

    class definition_values_json:
        """Class for creating json for definition values."""

        DEFINITION_ODATA_BIND = "https://graph.microsoft.com/beta/deviceManagement/groupPolicyDefinitions('{id}')"
        PRESENTATION_ODATA_BIND = "https://graph.microsoft.com/beta/deviceManagement/groupPolicyDefinitions('{id}')/presentations('{pid}')"

        def __init__(self, definition: dict, presentation: dict):
            self.definition = definition
            self.presentation = presentation
            self.request_json = self.request_json = {
                "added": [],
                "updated": [],
                "deletedIds": [],
            }

        def modify_definition(self, scenario, intune_definition_id):
            """
            Create the json for the definition values.

            Args:
                scenario (str): The scenario to which the definition value is added.
                intune_definition_id (str): The id of the definition value.
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
                        "presentation@odata.bind": self.PRESENTATION_ODATA_BIND.replace(
                            "{id}", d_id
                        ).replace("{pid}", presentation["presentation"]["id"]),
                    }

                    presentation_values.append(default_presentation)

            self.request_json[f"{scenario}"].append(
                {
                    "enabled": self.definition["enabled"],
                    "definition@odata.bind": self.DEFINITION_ODATA_BIND.replace(
                        "{id}", d_id
                    ),
                    "presentationValues": presentation_values,
                }
            )

            if intune_definition_id:
                self.request_json[f"{scenario}"][0]["id"] = intune_definition_id

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
                    "definition@odata.bind": self.DEFINITION_ODATA_BIND.replace(
                        "{id}", d_id
                    ),
                    "presentationValues": [
                        {
                            "@odata.type": self.presentation["@odata.type"],
                            "presentation@odata.bind": self.PRESENTATION_ODATA_BIND.replace(
                                "{id}", d_id
                            ).replace(
                                "{pid}", pvid
                            ),
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

    def custom_ingestion_match(self, data: dict) -> dict:
        """Match definitions from custom ingestion to definitions in Intune."""

        match = 0
        categories = self.make_graph_request(
            self.endpoint
            + "/beta/deviceManagement/groupPolicyCategories?$expand=definitions($select=id, displayName, categoryPath, classType)&$select=id, displayName&$filter=ingestionSource eq 'custom'",
        )
        # Go through each definition in repo data and compare to Intune data
        for definition in data["definitionValues"]:
            definition["definition"].pop("groupPolicyCategoryId", None)
            # Create string to compare
            repo_def_str = f'{definition["definition"]["classType"]}:{definition["definition"]["displayName"]}:{definition["definition"]["categoryPath"]}'
            # Go through each category and definition in Intune data
            for intune_definition in categories["value"]:
                for intune_definition in intune_definition["definitions"]:
                    # Create string to compare
                    intune_definition_str = f'{intune_definition["classType"]}:{intune_definition["displayName"]}:{intune_definition["categoryPath"]}'
                    # If the strings match, add the Intune definition id to the repo data
                    if repo_def_str == intune_definition_str:
                        definition["definition"]["id"] = intune_definition["id"]
                        # If the definition id was found, add 1 to match
                        match += 1

        if match == len(data["definitionValues"]):
            return data

        return False

    def find_matching_presentations(self, repo_data: dict, data: dict) -> dict:
        """Search for matching presentation values in repo data and Intune data."""
        for repo_def in repo_data.get("definitionValues", []):
            for intune_definition in data.get("definitionValues", []):
                for repo_pres in repo_def.get("presentationValues", []):
                    for intune_presentation in intune_definition.get(
                        "presentationValues", []
                    ):
                        repo_label = repo_pres.get("presentation", {}).get("label")
                        intune_label = intune_presentation.get("presentation", {}).get(
                            "label"
                        )
                        if repo_label == intune_label:
                            repo_pres["id"] = intune_presentation["id"]
                            repo_pres["presentation"]["id"] = intune_presentation[
                                "presentation"
                            ]["id"]

        return repo_data

    def post_presentation_values(
        self,
        definition: dict,
        presentation: dict,
        intune_id: str,
        scenario: str,
        pid: str,
    ):
        """
        Post presentation values to a group policy configuration

        Args:
            definition (dict): Definition values from repo
            presentation (dict): Presentation values from repo
            intune_id (str): Group policy configuration ID in Intune
            scenario (str): Scenario to use for API request
            pid (str): Presentation ID in Intune
        """
        defval_id = None

        # Get definition values from API
        def_vals = self.make_graph_request(
            self.endpoint
            + self.CONFIG_ENDPOINT
            + f"{intune_id}/definitionValues?$expand=definition"
        )

        # Find the matching definition value
        for def_val in def_vals["value"]:
            if def_val["definition"]["id"] == definition["definition"]["id"]:
                defval_id = def_val["id"]
                break

        # If no matching definition value is found, print a message and return
        if defval_id is None:
            label = presentation.get("presentation", {}).get("label", "None")
            self.log(
                tag="warning",
                msg=f"No matching definition found for presentation value '{label}'. Skipping...",
            )
            return

        # Prepare definition values data for API request
        json_data = self.definition_values_json(
            definition=definition, presentation=presentation
        )
        json_data.modify_presentation(scenario=scenario, defval_id=defval_id, pid=pid)
        request_data = json.dumps(json_data.request_json)

        # Make API request to update definition values
        self.make_graph_request(
            endpoint=self.endpoint
            + self.CONFIG_ENDPOINT
            + f"{intune_id}/updateDefinitionValues/",
            method="post",
            data=request_data,
            status_code=204,
        )

    def post_definition_values(
        self, definition: dict, intune_id: str, scenario: str, intune_definition_id: str
    ):
        """
        Post definition values to a group policy configuration

        Args:
            definition (dict): Definition values from repo
            intune_id (str): Group policy configuration ID in Intune
            scenario (str): Scenario to use for API request
            intune_definition_id (str): Definition ID in Intune
        """
        # Prepare definition values data for API request
        json_data = self.definition_values_json(
            definition=definition, presentation=None
        )
        json_data.modify_definition(
            scenario=scenario, intune_definition_id=intune_definition_id
        )
        request_data = json.dumps(json_data.request_json)

        # Make API request to update definition values
        self.make_graph_request(
            endpoint=self.endpoint
            + self.CONFIG_ENDPOINT
            + f"{intune_id}/updateDefinitionValues/",
            method="post",
            data=request_data,
            status_code=204,
        )

    def update_definition(
        self, repo_data: dict, data: dict, intune_id: str, intune_definition_ids: list
    ):
        """
        Update definition and presentation values in a group policy configuration

        Args:
            repo_data (dict): Group policy configuration data from repo
            data (dict): Group policy configuration data from Intune
            intune_id (str): Group policy configuration ID in Intune
            intune_definition_ids (str): Definition IDs in Intune
        """
        self.notify = False
        # Go through each definition value in repo data
        for definition in repo_data.get("definitionValues", []):
            def_id = definition["definition"]["id"]
            # If definition does not exist in data or not in intune_definition_ids, add it
            if not data.get("definitionValues") or def_id not in intune_definition_ids:
                self.log(msg="Adding definition values")
                self.post_definition_values(definition, intune_id, "added", None)
                for presentation in definition.get("presentationValues", []):
                    if presentation["presentation"].get("required", False) is False:
                        self.log(msg="Adding presentation values")
                        self.post_presentation_values(
                            definition, presentation, intune_id, "updated", None
                        )

            # Go through each definition value in data
            for intune_definition in data.get("definitionValues", []):
                intune_definition_id = intune_definition["id"]
                # If definition exists in data, compare and update if necessary
                if (
                    definition["definition"]["id"]
                    == intune_definition["definition"]["id"]
                ):
                    definition = self.remove_keys(definition)
                    # self.config_type = "Definition Value"
                    # self.name = definition["definition"]["displayName"]
                    definition_diff = self.get_diffs(
                        definition,
                        intune_definition,
                        [
                            "root['presentationValues']",
                            "root['definition']['groupPolicyCategoryId']",
                            "root['lastModifiedDateTime']",
                        ],
                    )

                    # If there are differences, update the definition
                    if definition_diff:
                        self.message = "Updating definition values, values changed:"
                        self.update_diff_data(definition_diff)
                        self.post_definition_values(
                            definition, intune_id, "updated", intune_definition_id
                        )

                    for presentation in definition.get("presentationValues", []):
                        for intune_presentation in intune_definition.get(
                            "presentationValues", []
                        ):
                            presentation_id = intune_presentation["id"]
                            if (
                                presentation["presentation"]["id"]
                                == intune_presentation["presentation"]["id"]
                            ):
                                self.get_pop_keys(
                                    presentation,
                                    ["id", "lastModifiedDateTime", "createdDateTime"],
                                    "pop",
                                )
                                self.get_pop_keys(
                                    presentation["presentation"],
                                    ["lastModifiedDateTime", "createdDateTime"],
                                    "pop",
                                )

                                presentation_diff = self.get_diffs(
                                    presentation,
                                    intune_presentation,
                                    ["root['lastModifiedDateTime']"],
                                )

                                # If there are differences, update the presentation value
                                if presentation_diff:
                                    self.message = (
                                        "Updating presentation values, values changed:"
                                    )
                                    self.update_diff_data(presentation_diff)
                                    self.post_presentation_values(
                                        definition,
                                        presentation,
                                        intune_id,
                                        "updated",
                                        presentation_id,
                                    )

                            elif (
                                definition["definition"]["id"]
                                == intune_definition["definition"]["id"]
                                and intune_definition["presentationValues"] is None
                            ):
                                self.log(msg="Adding presentation values")
                                self.post_presentation_values(
                                    definition,
                                    presentation,
                                    intune_id,
                                    "added",
                                    None,
                                )

    def main(self) -> dict[str, any]:
        """The main method to update the Intune data"""
        if self.path_exists():
            try:
                intune_data = self.get_downstream_data(self.CONFIG_ENDPOINT)
            except Exception as e:
                self.log(tag="error", msg=f"Error getting {self.config_type} data: {e}")
                return None

            self.downstream_assignments = self.batch_assignment(
                intune_data["value"],
                self.assignment_endpoint,
                "/assignments",
            )

            intune_profiles = []
            for profile in intune_data["value"]:
                definitions = self.make_graph_request(
                    endpoint=self.endpoint
                    + self.CONFIG_ENDPOINT
                    + profile["id"]
                    + "/definitionValues",
                    params={"$expand": "definition"},
                )

                if not definitions:
                    continue

                profile["definitionValues"] = definitions["value"]

                for definition in profile["definitionValues"]:
                    presentation = self.make_graph_request(
                        endpoint=self.endpoint
                        + self.CONFIG_ENDPOINT
                        + profile["id"]
                        + "/definitionValues/"
                        + definition["id"]
                        + "/presentationValues",
                        params={"$expand": "presentation"},
                    )
                    definition["presentationValues"] = presentation["value"]

                intune_profiles.append(profile)

            for filename in os.listdir(self.path):
                repo_data = self.load_repo_data(filename)
                if repo_data:
                    self.create_request = None
                    self.config_type = "Group Policy Configuration"
                    self.notify = True
                    self.match_info = {
                        "displayName": repo_data.get("displayName"),
                        "policyConfigurationIngestionType": repo_data.get(
                            "policyConfigurationIngestionType"
                        ),
                    }
                    self.name = repo_data.get("displayName")
                    diff_data = self.create_diff_data(self.name, self.config_type)
                    update_data = {
                        "displayName": repo_data["displayName"],
                        "description": repo_data["description"],
                        "roleScopeTagIds": repo_data["roleScopeTagIds"],
                    }

                    if repo_data["policyConfigurationIngestionType"] == "custom":
                        repo_data = self.custom_ingestion_match(repo_data)
                        if not repo_data:
                            self.log(
                                tag="warning",
                                msg=f"Some definitions was not found for {self.name}, import custom ADMX files to Intune first.",
                            )
                            continue

                    try:
                        self.process_update(
                            downstream_data=intune_profiles,
                            repo_data=repo_data,
                            method="patch",
                            status_code=200,
                            config_endpoint=self.CONFIG_ENDPOINT,
                            update_data=update_data,
                        )
                    except Exception as e:
                        self.log(
                            tag="error",
                            msg=f"Error updating {self.config_type} {self.name}: {e}",
                        )

                    if self.downstream_object:
                        intune_definition_ids = [
                            val
                            for val in self.downstream_object["definitionValues"]
                            for key, val in val["definition"].items()
                            if key == "id"
                        ]

                        if repo_data["policyConfigurationIngestionType"] == "custom":
                            repo_data = self.custom_ingestion_match(repo_data)
                            repo_data = self.find_matching_presentations(
                                repo_data, self.downstream_object
                            )

                        self.update_definition(
                            repo_data,
                            self.downstream_object,
                            self.downstream_id,
                            intune_definition_ids,
                        )

                    if self.create_request:
                        if repo_data["policyConfigurationIngestionType"] == "custom":
                            for definition in repo_data.get("definitionValues", []):
                                definition["presentationValues"] = []

                        for definition in repo_data["definitionValues"]:
                            self.post_definition_values(
                                definition,
                                self.create_request["id"],
                                "added",
                                None,
                            )

                            for presentation in definition["presentationValues"]:
                                if (
                                    presentation["presentation"].get("required", False)
                                    is False
                                ):
                                    self.post_presentation_values(
                                        definition,
                                        presentation,
                                        self.create_request["id"],
                                        "updated",
                                        None,
                                    )

                    self.set_diff_data(diff_data)
                    self.diff_summary.append(diff_data)
                    self.reset_diffs_and_count()

            self.remove_downstream_data(self.CONFIG_ENDPOINT, intune_profiles)

        return self.diff_summary
