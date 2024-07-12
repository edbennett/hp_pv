#!/usr/bin/env python3


def get_consistent_metadata(data, key):
    values = set(datum[key] for datum in data)
    if len(values) > 1:
        raise ValueError(
            f"Different {key} values {values} cannot be combined in one fit."
        )

    return values.pop() if values else None
