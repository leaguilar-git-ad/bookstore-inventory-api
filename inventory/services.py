import logging
import os
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

import requests
from django.utils import timezone

logger = logging.getLogger(__name__)

EXCHANGE_RATE_API_URL = os.getenv(
    "EXCHANGE_RATE_API_URL",
    "https://api.exchangerate-api.com/v4/latest/USD",
)
MARGIN_MULTIPLIER = Decimal("1.40")
MARGIN_PERCENTAGE = 40
MONEY_QUANTIZER = Decimal("0.01")


def _decimal_env(name: str, default: str) -> Decimal:
    try:
        return Decimal(os.getenv(name, default))
    except InvalidOperation:
        logger.warning("Invalid %s value. Falling back to %s.", name, default)
        return Decimal(default)


def _timeout_seconds() -> float:
    try:
        return float(os.getenv("EXCHANGE_RATE_TIMEOUT", "5"))
    except ValueError:
        return 5.0


def get_exchange_rate(currency: str) -> Decimal:
    """
    Fetch USD -> target currency rate.

    Any external-service failure uses DEFAULT_EXCHANGE_RATE so the bookstore
    calculation remains available instead of failing the entire request.
    """
    default_rate = _decimal_env("DEFAULT_EXCHANGE_RATE", "1.0")

    try:
        response = requests.get(EXCHANGE_RATE_API_URL, timeout=_timeout_seconds())
        response.raise_for_status()
        payload = response.json()
        raw_rate = payload["rates"][currency]
        rate = Decimal(str(raw_rate))

        if rate <= 0:
            raise ValueError("Exchange rate must be greater than zero")

        return rate
    except (requests.RequestException, ValueError, KeyError, TypeError, InvalidOperation) as exc:
        logger.warning(
            "Exchange-rate API failed for currency=%s. Using fallback rate=%s. Error=%s",
            currency,
            default_rate,
            exc,
        )
        return default_rate


def calculate_and_persist_price(book):
    currency = os.getenv("LOCAL_CURRENCY", "EUR").upper()
    exchange_rate = get_exchange_rate(currency)

    cost_local_raw = book.cost_usd * exchange_rate
    selling_price_raw = book.cost_usd * exchange_rate * MARGIN_MULTIPLIER

    cost_local = cost_local_raw.quantize(MONEY_QUANTIZER, rounding=ROUND_HALF_UP)
    selling_price_local = selling_price_raw.quantize(
        MONEY_QUANTIZER,
        rounding=ROUND_HALF_UP,
    )

    book.selling_price_local = selling_price_local
    book.save(update_fields=["selling_price_local", "updated_at"])

    return {
        "book_id": book.id,
        "cost_usd": book.cost_usd,
        "exchange_rate": exchange_rate,
        "cost_local": cost_local,
        "margin_percentage": MARGIN_PERCENTAGE,
        "selling_price_local": selling_price_local,
        "currency": currency,
        "calculation_timestamp": timezone.now(),
    }
