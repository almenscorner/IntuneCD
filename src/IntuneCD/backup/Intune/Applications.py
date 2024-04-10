# -*- coding: utf-8 -*-
from ...intunecdlib.BaseBackupModule import BaseBackupModule


class ApplicationsBackupModule(BaseBackupModule):
    """A class used to backup Intune Applications

    Attributes:
        CONFIG_ENDPOINT (str): The endpoint to get the data from
        LOG_MESSAGE (str): The message to log when backing up the data
    """

    CONFIG_ENDPOINT = "/beta/deviceAppManagement/mobileApps"
    LOG_MESSAGE = "Backing up Application: "

    def __init__(self, *args, **kwargs):
        """Initializes the ApplicationsBackupModule class

        Args:
            *args: The positional arguments to pass to the base class's __init__ method.
            **kwargs: The keyword arguments to pass to the base class's __init__ method.
        """
        super().__init__(*args, **kwargs)
        self.path = f"{self.path}/Applications/"
        self.audit_filter = self.audit_filter or "componentName eq 'MobileApp'"
        self.assignment_endpoint = (
            self.assignment_endpoint or "deviceAppManagement/mobileApps/"
        )
        self.assignment_extra_url = self.assignment_extra_url or "/assignments"
        self.config_audit_data = True

    def main(self) -> dict[str, any]:
        """The main method to backup the Applications

        Returns:
            dict[str, any]: The results of the backup
        """
        try:
            self.graph_data = self.make_graph_request(
                endpoint=self.endpoint + self.CONFIG_ENDPOINT,
                params={
                    "$filter": "(microsoft.graph.managedApp/appAvailability) eq null or (microsoft.graph.managedApp/appAvailability) "
                    "eq 'lineOfBusiness' or isAssigned eq true"
                },
            )
        except Exception as e:
            self.log(
                tag="error",
                msg=f"Error getting Application data from {self.endpoint + self.CONFIG_ENDPOINT}: {e}",
            )
            return None

        app_ids = [app["id"] for app in self.graph_data["value"]]
        scope_tag_responses = self.batch_request(
            app_ids, "deviceAppManagement/mobileApps/", "?$select=roleScopeTagIds,id"
        )

        # create a list of dicts with the app id and the response
        self.app_ids = [{"id": app_id} for app_id in app_ids]
        # as we must process each app individually, get the assignment data up front
        self.assignment_responses = self.batch_assignment(
            self.app_ids, self.assignment_endpoint, self.assignment_extra_url
        )

        # as we must process each app individually, get the audit data up front
        if self.audit:
            self.audit_data = self.make_audit_request(self.audit_filter)

        for app in self.graph_data["value"]:
            platform = None
            base_path = self.path
            app.pop("description", None)
            scope_tag_data = [v for v in scope_tag_responses if app["id"] == v["id"]]
            if scope_tag_data:
                app["roleScopeTagIds"] = scope_tag_data[0]["roleScopeTagIds"]

            def generate_app_name(app, app_type, suffix=""):
                try:
                    return app["displayName"] + "_" + app_type + suffix
                except Exception as e:
                    self.log(
                        tag="error",
                        msg=f"Error generating app name for {app['id']}: {e}",
                    )
                    return app["displayName"]

            platform_mapping = {
                "ios": "iOS",
                "macos": "macOS",
                "android": "Android",
                "windows": "Windows",
                "microsoft": "Windows",
                "win32": "Windows",
                "office": "Office Suite",
                "webApp": "Web App",
            }

            app_type = app["@odata.type"]
            app_type_lower = app_type.lower()

            for key, value in platform_mapping.items():
                if key in app_type_lower:
                    platform = value
                    break

            if app_type == "#microsoft.graph.iosVppApp":
                app_name = generate_app_name(
                    app, "iOSVppApp", "_" + str(app["vppTokenAppleId"].split("@")[0])
                )
            elif app_type == "#microsoft.graph.macOsVppApp":
                app_name = generate_app_name(
                    app, "macOSVppApp", "_" + str(app["vppTokenAppleId"].split("@")[0])
                )
            elif app_type == "#microsoft.graph.win32LobApp":
                suffix = (
                    "_Win32"
                    if not app["displayVersion"]
                    else "_" + str(app["displayVersion"]).replace(".", "_")
                )
                app_name = generate_app_name(app, "Win32", suffix)
            elif app_type == "#microsoft.graph.windowsMobileMSI":
                app_name = generate_app_name(
                    app, "WinMSI", "_" + str(app["productVersion"]).replace(".", "_")
                )
            else:
                app_name = generate_app_name(app, app_type.split(".")[2])

            self.preset_filename = app_name

            self.path = f"{self.path}{platform}/"

            try:
                app_results = self.process_data(
                    data=app,
                    filetype=self.filetype,
                    path=self.path,
                    name_key="displayName",
                    log_message=self.LOG_MESSAGE,
                    audit_compare_info={"type": "resourceId", "value_key": "id"},
                )
                self.update_results(app_results)
            except Exception as e:
                self.log(tag="error", msg=f"Error processing Application data: {e}")
                return None

            self.path = base_path

        return self.results
