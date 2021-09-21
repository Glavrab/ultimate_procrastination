from enum import EnumMeta
from typing import Union


def get_all_enum_values(
        enum: EnumMeta,
) -> list[Union[str, int]]:
    """Get all enum fields values"""
    value_map = map(lambda x: getattr(x, 'value'), enum.__members__.values())
    return list(value_map)
