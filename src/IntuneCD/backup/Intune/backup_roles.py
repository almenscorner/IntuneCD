#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module backs up all Roles in Intune.
"""

from ...intunecdlib.clean_filename import clean_filename
from ...intunecdlib.graph_request import makeapirequest, makeAuditRequest
from ...intunecdlib.process_audit_data import process_audit_data
from ...intunecdlib.process_scope_tags import get_scope_tags_name
from ...intunecdlib.remove_keys import remove_keys
from ...intunecdlib.save_output import save_output

# Set MS Graph endpoint
ENDPOINT = "https://graph.microsoft.com/beta/deviceManagement/roleDefinitions"


# Get all Roles and save them in specified path
def savebackup(path, output, exclude, token, append_id, audit, scope_tags):
    """
    Saves all Roles in Intune to a JSON or YAML file.

    :param path: Path to save the backup to
    :param output: Format the backup will be saved as
    :param token: Token to use for authenticating the request
    """

    def _get_group_names(obj):
        """
        This function gets the group name from the object.

        :param object: The object to get the group name from.
        :return: The group name.
        """

        groups = []

        for group in obj:
            group_name = makeapirequest(
                f"https://graph.microsoft.com/beta/groups/{group}",
                token,
                "?$select=displayName",
            )

            if group_name:
                group_name = group_name["displayName"]
                groups.append(group_name)

        return groups

    results = {"config_count": 0, "outputs": []}
    audit_data = None
    configpath = path + "/" + "Roles/"
    q_param = {"$filter": "isBuiltIn eq false"}
    data = makeapirequest(ENDPOINT, token, q_param)
    if audit:
        graph_filter = "componentName eq 'RoleBasedAccessControl'"
        audit_data = makeAuditRequest(graph_filter, token)

    for role in data["value"]:
        results["config_count"] += 1
        print("Backing up Role: " + role["displayName"])

        if scope_tags:
            role = get_scope_tags_name(role, scope_tags)
        if "assignments" not in exclude:
            assignments = makeapirequest(
                ENDPOINT + f"/{role['id']}/roleAssignments", token
            )

            if assignments["value"]:
                role["roleAssignments"] = []
                for assignment in assignments["value"]:
                    role_assignment = makeapirequest(
                        f"https://graph.microsoft.com/beta/deviceManagement/roleAssignments/{assignment['id']}",
                        token,
                    )

                role["roleAssignments"].append(role_assignment)

                # Get the scopeMembers and resourceScopes ids
                scope_member_names = ""
                member_names = ""
                for assignment in role["roleAssignments"]:
                    remove_keys(assignment)
                    if assignment.get("scopeMembers"):
                        scope_member_names = _get_group_names(
                            assignment["scopeMembers"]
                        )

                    if scope_member_names:
                        assignment["scopeMembers"] = scope_member_names
                    assignment.pop("resourceScopes", None)

                    for assignment in role["roleAssignments"]:
                        if assignment.get("members"):
                            member_names = _get_group_names(assignment["members"])

                    assignment["members"] = member_names

        graph_id = role["id"]
        role = remove_keys(role)
        role.pop("permissions", None)
        role["rolePermissions"][0].pop("actions", None)

        # Get filename without illegal characters
        fname = clean_filename(role["displayName"])
        if append_id:
            fname = f"{fname}__{graph_id}"
        # Save Compliance policy as JSON or YAML depending on configured
        # value in "-o"
        save_output(output, configpath, fname, role)

        results["outputs"].append(fname)

        if audit_data:
            compare_data = {"type": "resourceId", "value": graph_id}
            process_audit_data(
                audit_data, compare_data, path, f"{configpath}{fname}.{output}"
            )

    return results
