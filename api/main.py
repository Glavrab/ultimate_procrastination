from aiohttp import web
from loguru import logger
from shared.project_settings import settings
from database.utilities import apply_migrations
from database.models import connect_to_db, db


app_route = web.RouteTableDef()


@app_route.get('/')
async def index(request: web.Request):
    return web.Response(text='test')


async def web_app() -> 'web.Application':
    """Start app entrypoint"""
    logger.info('Starting app web app')
    app = web.Application()
    app.add_routes(app_route)
    app.on_cleanup.append(on_shutdown)
    await connect_to_db(settings.create_db_uri())
    apply_migrations(settings)
    logger.info('Finishing starting process')
    return app


async def on_shutdown(app: web.Application):
    """Closing connection to db"""
    logger.info('Closing db connection')
    await db.pop_bind().close()
    logger.info('Shutting down web app')
