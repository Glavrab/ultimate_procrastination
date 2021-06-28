from aiohttp import web
from loguru import logger
from shared.project_settings import settings, ProjectSettings
from database.utilities import apply_migrations
from database.models import connect_to_db, db


app_routes = web.RouteTableDef()


@app_routes.get('/')
async def index(request: web.Request):
    return web.Response(text='test')


async def on_startup(settings: ProjectSettings) -> 'web.Application':
    logger.debug('Starting up web app')
    app = web.Application()
    app.add_routes(app_routes)
    await connect_to_db(settings.create_db_uri())
    apply_migrations(settings)
    return app


def on_shutdown():
    db.pop_bind()


if __name__ == '__main__':
    app = await on_startup(settings)