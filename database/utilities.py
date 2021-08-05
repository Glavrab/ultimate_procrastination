from typing import Optional

import alembic.command
import alembic.config
from loguru import logger

from shared.project_settings import ProjectSettings


def apply_migrations(settings: ProjectSettings):
    """Apply migrations based on project settings"""
    alembic_config = alembic.config.Config('alembic.ini')
    logger.info("Applying alembic migration")
    alembic_config.attributes["configure_logger"] = False
    alembic_config.set_main_option(
        "sqlalchemy.url",
        settings.create_db_uri(),
    )
    alembic.command.upgrade(alembic_config, settings.apply_migration)
    logger.info('finishing applying migrations')


def get_unrated_categories(
        rated_categories_ids: list[Optional[int]],
        all_available_categories_ids: list[int],
        amount_of_categories: int
) -> list[int]:
    """Get all unrated categories"""
    result = []
    if not rated_categories_ids:
        return all_available_categories_ids[amount_of_categories:]
    while amount_of_categories > 0:
        for rated_category, category in rated_categories_ids, all_available_categories_ids:
            if rated_category == category:
                pass
            else:
                amount_of_categories -= 1
                result.append(category)
    return result
