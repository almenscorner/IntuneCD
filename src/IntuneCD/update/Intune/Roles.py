# -*- coding: utf-8 -*-
import os

from ...intunecdlib.BaseUpdateModule import BaseUpdateModule


class RolesUpdateModule(BaseUpdateModule):
    """A class used to update Intune Roles

    Attributes:
        CONFIG_ENDPOINT (str): The endpoint to get the data from
        APP_ENDPOINT (str): The endpoint to get the app data from
    """

    CONFIG_ENDPOINT = "/beta/deviceManagement/roleDefinitions/"

    def __init__(self, *args, **kwargs):
        """Initializes the RolesUpdateModule class

        Args:
            *args: The positional arguments to pass to the base class's __init__ method.
            **kwargs: The keyword arguments to pass to the base class's __init__ method.
        """
        super().__init__(*args, **kwargs)
        self.path = f"{self.path}/Roles/"
        self.config_type = "Roles"
        self.params = {"$filter": "isBuiltIn eq false"}
        self.exclude_paths = [
            "root['rolePermissions'][0]['actions']",
            "root['roleAssignments']",
            "root['permissions']",
            "root['isBuiltInRoleDefinition']",
            "root['isBuiltIn']",
        ]
        self.handle_assignment = False
        self.post_status_code = 200

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
                    self.match_info = {
                        "displayName": repo_data.get("displayName"),
                    }
                    self.name = repo_data.get("displayName")
                    diff_data = self.create_diff_data(self.name, self.config_type)
                    self.get_pop_keys(
                        repo_data,
                        [
                            "roleAssignments",
                            "permissions",
                            "rolePermissions[0].actions",
                            "isBuiltInRoleDefinition",
                            "isBuiltIn",
                        ],
                        "pop",
                    )

                    try:
                        self.process_update(
                            downstream_data=intune_data["value"],
                            repo_data=repo_data,
                            method="patch",
                            status_code=200,
                            config_endpoint=self.CONFIG_ENDPOINT,
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
