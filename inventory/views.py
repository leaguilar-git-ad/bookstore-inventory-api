from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Book
from .serializers import (
    BookSerializer,
    CalculatePriceResponseSerializer,
    EmptySerializer,
)
from .services import calculate_and_persist_price


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    @extend_schema(
        summary="Search books by category",
        description=(
            "Returns books whose category matches the supplied value "
            "case-insensitively. Results use the API's global pagination."
        ),
        parameters=[
            OpenApiParameter(
                name="category",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description="Category to search for (case-insensitive exact match).",
            )
        ],
        responses={
            200: BookSerializer(many=True),
            400: OpenApiResponse(
                description="The category query parameter is missing."
            ),
        },
    )
    @action(detail=False, methods=["get"], url_path="search")
    def search(self, request):
        category = request.query_params.get("category")
        if not category:
            return Response(
                {"category": ["This query parameter is required."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = self.filter_queryset(
            self.get_queryset().filter(category__iexact=category.strip())
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="List books with low stock",
        description=(
            "Returns books whose stock quantity is less than or equal to the "
            "threshold. The default threshold is 10. Results use the API's "
            "global pagination."
        ),
        parameters=[
            OpenApiParameter(
                name="threshold",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                default=10,
                description="Maximum stock quantity considered low stock.",
            )
        ],
        responses={
            200: BookSerializer(many=True),
            400: OpenApiResponse(
                description="Threshold is not a non-negative integer."
            ),
        },
    )
    @action(detail=False, methods=["get"], url_path="low-stock")
    def low_stock(self, request):
        raw_threshold = request.query_params.get("threshold", "10")

        try:
            threshold = int(raw_threshold)
        except (TypeError, ValueError):
            return Response(
                {"threshold": ["Must be a non-negative integer."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if threshold < 0:
            return Response(
                {"threshold": ["Must be a non-negative integer."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = self.filter_queryset(
            self.get_queryset().filter(stock_quantity__lte=threshold)
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Calculate suggested selling price",
        description=(
            "Loads the book's USD cost, obtains the configured USD-to-local "
            "exchange rate, applies the required 40% profit margin, persists "
            "selling_price_local, and returns the detailed calculation. "
            "No request body is required."
        ),
        request=None,
        responses={
            200: CalculatePriceResponseSerializer,
            404: OpenApiResponse(description="Book not found."),
            500: OpenApiResponse(description="Unexpected server error."),
            503: OpenApiResponse(
                description="A critical dependent service is unavailable."
            ),
        },
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="calculate-price",
        serializer_class=EmptySerializer,
    )
    def calculate_price(self, request, pk=None):
        book = self.get_object()
        result = calculate_and_persist_price(book)
        return Response(result, status=status.HTTP_200_OK)
