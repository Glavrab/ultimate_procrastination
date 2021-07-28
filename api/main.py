import ujson
from aiohttp import web
from aiohttp_session import setup, get_session
from loguru import logger

from api.utilities import (
    register_user,
    login_user,
    get_random_fact,
    check_if_user_logged_in,
    create_redis_storage,
    get_random_rated_fact_info,
    process_rating,
)
from database.models import connect_to_db, db
from database.utilities import apply_migrations
from shared.exceptions import PasswordError, LoginError
from shared.project_settings import settings


app_route = web.RouteTableDef()


@app_route.post('/registration')
async def register(request: web.Request):
    data = await request.json(loads=ujson.loads)
    logger.debug(f'User: {data["username"]} is trying to register')
    try:
        response = await register_user(data)
        logger.debug(f'Successful registration by user: {data["username"]}')
        return web.json_response(response, dumps=ujson.dumps)
    except (LoginError, PasswordError) as error:
        response = {'error': str(error)}
        logger.debug(f'Registration error: {error}, user: {data["username"]}')
        return web.json_response(response, dumps=ujson.dumps)



async def web_app() -> 'web.Application':
    """Start app entrypoint"""
    logger.info('Starting app web app')
    app = web.Application(debug=True)
    storage = await create_redis_storage()
    setup(app, storage)
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
