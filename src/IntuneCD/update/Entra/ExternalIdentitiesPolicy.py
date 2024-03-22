# -*- coding: utf-8 -*-
import os

from ...intunecdlib.BaseUpdateModule import BaseUpdateModule


class ExternalIdentitiesPolicyUpdateModule(BaseUpdateModule):
    """A class used to update Entra External Collaboration Settings

    Attributes:
        CONFIG_ENDPOINT (str): The endpoint to get the data from
        APP_ENDPOINT (str): The endpoint to get the app data from
    """

    CONFIG_ENDPOINT = "/beta/policies/externalidentitiespolicy"

    def __init__(self, *args, **kwargs):
        """Initializes the ExternalIdentitiesPolicyUpdateModule class

        Args:
            *args: The positional arguments to pass to the base class's __init__ method.
            **kwargs: The keyword arguments to pass to the base class's __init__ method.
        """
        super().__init__(*args, **kwargs)
        self.path = f"{self.path}/Entra/External Collaboration Settings/"
        self.config_type = "External Collaboration Settings"
        self.handle_assignment = False
        self.get_match = False
        self.url_append_id = False

    def main(self) -> dict[str, any]:
        """The main method to update the Entra data"""
        if self.path_exists():
            try:
                entra_data = self.get_downstream_data(self.CONFIG_ENDPOINT)
            except Exception as e:
                self.log(tag="error", msg=f"Error getting {self.config_type} data: {e}")
                return None

            for filename in os.listdir(self.path):
                if not filename.startswith("external_identities_policy."):
                    continue
                repo_data = self.load_repo_data(filename)
                if repo_data:
                    self.name = "External Identities Policy"
                    diff_data = self.create_diff_data(self.name, self.config_type)
                    update_data = {
                        "allowDeletedIdentitiesDataRemoval": repo_data[
                            "allowDeletedIdentitiesDataRemoval"
                        ],
                        "allowExternalIdentitiesToLeave": repo_data[
                            "allowExternalIdentitiesToLeave"
                        ],
                    }

                    try:
                        self.process_update(
                            downstream_data=entra_data,
                            repo_data=repo_data,
                            method="patch",
                            status_code=204,
                            config_endpoint=self.CONFIG_ENDPOINT,
                            update_data=update_data,
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
