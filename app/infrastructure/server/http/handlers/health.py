"""
HTTP health check.
"""


from aiohttp import web


async def health_check(request: web.Request):
    """Health check handler."""
    return web.json_response({"status": "OK"})
