def clamp(value, min_val, max_val):
    """Return a value that is bounded by a minimum and maximum.

    Args:
        value: The value to evaluate.
        min_val: The minimum allowed value.
        max_val: The maximum allowed value.

    Returns:
        The value, constrained between `min_val` and `max_val`.
    """
    return min(max(value, min_val), max_val)


def unsnake(string):
    """Remove underscores from a snake_case string.

    Args:
        string (str): A string containing underscores.

    Returns:
        str: The string with underscores removed.
    """
    return string.replace('_', '')


def unsnake_kwargs(kwargs):
    """Remove underscores from snake_case key"""
    return {unsnake(k): v for k, v in kwargs.items()}
