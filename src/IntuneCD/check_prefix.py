def check_prefix_match(name, prefix):
    if not name.startswith(prefix) or name[len(prefix)] != " ":
        return False
    else:
        return True
