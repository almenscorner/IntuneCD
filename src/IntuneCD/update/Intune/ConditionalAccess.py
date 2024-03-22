# -*- coding: utf-8 -*-
import copy
import os

from ...intunecdlib.BaseUpdateModule import BaseUpdateModule


class ConditionalAccessUpdateModule(BaseUpdateModule):
    """A class used to update Conditional Access

    Attributes:
        CONFIG_ENDPOINT (str): The endpoint to get the data from
        APP_ENDPOINT (str): The endpoint to get the app data from
    """

    CONFIG_ENDPOINT = "/beta/identity/conditionalAccess/policies/"

    def __init__(self, *args, **kwargs):
        """Initializes the ConditionalAccessUpdateModule class

        Args:
            *args: The positional arguments to pass to the base class's __init__ method.
            **kwargs: The keyword arguments to pass to the base class's __init__ method.
        """
        super().__init__(*args, **kwargs)
        self.path = f"{self.path}/Conditional Access/"
        self.config_type = "Conditional Access"
        self.handle_assignment = False
        self.exclude_paths = [
            "root['conditions']['users']",
            "root['templateId']",
            "root['grantControls']['authenticationStrength']['combinationConfigurations@odata.context']",
            "root['grantControls']['authenticationStrength@odata.context']",
        ]
        self.handle_assignment = False

    def main(self) -> dict[str, any]:
        """The main method to update the Intune data"""
        if self.path_exists():
            try:
                intune_data = self.get_downstream_data(self.CONFIG_ENDPOINT)
            except Exception as e:
                self.log(tag="error", msg=f"Error getting {self.config_type} data: {e}")
                return None

            for filename in os.listdir(self.path):
                repo_data = self.load_repo_data(filename)
                if repo_data:
                    self.get_pop_keys(
                        repo_data,
                        [
                            "conditions.users",
                            "templateId",
                            "grantControls.authenticationStrength.combinationConfigurations@odata.context",
                        ],
                        "pop",
                    )
                    self.match_info = {
                        "displayName": repo_data.get("displayName"),
                    }
                    self.name = repo_data.get("displayName")
                    diff_data = self.create_diff_data(self.name, self.config_type)

                    # Create a new instance of the repo data to avoid modifying the original data
                    update_data = copy.deepcopy(repo_data)
                    auth_strength = self.get_pop_keys(
                        update_data, ["grantControls.authenticationStrength"], "get"
                    )
                    if auth_strength:
                        auth_strength_id = (
                            update_data["grantControls"]
                            .get("authenticationStrength", {})
                            .get("id")
                        )
                        update_data["grantControls"]["authenticationStrength"] = (
                            {"id": auth_strength_id} if auth_strength_id else None
                        )
                        update_data["grantControls"]["operator"] = (
                            "AND" if auth_strength_id else None
                        )

                    # Create a new instance of the update data to avoid modifying the original data
                    create_data = copy.deepcopy(update_data)
                    # Users is a required key, set to None as updating assignment is currently not supported
                    create_data["conditions"]["users"] = {"includeUsers": ["None"]}

                    try:
                        self.process_update(
                            downstream_data=intune_data["value"],
                            repo_data=repo_data,
                            method="patch",
                            status_code=204,
                            config_endpoint=self.CONFIG_ENDPOINT,
                            update_data=update_data,
                            create_data=create_data,
                        )
                    except Exception as e:
                        self.log(
                            tag="error",
                            msg=f"Error updating {self.config_type} {self.name}: {e}",
                        )

                    self.set_diff_data(diff_data)
                    self.diff_summary.append(diff_data)
                    self.reset_diffs_and_count()

        return self.diff_summary
