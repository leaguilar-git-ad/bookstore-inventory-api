import re
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q


def normalize_isbn(value: str) -> str:
    return re.sub(r"[-\s]", "", value or "")


def validate_isbn(value: str) -> None:
    normalized = normalize_isbn(value)
    if not re.fullmatch(r"(?:\d{10}|\d{13})", normalized):
        raise ValidationError("ISBN must contain exactly 10 or 13 digits.")


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.CharField(max_length=17, unique=True, validators=[validate_isbn])
    cost_usd = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    selling_price_local = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )
    stock_quantity = models.IntegerField(validators=[MinValueValidator(0)])
    category = models.CharField(max_length=150)
    supplier_country = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["id"]
        constraints = [
            models.CheckConstraint(
                check=Q(cost_usd__gt=0),
                name="book_cost_usd_gt_0",
            ),
            models.CheckConstraint(
                check=Q(stock_quantity__gte=0),
                name="book_stock_quantity_gte_0",
            ),
            models.CheckConstraint(
                check=Q(isbn__regex=r"^\d{10}$") | Q(isbn__regex=r"^\d{13}$"),
                name="book_isbn_10_or_13_digits",
            ),
        ]

    def clean(self):
        super().clean()
        self.isbn = normalize_isbn(self.isbn)
        validate_isbn(self.isbn)

    def save(self, *args, **kwargs):
        self.isbn = normalize_isbn(self.isbn)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.isbn})"
