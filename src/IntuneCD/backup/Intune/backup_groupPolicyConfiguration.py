#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module backs up Group Policy Configurations in Intune.
"""

from ...intunecdlib.check_prefix import check_prefix_match
from ...intunecdlib.clean_filename import clean_filename
from ...intunecdlib.graph_batch import batch_assignment, get_object_assignment
from ...intunecdlib.graph_request import makeapirequest, makeAuditRequest
from ...intunecdlib.process_audit_data import process_audit_data
from ...intunecdlib.process_scope_tags import get_scope_tags_name
from ...intunecdlib.remove_keys import remove_keys
from ...intunecdlib.save_output import save_output

# Set MS Graph endpoint
ENDPOINT = "https://graph.microsoft.com/beta/deviceManagement/groupPolicyConfigurations"


# Get all Group Policy Configurations and save them in specified path
def savebackup(path, output, exclude, token, prefix, append_id, audit, scope_tags):
    """
    Saves all Group Policy Configurations in Intune to a JSON or YAML file.

    :param path: Path to save the backup to
    :param output: Format the backup will be saved as
    :param exclude: If "assignments" is in the list, it will not back up the assignments
    :param token: Token to use for authenticating the request
    """

    results = {"config_count": 0, "outputs": []}
    audit_data = None
    configpath = path + "/" + "Group Policy Configurations/"
    data = makeapirequest(ENDPOINT, token)

    assignment_responses = batch_assignment(
        data, "deviceManagement/groupPolicyConfigurations/", "/assignments", token
    )
    if audit:
        graph_filter = "componentName eq 'DeviceConfiguration'"
        audit_data = makeAuditRequest(graph_filter, token)

    for profile in data["value"]:
        if prefix and not check_prefix_match(profile["displayName"], prefix):
            continue

        results["config_count"] += 1
        definition_endpoint = (
            f"{ENDPOINT}/{profile['id']}/definitionValues?$expand=definition"
        )
        # Get definitions
        definitions = makeapirequest(definition_endpoint, token)

        if definitions:
            profile["definitionValues"] = definitions["value"]

            for definition in profile["definitionValues"]:
                presentation_endpoint = (
                    f"{ENDPOINT}/{profile['id']}/definitionValues/{definition['id']}/"
                    f"presentationValues?$expand=presentation "
                )
                presentation = makeapirequest(presentation_endpoint, token)
                definition["presentationValues"] = presentation["value"]

        if scope_tags:
            profile = get_scope_tags_name(profile, scope_tags)

        if "assignments" not in exclude:
            assignments = get_object_assignment(profile["id"], assignment_responses)
            if assignments:
                profile["assignments"] = assignments

        graph_id = profile["id"]
        profile = remove_keys(profile)

        print("Backing up profile: " + profile["displayName"])

        # Get filename without illegal characters
        fname = clean_filename(profile["displayName"])
        if append_id:
            fname = f"{fname}__{graph_id}"

        save_output(output, configpath, fname, profile)

        results["outputs"].append(fname)

        if audit_data:
            compare_data = {"type": "resourceId", "value": graph_id}
            process_audit_data(
                audit_data, compare_data, path, f"{configpath}{fname}.{output}"
            )

    return results
