import alembic.config
import alembic.command
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

