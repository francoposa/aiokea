"""
Custom, JSON-formatted HTTP errors.
"""

import json

from aiohttp import web


async def api_error_handler(
    request: web.Request, response: web.Response
) -> web.Response:
    """Provide an API-friendly error message.
    The body can either be a simple text message, in which case it is sent as the "message" field.
    Otherwise the body is JSON-encoded data containing two fields:
        message: A summary description of the error.
        reasons: A dict, in which the keys are components, and the values are lists of error
            messages.
    Because API "helpfully" adds a period at the end of an error message, we strip them out here.
    """

    try:
        err_data = json.loads(response.text)  # Might not be JSON.
        if not isinstance(err_data, dict):
            raise ValueError  # If JSON, must be a object/dict.

        return web.json_response(err_data, status=response.status)

    except (json.JSONDecodeError, ValueError):
        return web.json_response(
            {
                "success": False,
                "status": response.status,
                "message": response.text.rstrip("."),
            },
            status=response.status,
        )


ERROR_HANDLERS = {
    400: api_error_handler,
    403: api_error_handler,
    404: api_error_handler,
    409: api_error_handler,
    415: api_error_handler,
    500: api_error_handler,
    503: api_error_handler,
}
