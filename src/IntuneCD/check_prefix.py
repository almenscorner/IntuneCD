import re


def check_prefix_match(name, prefix):
    prefix_in_name = re.search(r"(^|\s)" + prefix.lower() + r".*($|\s)", name.lower())
    if not prefix_in_name:
        return False
    else:
        return True
