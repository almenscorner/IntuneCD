#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module is used to log messages if verbose is set to True.
"""

import os
import time

verbose = os.getenv("VERBOSE")


def log(function, msg):
    """Prints a message to the console if the VERBOSE environment variable is set to True.

    Args:
        function (str): The name of the function that is calling the log function.
        msg (str): The message to print to the console.
    """
    if verbose:
        msg = f"[{time.asctime()}] - [{function}] - {msg}"
        print(msg)
