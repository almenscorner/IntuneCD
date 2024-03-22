# -*- coding: utf-8 -*-
import os

from ...intunecdlib.BaseUpdateModule import BaseUpdateModule


class AuthenticationMethodsConfigurationsUpdateModule(BaseUpdateModule):
    """A class used to update Entrata Authentication Methods

    Attributes:
        CONFIG_ENDPOINT (str): The endpoint to get the data from
        APP_ENDPOINT (str): The endpoint to get the app data from
    """

    CONFIG_ENDPOINT = "/beta/policies/authenticationMethodsPolicy"

    def __init__(self, *args, **kwargs):
        """Initializes the TemplateUpdateModule class

        Args:
            *args: The positional arguments to pass to the base class's __init__ method.
            **kwargs: The keyword arguments to pass to the base class's __init__ method.
        """
        super().__init__(*args, **kwargs)
        self.path = f"{self.path}/Entra/Authentication Methods/"
        self.config_type = "Authentication Methods Configuration"
        self.handle_assignment = False
        self.exclude_paths = [
            "root['id']",
            "root['featureSettings']['numberMatchingRequiredState']",
        ]
        self.get_match = False

    def main(self) -> dict[str, any]:
        """The main method to update the Intune data"""
        if self.path_exists():
            try:
                entra_data = self.get_downstream_data(self.CONFIG_ENDPOINT)
            except Exception as e:
                self.log(tag="error", msg=f"Error getting {self.config_type} data: {e}")
                return None

            for filename in os.listdir(self.path):
                repo_data = self.load_repo_data(filename)
                if repo_data:
                    for entra_config, repo_config in zip(
                        entra_data["authenticationMethodConfigurations"],
                        repo_data["authenticationMethodConfigurations"],
                    ):
                        self.name = repo_config["id"]
                        diff_data = self.create_diff_data(self.name, self.config_type)
                        config_endpoint = f"{self.CONFIG_ENDPOINT}/authenticationMethodConfigurations/"
                        self.get_pop_keys(
                            entra_config,
                            [
                                "featureSettings.numberMatchingRequiredState",
                            ],
                        )

                        try:
                            self.process_update(
                                downstream_data=entra_config,
                                repo_data=repo_config,
                                method="patch",
                                status_code=204,
                                config_endpoint=config_endpoint,
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
