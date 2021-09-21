from typing import Optional, Union
from dataclasses import dataclass
import alembic.command
import alembic.config
from loguru import logger
from sqlalchemy.engine import RowProxy
from shared.project_settings import ProjectSettings


@dataclass
class CategoryRating:
    category_id: int
    rating_number: int


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


def get_required_categories(
        rated_categories: Optional[list['RowProxy']],
        all_available_categories_ids: list[int],
        amount_of_categories: int
) -> list[int]:
    """Get all unrated categories"""
    if not rated_categories:
        return all_available_categories_ids[amount_of_categories:]
    result = [
        category_id for (rated_category_id, _) in rated_categories
        for category_id in all_available_categories_ids
        if rated_category_id != category_id
    ]
    return result[amount_of_categories:]


def parse_results(
        amount_of_categories: int,
        rated_categories: Optional[list['RowProxy']],
        all_categories_ids: list[int],
) -> list['CategoryRating']:
    """Process parsing results and getting additional categories if needed"""
    result: list['CategoryRating'] = []
    if len(rated_categories) < amount_of_categories:
        unrated_categories = get_required_categories(
            rated_categories,
            all_categories_ids,
            amount_of_categories - len(rated_categories),
        )
        for unrated_category_id in unrated_categories:
            rated_categories.append((unrated_category_id, 0))
    while len(result) < amount_of_categories:
        for (category_id, category_rating) in rated_categories:
            result.append(CategoryRating(category_id, category_rating))
    return result
