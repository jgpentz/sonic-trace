# utils.py
def normalize_prefix(prefix):
    if "/" not in prefix:
        return prefix + "/32"
    return prefix