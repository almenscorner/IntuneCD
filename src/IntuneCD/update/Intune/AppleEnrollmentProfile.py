# -*- coding: utf-8 -*-
import os

from ...intunecdlib.BaseUpdateModule import BaseUpdateModule


class AppleEnrollmentProfileUpdateModule(BaseUpdateModule):
    """A class used to update Intune Apple Enrollment Profiles

    Attributes:
        CONFIG_ENDPOINT (str): The endpoint to get the data from
        APP_ENDPOINT (str): The endpoint to get the app data from
    """

    CONFIG_ENDPOINT = "/beta/deviceManagement/depOnboardingSettings/"

    def __init__(self, *args, **kwargs):
        """Initializes the AppleEnrollmentProfileUpdateModule class

        Args:
            *args: The positional arguments to pass to the base class's __init__ method.
            **kwargs: The keyword arguments to pass to the base class's __init__ method.
        """
        super().__init__(*args, **kwargs)
        self.path = f"{self.path}/Enrollment Profiles/Apple/"
        self.config_type = "Apple Enrollment Profile"
        self.exclude_paths = ["root['isDefault']"]
        self.handle_assignment = False
        self.create_config = False

    def _get_profile_item_and_account_id(
        self, profile_data: dict, repo_data: dict
    ) -> tuple[dict, str]:
        """Gets the profile item and account ID of the Apple Enrollment Profile

        Args:
            profile_data (dict): The data of the Apple Enrollment Profile
            repo_data (dict): The data of the Apple Enrollment Profile in the repository

        Returns:
            tuple[dict, str]: The profile item and account ID of the Apple Enrollment Profile
        """
        profile_item = None
        account_id = None
        for profile in profile_data:
            if profile["displayName"] == repo_data["displayName"]:
                profile_item = profile
                account_id = profile_item["id"].split("_")[0]
                break

        if not account_id or not profile_item:
            return None, None

        return profile_item, account_id

    def main(self) -> dict[str, any]:
        """The main method to update the Intune data"""
        if self.path_exists():
            try:
                intune_data = self.get_downstream_data(self.CONFIG_ENDPOINT)
            except Exception as e:
                self.log(tag="error", msg=f"Error getting {self.config_type} data: {e}")
                return None

            profile_ids = [profile["id"] for profile in intune_data["value"]]

            batch_data = self.batch_request(
                profile_ids,
                "deviceManagement/depOnboardingSettings/",
                "/enrollmentProfiles",
            )
            profile_data = [
                value
                for profile in batch_data
                for value in profile["value"]
                if value is not None
            ]

            for filename in os.listdir(self.path):
                self.downstream_id = None
                repo_data = self.load_repo_data(filename)
                if repo_data:
                    repo_data.pop("isDefault", None)
                    self.match_info = {
                        "displayName": repo_data.get("displayName"),
                    }
                    self.name = repo_data.get("displayName")
                    diff_data = self.create_diff_data(self.name, self.config_type)

                    profile_item, account_id = self._get_profile_item_and_account_id(
                        profile_data, repo_data
                    )

                    if not profile_item or not account_id:
                        self.log(
                            tag="error",
                            msg=f"Error getting {self.config_type} {self.name} item or account ID",
                        )
                        continue

                    self.downstream_id = profile_item["id"]
                    config_endpoint = (
                        f"{self.CONFIG_ENDPOINT}{account_id}/enrollmentProfiles/"
                    )

                    try:
                        self.process_update(
                            downstream_data=profile_data,
                            repo_data=repo_data,
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
