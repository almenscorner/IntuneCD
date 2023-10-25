#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module is used to check if a file is a YAML or JSON file.
"""

import os


def check_file(configpath, filename):
    """
    Check if file is YAML or JSON, if true return the file, if not return False.

    :param configpath: The path to the config file
    :param filename: The name of the file
    :return: The file or False
    """

    file = os.path.join(configpath, filename)
    if file.endswith(".yaml"):
        return file
    if file.endswith(".json"):
        return file
    return False
