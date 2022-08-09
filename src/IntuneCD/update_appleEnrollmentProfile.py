#!/usr/bin/env python3

"""
This module is used to update all Apple Enrollment profiles in Intune.
"""

import json
import os

from deepdiff import DeepDiff
from .graph_request import makeapirequest, makeapirequestPatch
from .remove_keys import remove_keys
from .check_file import check_file
from .load_file import load_file
from .get_diff_output import get_diff_output

# Set MS Graph endpoint
ENDPOINT = "https://graph.microsoft.com/beta/deviceManagement/depOnboardingSettings/"


def update(path, token):
    """
    This function updates all Apple Enrollment Profiles in Intune,
    if the configuration in Intune differs from the JSON/YAML file.

    :param path: Path to where the backup is saved
    :param token: Token to use for authenticating the request
    """

    diff_count = 0
    # Set Apple Enrollment Profile path
    configpath = path + "/" + "Enrollment Profiles/Apple/"
    # If Apple Enrollment Profile path exists, continue
    if os.path.exists(configpath):
        # Get IDs of all Apple Enrollment Profiles and add them to a list
        ids = []
        mem_data_accounts = makeapirequest(ENDPOINT, token)
        for id in mem_data_accounts['value']:
            ids.append(id['id'])

        for profile in ids:
            for filename in os.listdir(configpath):
                file = check_file(configpath, filename)
                if file is False:
                    continue
                # Check which format the file is saved as then open file, load
                # data and set query parameter
                with open(file) as f:
                    repo_data = load_file(filename, f)
                    q_param = {"$filter": "displayName eq " +
                               "'" + repo_data['displayName'] + "'"}

                    # Get Apple Enrollment Profile with query parameter
                    profile_data = makeapirequest(
                        ENDPOINT + profile + '/enrollmentProfiles', token, q_param)

                    # If Apple Enrollment Profile exists, continue
                    if profile_data['value']:
                        print("-" * 90)
                        pid = profile_data['value'][0]['id']
                        # Remove keys before using DeepDiff
                        profile_data['value'][0] = remove_keys(profile_data['value'][0])

                        diff = DeepDiff(
                            profile_data['value'][0],
                            repo_data,
                            ignore_order=True).get(
                            'values_changed',
                            {})

                        # If any changed values are found, push them to Intune
                        if diff:
                            diff_count += 1
                            print(
                                "Updating Apple Enrollment profile: " +
                                repo_data['displayName'] +
                                ", values changed:")
                            values = get_diff_output(diff)
                            for val in values:
                                print(val)
                            request_data = json.dumps(repo_data)
                            q_param = None
                            makeapirequestPatch(
                                ENDPOINT +
                                profile +
                                "/enrollmentProfiles/" +
                                pid,
                                token,
                                q_param,
                                request_data,
                                status_code=204)
                        else:
                            print(
                                'No difference found for Apple Enrollment profile: ' +
                                repo_data['displayName'])

    return diff_count
