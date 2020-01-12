from aiohttp import web


HEALTH_PATH = "/health"
HEALTH_NAME = "health"

USER_PATH = "/api/v1/users"
USER_NAME = "users"
USER_ID_PATH = "/api/vi/users/{id}"
USER_ID_NAME = "users_id"


def redirect(router, route_name):
    location = router[route_name].url_for()
    return web.HTTPFound(location)
