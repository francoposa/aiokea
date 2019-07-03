"""
HTTP health check.
"""

import json
import os
import socket

from aiohttp import web


ENV_INFO_KEYS = [
    "BUILD_DATE",
    "BUILD_URL",
    "GIT_COMMIT",
    "GIT_COMMIT_DATE",
    "IMAGE_NAME",
    "SERVER_HOSTNAME",
    "SERVICE_ID",
    "SERVICE_NAME",
]
INFO = {key.lower(): os.environ.get(key) for key in ENV_INFO_KEYS}
INFO["hostname"] = socket.gethostname()


def _dumps(obj):
    """Pretty JSON"""
    return json.dumps(obj, indent=4, sort_keys=True) + "\n"


async def health_check(request):
    """Health check handler."""
    return web.json_response({"status": "OK"})


async def info(request):
    """Metadata."""
    return web.json_response(INFO, dumps=_dumps)
