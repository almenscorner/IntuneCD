# -*- coding: utf-8 -*-
import os

from ...intunecdlib.BaseUpdateModule import BaseUpdateModule


class TemplateUpdateModule(BaseUpdateModule):
    """A class used to update Intune {config_type} data

    Attributes:
        CONFIG_ENDPOINT (str): The endpoint to get the data from
        APP_ENDPOINT (str): The endpoint to get the app data from
    """

    CONFIG_ENDPOINT = (
        "/beta/template/"  # TODO: Change this to the endpoint to get the data from
    )

    def __init__(self, *args, **kwargs):
        """Initializes the {config_type}UpdateModule class

        Args:
            *args: The positional arguments to pass to the base class's __init__ method.
            **kwargs: The keyword arguments to pass to the base class's __init__ method.
        """
        super().__init__(*args, **kwargs)
        self.path = f"{self.path}/Template/"  # TODO: Change this to the path to the data in the backup
        self.config_type = "Template"  # TODO Change this to the type of data
        # TODO: Remove below parameters if not needed
        self.assignment_endpoint = (
            "/"  # TODO: Change this to the endpoint to get the assignments from
        )
        self.assignment_extra_url = (
            "/assign"  # TODO: Change this to the extra URL to get the assignments from
        )
        self.exclude_paths = [
            "root['assignments']",
        ]  # TODO: Change this to the paths to exclude from the diff

    # TODO: If any other helper methods are needed, add them here

    def main(self) -> dict[str, any]:
        """The main method to update the Intune data"""
        if self.path_exists():
            try:
                intune_data = self.get_downstream_data(self.CONFIG_ENDPOINT)
            except Exception as e:
                self.log(tag="error", msg=f"Error getting {self.config_type} data: {e}")
                return None

            # TODO: Remove batch assignment if not needed
            self.downstream_assignments = self.batch_assignment(
                intune_data["value"],
                self.assignment_endpoint,
                "/assignments",
            )

            for filename in os.listdir(self.path):
                repo_data = self.load_repo_data(filename)
                if repo_data:
                    self.match_info = {
                        "displayName": repo_data.get("displayName"),
                        "@odata.type": repo_data.get("@odata.type"),
                    }  # TODO: Change this to the match info of the data
                    self.name = repo_data.get(
                        "displayName"
                    )  # TODO: Change this to the name of the data from the repo file
                    diff_data = self.create_diff_data(self.name, self.config_type)

                    # TODO: Do anything else needed before the update here

                    try:
                        self.process_update(
                            downstream_data=intune_data["value"],
                            repo_data=repo_data,
                            method="patch",  # TODO: Change this to the method to use for the update request
                            status_code=204,  # TODO: Change this to the status code to expect
                            config_endpoint=self.CONFIG_ENDPOINT,
                            # update_data={"settings": repo_data},  # TODO: If patching uses a special data format, add it here, else remove this line
                        )
                    except Exception as e:
                        self.log(
                            tag="error",
                            msg=f"Error updating {self.config_type} {self.name}: {e}",
                        )

                    self.set_diff_data(diff_data)
                    self.diff_summary.append(diff_data)
                    self.reset_diffs_and_count()

            self.remove_downstream_data(self.CONFIG_ENDPOINT, intune_data["value"])

        return self.diff_summary
