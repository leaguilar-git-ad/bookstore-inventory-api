import logging

from django.db import DatabaseError, IntegrityError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

logger = logging.getLogger(__name__)


def api_exception_handler(exc, context):
    """Return consistent JSON errors for handled and unexpected API failures."""
    response = drf_exception_handler(exc, context)
    if response is not None:
        return response

    if isinstance(exc, IntegrityError):
        logger.warning("Database constraint violation", exc_info=exc)
        return Response(
            {"detail": "The request violates a database constraint."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if isinstance(exc, DatabaseError):
        logger.exception("Database operation failed", exc_info=exc)
        return Response(
            {"detail": "Database service is temporarily unavailable."},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    logger.exception("Unhandled API exception", exc_info=exc)
    return Response(
        {"detail": "Internal server error."},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
