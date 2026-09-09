from decimal import Decimal
from unittest.mock import Mock, patch

import requests
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Book
from .services import get_exchange_rate


class BookApiTests(APITestCase):
    def setUp(self):
        self.book = Book.objects.create(
            title="El Quijote",
            author="Miguel de Cervantes",
            isbn="9788437604947",
            cost_usd=Decimal("15.99"),
            stock_quantity=5,
            category="Literatura Clasica",
            supplier_country="ES",
        )

    def test_create_rejects_negative_stock(self):
        payload = {
            "title": "Test",
            "author": "Author",
            "isbn": "1234567890",
            "cost_usd": "10.00",
            "stock_quantity": -1,
            "category": "Test",
            "supplier_country": "US",
        }
        response = self.client.post("/books", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_isbn_is_normalized_and_unique(self):
        payload = {
            "title": "Duplicate",
            "author": "Author",
            "isbn": "978-84-376-0494-7",
            "cost_usd": "10.00",
            "stock_quantity": 1,
            "category": "Test",
            "supplier_country": "ES",
        }
        response = self.client.post("/books", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("isbn", response.data)

    @patch("inventory.services.requests.get")
    def test_calculate_price_uses_external_rate(self, mocked_get):
        mocked_response = Mock()
        mocked_response.raise_for_status.return_value = None
        mocked_response.json.return_value = {"rates": {"EUR": 0.85}}
        mocked_get.return_value = mocked_response

        with patch.dict("os.environ", {"LOCAL_CURRENCY": "EUR"}):
            response = self.client.post(f"/books/{self.book.id}/calculate-price")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Decimal(str(response.data["selling_price_local"])), Decimal("19.03"))

        self.book.refresh_from_db()
        self.assertEqual(self.book.selling_price_local, Decimal("19.03"))

    @patch("inventory.services.requests.get")
    def test_exchange_rate_falls_back_when_external_api_fails(self, mocked_get):
        mocked_get.side_effect = requests.RequestException("timeout")

        with patch.dict("os.environ", {"DEFAULT_EXCHANGE_RATE": "1.0"}):
            rate = get_exchange_rate("EUR")

        self.assertEqual(rate, Decimal("1.0"))

    def test_low_stock_uses_threshold(self):
        response = self.client.get("/books/low-stock?threshold=10")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_unknown_book_returns_404(self):
        response = self.client.get("/books/999999")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
