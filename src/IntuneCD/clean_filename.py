#!/usr/bin/env python3

"""
This module is used to remove illegal characters from strings before saving files.
"""


def clean_filename(filename):
    """
    This function removes illegal characters from strings.

    :param filename: The name of file to save
    :return: The cleaned filename
    """

    remove_characters = "/\\:*?<>|"
    if type(filename) != str:
        filename = str(filename)
    for character in remove_characters:
        filename = filename.replace(character, "_")
    return filename
