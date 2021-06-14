from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import Optional, Any
import json
import itertools


def create_inline_keyboard(
        buttons: list[str],
        queries: Optional[tuple] = None,
        repeat: bool = False,
) -> InlineKeyboardMarkup:
    """Create an inline keyboard to communicate with bot."""
    if repeat:
        queries = (queries[0] for _ in range(len(buttons)))
    if queries is None:
        queries = buttons.copy()

    assert len(queries) <= len(buttons), 'Queries should be less or equal to buttons size'

    keyboard = InlineKeyboardMarkup()
    for button, query in itertools.zip_longest(buttons, queries):
        button_to_add = InlineKeyboardButton(button, callback_data=_callback_data_normalize(query))
        keyboard.add(button_to_add)
    return keyboard


def _callback_data_normalize(data: Any) -> Optional[str]:
    """Process data to appear as str in callbacks"""
    if isinstance(data, str):
        return data
    if isinstance(data, (int, float)):
        return str(data)
    if data is None:
        return None
    return json.dumps(data, ensure_ascii=False)
