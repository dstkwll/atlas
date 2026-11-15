"""Comparison for the acyclic built-in values in local evaluator fixtures."""


def same_value(left, right):
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        if len(left) != len(right):
            return False
        return all(any(same_value(key, other) and same_value(value, right[other])
                       for other in right) for key, value in left.items())
    if isinstance(left, (list, tuple)):
        return len(left) == len(right) and all(same_value(a, b) for a, b in zip(left, right))
    return left == right
