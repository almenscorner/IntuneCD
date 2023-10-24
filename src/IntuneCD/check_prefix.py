# -*- coding: utf-8 -*-
import re


def check_prefix_match(name, prefix):
    """Match prefix in name"""
    prefix_in_name = re.search(r"(^|\s)" + prefix.lower() + r".*($|\s)", name.lower())
    if not prefix_in_name:
        return False
    return True
