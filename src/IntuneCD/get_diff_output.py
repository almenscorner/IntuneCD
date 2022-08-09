#!/usr/bin/env python3

"""
This module is used to get diff output from the diff.
"""

import re


def get_diff_output(data):
    """
    This function takes the data from the diff and returns a string with the differences.

    :param data: The data from the diff
    :return: A string with the differences
    """
    output = []

    for key, value in data.items():
        setting = re.search(
            "\\[(.*)\\]", key).group(1).split("[")[-1]
        new_val = value['new_value']
        old_val = value['old_value']

        output.append(f"Setting: {setting}, New Value: {new_val}, Old Value: {old_val}")

    return output
