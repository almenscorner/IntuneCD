# -*- coding: utf-8 -*-
from ...intunecdlib.BaseBackupModule import BaseBackupModule


class RolesBackupModule(BaseBackupModule):
    """A class used to backup Intune Roles

    Attributes:
        CONFIG_ENDPOINT (str): The endpoint to get the data from
        LOG_MESSAGE (str): The message to log when backing up the data
    """

    CONFIG_ENDPOINT = "/beta/deviceManagement/roleDefinitions"
    LOG_MESSAGE = "Backing up Role: "

    def __init__(self, *args, **kwargs):
        """Initializes the RolesBackupModule class

        Args:
            *args: The positional arguments to pass to the base class's __init__ method.
            **kwargs: The keyword arguments to pass to the base class's __init__ method.
        """
        super().__init__(*args, **kwargs)
        self.path = f"{self.path}/Roles/"
        self.audit_filter = "componentName eq 'RoleBasedAccessControl'"

    def _get_group_names(self, item) -> list:
        """Gets the group names from the group ids

        Args:
            item (dict): The group ids

        Returns:
            list: The group names
        """
        groups = []

        for group in item:
            try:
                group_name = self.make_graph_request(
                    endpoint=f"https://graph.microsoft.com/beta/groups/{group}",
                    params={"$select": "displayName"},
                )
            except Exception as e:
                self.log(
                    tag="error",
                    msg=f"Error getting group data from {self.endpoint + self.CONFIG_ENDPOINT}: {e}",
                )
                return None

            if group_name:
                group_name = group_name["displayName"]
                groups.append(group_name)

        return groups

    def main(self) -> dict[str, any]:
        """The main method to backup the Roles

        Returns:
            dict[str, any]: The results of the backup
        """
        try:
            self.graph_data = self.make_graph_request(
                endpoint=self.endpoint + self.CONFIG_ENDPOINT,
                params={"$filter": "isBuiltIn eq false"},
            )
        except Exception as e:
            self.log(
                tag="error",
                msg=f"Error getting Role data from {self.endpoint + self.CONFIG_ENDPOINT}: {e}",
            )
            return None

        for item in self.graph_data["value"]:
            if "assignments" not in self.exclude:
                assignments = self.make_graph_request(
                    self.endpoint
                    + self.CONFIG_ENDPOINT
                    + f"/{item['id']}/roleAssignments"
                )

                if assignments["value"]:
                    item["roleAssignments"] = []
                    for assignment in assignments["value"]:
                        role_assignment = self.make_graph_request(
                            f"{self.endpoint}/beta/deviceManagement/roleAssignments/{assignment['id']}",
                        )

                        item["roleAssignments"].append(role_assignment)

                    # Get the scopeMembers and resourceScopes ids
                    scope_member_names = ""
                    member_names = ""
                    for assignment in item["roleAssignments"]:
                        self.remove_keys(assignment)
                        if assignment.get("scopeMembers"):
                            scope_member_names = self._get_group_names(
                                assignment["scopeMembers"]
                            )

                        if scope_member_names:
                            assignment["scopeMembers"] = scope_member_names
                        assignment.pop("resourceScopes", None)

                        if assignment.get("members"):
                            member_names = self._get_group_names(assignment["members"])

                        assignment["members"] = member_names

            item.pop("permissions", None)
            item["rolePermissions"][0].pop("actions", None)

        # Skip assignments for this module
        self.has_assignments = False

        try:
            self.results = self.process_data(
                data=self.graph_data["value"],
                filetype=self.filetype,
                path=self.path,
                name_key="displayName",
                log_message=self.LOG_MESSAGE,
                audit_compare_info={"type": "resourceId", "value_key": "id"},
            )
        except Exception as e:
            self.log(tag="error", msg=f"Error processing Role data: {e}")
            return None

        return self.results
