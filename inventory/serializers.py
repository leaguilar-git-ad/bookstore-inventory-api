from decimal import Decimal

from rest_framework import serializers

from .models import Book, normalize_isbn, validate_isbn


class BookSerializer(serializers.ModelSerializer):
    isbn = serializers.CharField(max_length=17)
    cost_usd = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal("0.01"),
    )
    stock_quantity = serializers.IntegerField(min_value=0)

    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "author",
            "isbn",
            "cost_usd",
            "selling_price_local",
            "stock_quantity",
            "category",
            "supplier_country",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "selling_price_local",
            "created_at",
            "updated_at",
        ]

    def validate_isbn(self, value):
        normalized = normalize_isbn(value)
        validate_isbn(normalized)

        queryset = Book.objects.filter(isbn=normalized)
        if self.instance is not None:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise serializers.ValidationError(
                "A book with this ISBN already exists."
            )

        return normalized


class EmptySerializer(serializers.Serializer):
    """Serializer for actions that intentionally do not accept a request body."""


class CalculatePriceResponseSerializer(serializers.Serializer):
    """OpenAPI contract returned by POST /books/{id}/calculate-price."""

    book_id = serializers.IntegerField()
    cost_usd = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
    exchange_rate = serializers.DecimalField(
        max_digits=20,
        decimal_places=10,
    )
    cost_local = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    margin_percentage = serializers.IntegerField()
    selling_price_local = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    currency = serializers.CharField(max_length=3)
    calculation_timestamp = serializers.DateTimeField()
