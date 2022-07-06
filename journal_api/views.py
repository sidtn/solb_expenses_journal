from django.db.models import Q
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from journal_api.core.custom_permissions import IsOwnerOrAdminOrReadOnly
from journal_api.core.services import TotalExpenses
from journal_api.models import Category, Expense
from journal_api.serializers import (
    CategorySerializer,
    ExpenseSerializer,
    TotalExpensesSerializer,
    UserSerializer,
)


class CreateUserView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserSerializer


name = openapi.Parameter(
    "name",
    in_=openapi.IN_QUERY,
    description="Category name",
    type=openapi.TYPE_STRING,
)


class CategoryAPIViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsOwnerOrAdminOrReadOnly, IsAuthenticated]
    sw_tags = ["Categories"]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Category.objects.all()
        elif self.request.user.is_authenticated:
            user = self.request.user
            return Category.objects.filter(Q(owner=user) | Q(owner=None))
        return Category.objects.filter(owner=None)

    @swagger_auto_schema(manual_parameters=[name])
    def list(self, request, *args, **kwargs):
        if request.query_params.get("name"):
            queryset = self.filter_queryset(self.get_queryset()).filter(
                name__icontains=request.query_params.get("name")
            )
        else:
            queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ExpenseAPIViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    permission_classes = [IsOwnerOrAdminOrReadOnly, IsAuthenticated]
    sw_tags = ["Expenses"]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Expense.objects.all()
        elif self.request.user.is_authenticated:
            user = self.request.user
            return Expense.objects.filter(owner=user)
        return Expense.objects.all()

    def create(self, request, *args, **kwargs):

        # old api support --------------------------------
        if request.data["category"].isdigit():
            try:
                category_id = int(request.data["category"])
                category_uuid = Category.objects.values("uuid").get(
                    id=category_id
                )["uuid"]
                request.data._mutable = True
                request.data.update({"category": category_uuid})
            except Category.DoesNotExist:
                pass
        # ------------------------------------------------
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    @swagger_auto_schema(
        query_serializer=TotalExpensesSerializer,
        operation_id="Get total expenses endpoint",
    )
    @action(url_path="total", methods=["GET"], detail=False)
    def total_expenses(self, request):
        qp = TotalExpensesSerializer(data=request.query_params)
        qp.is_valid(raise_exception=True)
        total_expenses = TotalExpenses(self.request).get_report()
        return Response(total_expenses, status=status.HTTP_200_OK)
