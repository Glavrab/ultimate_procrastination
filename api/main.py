import ujson
from aiohttp import web
from aiohttp_session import setup, get_session
from loguru import logger

from api.utilities import (
    register_user,
    login_user,
    get_random_fact_info,
    create_redis_storage,
    get_random_rated_fact_info,
    process_rating,
    check_for_required_info_for_login,
    check_for_required_info_for_registration,
    check_for_required_info_to_rate_title,
    create_json_response,
    login_required,
    json_required,
    process_email_confirmation
)
from database.models import connect_to_db, db
from database.utilities import apply_migrations
from shared.exceptions import PasswordError, LoginError, EmailError
from shared.project_settings import settings


@json_required
async def register(request: web.Request) -> web.Response:
    data = await request.json(loads=ujson.loads)
    check_for_required_info_for_registration(data)
    logger.debug(f'User: {data["username"]} is trying to register')
    try:
        response = await register_user(data, request)
        logger.debug(f'Successful registration by user: {data["username"]}')
        return create_json_response(response)
    except (LoginError, PasswordError, EmailError) as error:
        response = {'error': str(error)}
        logger.debug(f'Registration error: {error}, user: {data["username"]}')
        return create_json_response(response)


@json_required
async def login(request: web.Request) -> web.Response:
    data = await request.json(loads=ujson.loads)
    check_for_required_info_for_login(data)
    logger.debug(f'Authorization attempt by user:{data["username"]}')
    try:
        response = await login_user(data, request)
        logger.debug(f'Successful authorization by user:{data["username"]}')
        return create_json_response(response)
    except LoginError as error:
        response = {'error': str(error)}
        logger.debug(f'Unsuccessful authorization by user:{data["username"]}, error:{error}')
        return create_json_response(response)


@login_required
async def get_random_fact(request: web.Request) -> web.Response:
    session = await get_session(request)
    logger.debug(f'User:{session["username"]}, session id:{session.identity} asked for random info')
    object_description = await get_random_fact_info()
    response = {'random_fact': object_description}
    return create_json_response(response)


@login_required
async def get_random_rated_fact(request: web.Request) -> web.Response:
    session = await get_session(request)
    logger.debug(f'User:{session["username"]} session_id:{session.identity} asked for random rated fact')
    object_description, title_name = await get_random_rated_fact_info(session)
    response = {'random_rated_fact': object_description, 'title_name': title_name}
    return create_json_response(response)


@login_required
@json_required
async def rate_fact(request: web.Request) -> web.Response:
    data = await request.json(loads=ujson.loads)
    check_for_required_info_to_rate_title(data)
    session = await get_session(request)
    username, rate_command, response = await process_rating(data, session)
    logger.debug(f'User: {session["username"]}, session_id:{session.identity} has proceed command: {rate_command}')
    return create_json_response(response)


async def email_confirmation(request: web.Request):
    """Process email confirmation"""
    return create_json_response(await process_email_confirmation(request))


async def web_app() -> 'web.Application':
    """Start app entrypoint"""
    logger.info('Starting app web app')
    app = web.Application(debug=settings.debug_status)
    storage = await create_redis_storage()
    add_handlers(app)
    setup(app, storage)
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


def add_handlers(app: web.Application):
    """Add handlers"""
    app.add_routes(
        [
            web.get('/email_confirmation/{token}', email_confirmation),
            web.post('/registration', register),
            web.post('/rate_fact', rate_fact),
            web.post('/login', login),
            web.get('/random_fact', get_random_fact),
            web.get('/random_rated_fact', get_random_rated_fact),
        ]
    )
