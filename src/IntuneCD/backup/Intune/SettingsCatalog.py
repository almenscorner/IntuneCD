# -*- coding: utf-8 -*-
from ...intunecdlib.BaseBackupModule import BaseBackupModule


class SettingsCatalogBackupModule(BaseBackupModule):
    """A class used to backup Intune Settings Catalog

    Attributes:
        CONFIG_ENDPOINT (str): The endpoint to get the data from
        LOG_MESSAGE (str): The message to log when backing up the data
    """

    CONFIG_ENDPOINT = "/beta/deviceManagement/configurationPolicies"
    LOG_MESSAGE = "Backing up Settings Catalog Policy: "

    def __init__(self, *args, **kwargs):
        """Initializes the SettingsCatalogBackupModule class

        Args:
            *args: The positional arguments to pass to the base class's __init__ method.
            **kwargs: The keyword arguments to pass to the base class's __init__ method.
        """
        super().__init__(*args, **kwargs)
        self.path = f"{self.path}/Settings Catalog/"
        self.audit_filter = (
            self.audit_filter or "componentName eq 'DeviceConfiguration'"
        )
        self.assignment_endpoint = "deviceManagement/configurationPolicies/"
        self.assignment_extra_url = "/assignments"
        self.config_audit_data = True

    def main(self) -> dict[str, any]:
        """The main method to backup the Settings Catalog

        Returns:
            dict[str, any]: The results of the backup
        """
        try:
            self.graph_data = self.make_graph_request(
                endpoint=self.endpoint + self.CONFIG_ENDPOINT
            )
        except Exception as e:
            self.log(
                tag="error",
                msg=f"Error getting Settings Catalog data from {self.endpoint + self.CONFIG_ENDPOINT}: {e}",
            )
            return None

        item_ids = [item["id"] for item in self.graph_data["value"]]
        item_ids_dict = [{"id": item_id} for item_id in item_ids]
        # As we need to process each item individually, get the assignments up front
        self.assignment_responses = self.batch_assignment(
            item_ids_dict, self.assignment_endpoint, self.assignment_extra_url
        )
        # As we need to process each item individually, get the audit data up front
        if self.audit:
            self.audit_data = self.make_audit_request(self.audit_filter)
        # Get the settings for each policy using batch request
        policy_responses = self.batch_request(
            item_ids, "deviceManagement/configurationPolicies/", "/settings?&top=1000"
        )

        for item in self.graph_data["value"]:
            settings = self.get_object_details(item["id"], policy_responses)
            if settings:
                item["settings"] = settings

            self.preset_filename = (
                f"{item['name']}_{str(item['technologies']).rsplit(',', 1)[-1]}"
            )

            try:
                results = self.process_data(
                    data=item,
                    filetype=self.filetype,
                    path=self.path,
                    name_key="name",
                    log_message=self.LOG_MESSAGE,
                    audit_compare_info={
                        "type": "resourceId",
                        "value_key": "id",
                    },
                )
                self.update_results(results)
            except Exception as e:
                self.log(
                    tag="error", msg=f"Error processing Settings Catalog data: {e}"
                )
                return None

        return self.results
