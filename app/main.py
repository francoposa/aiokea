import os

from aiohttp import web

from app.infrastructure.server import http


def main():
    app = web.Application()
    http.configure_app(app)
    port = int(os.environ.get("PORT", 8080))
    web.run_app(app, host="0.0.0.0", port=port)
