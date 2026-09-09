import logging

from django.db import (
    DatabaseError,
    IntegrityError,
    InterfaceError,
    OperationalError,
)
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler


logger = logging.getLogger(__name__)


def api_exception_handler(exc, context):
    """
    Return consistent JSON errors while preserving the correct HTTP semantics.

    - DRF-managed exceptions keep their native response (400/404/etc.).
    - IntegrityError is treated as a client/data constraint problem -> 400.
    - OperationalError / InterfaceError represent connectivity or DB
      availability problems -> 503.
    - Other DatabaseError instances are internal server errors -> 500.
    - Any other unhandled exception -> 500.

    Detailed exception information is written to the application logs and is
    intentionally not exposed to API consumers.
    """
    response = drf_exception_handler(exc, context)

    if response is not None:
        return response

    if isinstance(exc, IntegrityError):
        logger.warning(
            "Database constraint violation",
            exc_info=True,
        )
        return Response(
            {
                "detail": (
                    "The request violates a database constraint."
                )
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    if isinstance(exc, (OperationalError, InterfaceError)):
        logger.exception(
            "Database service unavailable: %s",
            exc.__class__.__name__,
        )
        return Response(
            {
                "detail": (
                    "Database service is temporarily unavailable."
                )
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    if isinstance(exc, DatabaseError):
        logger.exception(
            "Unexpected database error: %s",
            exc.__class__.__name__,
        )
        return Response(
            {
                "detail": "Internal server error."
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    logger.exception(
        "Unhandled API exception: %s",
        exc.__class__.__name__,
    )
    return Response(
        {
            "detail": "Internal server error."
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
