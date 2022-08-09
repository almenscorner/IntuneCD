#!/usr/bin/env python3

"""
This module is used to save the configuration to a file.
"""

import os
import json
import yaml


def save_output(output, configpath, fname, data):
    """
    This function saves the configuration to a file in JSON or YAML format.

    :param output: The format the configuration will be saved as
    :param configpath: The path to save the configuration to
    :param fname: The filename of the configuration
    :param data: The configuration data
    """

    if not os.path.exists(configpath):
        os.makedirs(configpath)

    if output == 'yaml':
        with open(configpath + fname + ".yaml", 'w') as yamlFile:
            yaml.dump(data, yamlFile, sort_keys=False,
                      default_flow_style=False)
    elif output == 'json':
        with open(configpath + fname + ".json", 'w') as jsonFile:
            json.dump(data, jsonFile, indent=10)

    else:
        raise ValueError("Invalid output format")
