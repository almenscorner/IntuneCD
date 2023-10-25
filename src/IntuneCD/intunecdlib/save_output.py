#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module is used to save the configuration to a file.
"""

import json
import os

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

    if output == "yaml":
        with open(configpath + fname + ".yaml", "w", encoding="utf-8") as yamlFile:
            yaml.dump(data, yamlFile, sort_keys=False, default_flow_style=False)
    elif output == "json":
        with open(configpath + fname + ".json", "w", encoding="utf-8") as jsonFile:
            json.dump(data, jsonFile, indent=5)

    else:
        raise ValueError("Invalid output format")
