# -*- coding: utf-8 -*-
import json
import os

from ...intunecdlib.BaseUpdateModule import BaseUpdateModule


class NotificationTemplateUpdateModule(BaseUpdateModule):
    """A class used to update Intune Notification Templates

    Attributes:
        CONFIG_ENDPOINT (str): The endpoint to get the data from
        APP_ENDPOINT (str): The endpoint to get the app data from
    """

    CONFIG_ENDPOINT = "/beta/deviceManagement/notificationMessageTemplates/"

    def __init__(self, *args, **kwargs):
        """Initializes the NotificationTemplateUpdateModule class

        Args:
            *args: The positional arguments to pass to the base class's __init__ method.
            **kwargs: The keyword arguments to pass to the base class's __init__ method.
        """
        super().__init__(*args, **kwargs)
        self.path = f"{self.path}/Compliance Policies/Message Templates/"
        self.handle_assignment = False
        self.params = {"$expand": "localizedNotificationMessages"}
        self.exclude_paths = [
            "root['defaultLocale']",
            "root['localizedNotificationMessages']",
            "root['localizedNotificationMessages@odata.context']",
        ]
        self.post_status_code = 200

    def _handle_locale_diffs(
        self, intune_data: dict[str, any], repo_data: dict[str, any]
    ) -> None:
        """Get the differences between the Intune and repo data for the localizedNotificationMessages

        Args:
            intune_data (dict[str, any]): The Intune data
            repo_data (dict[str, any]): The repo data
        """
        for intune_locale, repo_locale in zip(
            intune_data["localizedNotificationMessages"],
            repo_data["localizedNotificationMessages"],
        ):
            self.name = repo_locale.get("locale")
            if locale_diff := self.get_diffs(
                intune_locale, repo_locale, "root['isDefault']"
            ):
                self.config_type = "Notification Template Locale"
                data = repo_data.copy()
                data.pop("isDefault", None)
                data.pop("locale", None)
                self.update_downstream_data(
                    self.endpoint
                    + self.CONFIG_ENDPOINT
                    + "/"
                    + self.downstream_id
                    + "/"
                    + "localizedNotificationMessages"
                    + "/"
                    + intune_locale["id"],
                    status_code=200,
                    method="patch",
                    data=data,
                )

                self.update_diff_data(locale_diff)

    def _handle_locale_isDefault(
        self, intune_data: dict[str, any], repo_data: dict[str, any]
    ) -> None:
        """Update the isDefault value for the locale

        Args:
            intune_data (dict[str, any]): The Intune data
        """
        for intune_locale, repo_locale in zip(
            intune_data["localizedNotificationMessages"],
            repo_data["localizedNotificationMessages"],
        ):
            repo_locale.pop("locale", None)
            if (
                intune_locale.get("isDefault") != repo_locale.get("isDefault")
                and repo_locale.get("isDefault") is not None
            ):
                if repo_locale["isDefault"] is False:
                    repo_locale.pop("isDefault", None)

                self.log(
                    msg=f"Updating isDefault for {self.name} to {repo_locale.get('isDefault')}",
                    tag="info",
                )

                self.update_downstream_data(
                    self.endpoint
                    + self.CONFIG_ENDPOINT
                    + self.downstream_id
                    + "/"
                    + "localizedNotificationMessages"
                    + "/"
                    + intune_locale["id"],
                    status_code=200,
                    method="patch",
                    data=repo_locale,
                )

    def _post_locale_data(self, repo_data: dict[str, any]) -> None:
        """Post the locale data to Intune

        Args:
            repo_data (dict[str, any]): The repo data
        """
        for locale in repo_data["localizedNotificationMessages"]:
            data = json.dumps(locale)
            self.make_graph_request(
                endpoint=self.endpoint
                + self.CONFIG_ENDPOINT
                + self.create_request["id"]
                + "/localizedNotificationMessages",
                data=data,
                method="post",
            )

    def main(self) -> dict[str, any]:
        """The main method to update the Intune data"""
        if self.path_exists():
            try:
                intune_data = self.get_downstream_data(self.CONFIG_ENDPOINT)
            except Exception as e:
                self.log(tag="error", msg=f"Error getting {self.config_type} data: {e}")
                return None

            # Get Intune data that is not EnrollmentNotificationInternalMEO
            intune_data["value"] = [
                val
                for val in intune_data["value"]
                if val["displayName"] != "EnrollmentNotificationInternalMEO"
            ]

            for filename in os.listdir(self.path):
                # Reset the paramters
                self.create_request = None
                self.config_type = "Notification Template"

                repo_data = self.load_repo_data(filename)
                if repo_data:
                    self.match_info = {
                        "displayName": repo_data.get("displayName"),
                    }
                    self.name = repo_data.get("displayName")
                    diff_data = self.create_diff_data(self.name, self.config_type)
                    update_and_create_data = {
                        "displayName": repo_data.get("displayName"),
                        "description": repo_data.get("description"),
                        "brandingOptions": repo_data.get("brandingOptions"),
                        "roleScopeTagIds": repo_data.get("roleScopeTagIds"),
                    }

                    try:
                        self.process_update(
                            downstream_data=intune_data["value"],
                            repo_data=repo_data,
                            method="patch",
                            status_code=200,
                            config_endpoint=self.CONFIG_ENDPOINT,
                            update_data=update_and_create_data,
                            create_data=update_and_create_data,
                        )
                    except Exception as e:
                        self.log(
                            tag="error",
                            msg=f"Error updating {self.config_type} {self.name}: {e}",
                        )

                    if self.downstream_object:
                        self.params = None
                        self.config_type = "Notification Template Locale"
                        self._handle_locale_diffs(self.downstream_object, repo_data)
                        self._handle_locale_isDefault(self.downstream_object, repo_data)
                    if self.create_request:
                        self.params = None
                        self._post_locale_data(repo_data)

                    self.set_diff_data(diff_data)
                    self.diff_summary.append(diff_data)
                    self.reset_diffs_and_count()

            self.remove_downstream_data(self.CONFIG_ENDPOINT, intune_data["value"])

        return self.diff_summary
