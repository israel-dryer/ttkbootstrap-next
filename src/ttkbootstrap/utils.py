def clamp(value, min_val, max_val):
    """Return a value that is bounded by a min and max.

    Parameters
    ----------
    value : Any
        The amount of evaluate

    min_val : Any
        The minimum allowed value

    max_val : Any
        The maximum allowed value

    Returns
    -------
    Any
        The bounded value
    """
    return min(max(value, min_val), max_val)