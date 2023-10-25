#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module is used to load a file into a dictionary.
"""

import json

import yaml


def load_file(filename, file):
    """
    This function loads a JSON or YAML file to a dictionary.
    :param filename: The name of the file.
    :param file: The file to load.
    :return: The dictionary.
    """

    if filename.endswith(".yaml"):
        data = json.dumps(yaml.safe_load(file))
        repo_data = json.loads(data)

    elif filename.endswith(".json"):
        repo_data = json.load(file)

    else:
        raise ValueError(f"{filename} is not a valid file type.")

    return repo_data
