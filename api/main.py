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
    check_for_required_info_for_login,
    check_for_required_info_for_registration,
    check_for_required_info_to_rate_title
)
from database.models import connect_to_db, db
from database.utilities import apply_migrations
from shared.exceptions import PasswordError, LoginError
from shared.project_settings import settings


DATA_CHECK = {
    'login': check_for_required_info_for_login,
    'registration': check_for_required_info_for_registration,
    'rate_process': check_for_required_info_to_rate_title,
    }
app_route = web.RouteTableDef()


@app_route.post('/registration')
async def register(request: web.Request):
    data = await request.json(loads=ujson.loads)
    DATA_CHECK['registration'](data)
    logger.debug(f'User: {data["username"]} is trying to register')
    try:
        response = await register_user(data)
        logger.debug(f'Successful registration by user: {data["username"]}')
        return web.json_response(response, dumps=ujson.dumps)
    except (LoginError, PasswordError) as error:
        response = {'error': str(error)}
        logger.debug(f'Registration error: {error}, user: {data["username"]}')
        return web.json_response(response, dumps=ujson.dumps)


@app_route.post('/login')
async def login(request: web.Request):
    data = await request.json(loads=ujson.loads)
    DATA_CHECK['login'](data)
    logger.debug(f'Authorization attempt by user:{data["username"]}')
    try:
        response = await login_user(data, request)
        logger.debug(f'Successful authorization by user:{data["username"]}')
        return web.json_response(response, dumps=ujson.dumps)
    except LoginError as error:
        response = {'error': str(error)}
        logger.debug(f'Unsuccessful authorization by user:{data["username"]}, error:{error}')
        return web.json_response(response, dumps=ujson.dumps)


@app_route.get('/random_fact')
async def get_random_fact(request: web.Request):
    if not await check_if_user_logged_in(request):
        raise web.HTTPFound('/login')
    session = await get_session(request)
    logger.debug(f'User:{session["username"]}, session id:{session.identity} asked for random info')
    object_description = await get_random_fact()
    response = {'random_fact': object_description}
    return web.json_response(response, dumps=ujson.dumps)


@app_route.get('/random_rated_fact')
async def get_random_rated_fact(request: web.Request):
    if not await check_if_user_logged_in(request):
        raise web.HTTPFound('/login')
    session = await get_session(request)
    logger.debug(f'User:{session["username"]} session_id:{session.identity} asked for random rated fact')
    object_description, title_name = await get_random_rated_fact_info(session)
    response = {'random_rated_fact': object_description, 'title_name': title_name}
    return web.json_response(response, dumps=ujson.dumps)


@app_route.post('/rate_fact')
async def rate_fact(request: web.Request):
    if not await check_if_user_logged_in(request):
        raise web.HTTPFound('/login')
    data = await request.json(loads=ujson.loads)
    DATA_CHECK['rate_process'](data)
    session = await get_session(request)
    username, rate_command, result = await process_rating(data, session)
    logger.debug(f'User: {session["username"]}, session_id:{session.identity} has proceed command: {rate_command}')
    return web.json_response(result, dumps=ujson.dumps)


async def web_app() -> 'web.Application':
    """Start app entrypoint"""
    logger.info('Starting app web app')
    app = web.Application(debug=True)
    storage = await create_redis_storage()
    setup(app, storage)
    app.add_routes(app_route)
    app.on_cleanup.append(on_cleanup)
    await connect_to_db(settings.create_db_uri())
    apply_migrations(settings)
    logger.info('Finishing starting process')
    return app


async def on_cleanup(app: web.Application):
    """Closing connection to db"""
    logger.info('Closing db connection')
    await db.pop_bind().close()
    logger.info('Shutting down web app')
