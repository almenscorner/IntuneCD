"""
This module is used to remove illegal characters from strings before saving files.

Parameters
----------
filenasme : str
    The name of file to save
"""

def clean_filename(filename):
    remove_characters = "/\:*?<>|"
    if type(filename) != str:
        filename = str(filename)
    for character in remove_characters:
        filename = filename.replace(character, "_")
    return filename