"""Correlation ID Middleware — Rastreabilidade ponta a ponta."""

import uuid
import logging
from flask import g, request

logger = logging.getLogger("Correlation")


class CorrelationMiddleware:
    """
    Middleware Flask que injeta Correlation ID em todas as requisições.
    Se o header X-Correlation-ID estiver presente, reutiliza o valor.
    Caso contrário, gera um novo UUID v4.
    """

    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app):
        app.before_request(self._inject_correlation_id)
        app.after_request(self._add_correlation_header)

    @staticmethod
    def _inject_correlation_id():
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        g.correlation_id = correlation_id

    @staticmethod
    def _add_correlation_header(response):
        correlation_id = g.get("correlation_id", "unknown")
        response.headers["X-Correlation-ID"] = correlation_id
        return response
