from aiohttp import web


HEALTH_PATH = "/api/v1/health"
HEALTH_NAME = "health"


def redirect(router, route_name):
    location = router[route_name].url_for()
    return web.HTTPFound(location)
