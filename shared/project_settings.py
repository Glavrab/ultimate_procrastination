"""Project settings"""
import ujson

from pydantic import BaseModel
import pathlib


class ProjectSettings(BaseModel):
    telegram_token: str
    apply_migration: str
    pg_host: str
    pg_username: str
    pg_password: str
    pg_port: int
    pg_db: str
    debug_status: bool
    redis_password: str

    project_dir = pathlib.Path(__file__).parent.parent.resolve()

    @classmethod
    def load_settings_from_json_file(cls, config_path: pathlib.Path) -> 'ProjectSettings':
        """Load project settings from config.json file"""
        config = ujson.load(config_path.open('r'))
        return cls(
            telegram_token=config.get('telegram_token'),
            apply_migration=config.get('apply_migration'),
            pg_host=config.get('pg_host'),
            pg_username=config.get('pg_username'),
            pg_password=config.get('pg_password'),
            pg_port=config.get('pg_port'),
            pg_db=config.get('pg_db'),
            debug_status=config.get('debug_status'),
            redis_password=config.get('redis_password'),
        )

    def create_db_uri(self) -> str:
        """Create correct db uri"""
        db_uri = f'postgres://{self.pg_username}:{self.pg_password}@{self.pg_host}:{self.pg_port}/{self.pg_db}'
        return db_uri


settings = ProjectSettings.load_settings_from_json_file(pathlib.Path('./config.json'))
