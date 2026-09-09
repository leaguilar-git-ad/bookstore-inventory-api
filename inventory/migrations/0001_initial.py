from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import migrations, models

import inventory.models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Book",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=255)),
                ("author", models.CharField(max_length=255)),
                (
                    "isbn",
                    models.CharField(
                        max_length=17,
                        unique=True,
                        validators=[inventory.models.validate_isbn],
                    ),
                ),
                (
                    "cost_usd",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=10,
                        validators=[MinValueValidator(Decimal("0.01"))],
                    ),
                ),
                (
                    "selling_price_local",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        max_digits=12,
                        null=True,
                    ),
                ),
                (
                    "stock_quantity",
                    models.IntegerField(validators=[MinValueValidator(0)]),
                ),
                ("category", models.CharField(max_length=150)),
                ("supplier_country", models.CharField(max_length=100)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ["id"]},
        ),
        migrations.AddConstraint(
            model_name="book",
            constraint=models.CheckConstraint(
                check=models.Q(("cost_usd__gt", 0)),
                name="book_cost_usd_gt_0",
            ),
        ),
        migrations.AddConstraint(
            model_name="book",
            constraint=models.CheckConstraint(
                check=models.Q(("stock_quantity__gte", 0)),
                name="book_stock_quantity_gte_0",
            ),
        ),
        migrations.AddConstraint(
            model_name="book",
            constraint=models.CheckConstraint(
                check=(
                    models.Q(("isbn__regex", r"^\d{10}$"))
                    | models.Q(("isbn__regex", r"^\d{13}$"))
                ),
                name="book_isbn_10_or_13_digits",
            ),
        ),
    ]
