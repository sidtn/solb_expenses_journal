from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from journal_api.core.custom_permissions import IsOwnerOrAdminOrReadOnly
from journal_api.core.response_examples import (
    response_total_expenses_schema_dict,
)
from journal_api.core.services import TotalExpenses
from journal_api.filters import CategoryFilter, ExpenseFilter
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


class CategoryAPIViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsOwnerOrAdminOrReadOnly, IsAuthenticated]
    sw_tags = ["Categories"]
    filter_backends = [DjangoFilterBackend]
    filterset_class = CategoryFilter

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Category.objects.all()
        elif self.request.user.is_authenticated:
            user = self.request.user
            return Category.objects.filter(Q(owner=user) | Q(owner=None))
        return Category.objects.filter(owner=None)


class ExpenseAPIViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    permission_classes = [IsOwnerOrAdminOrReadOnly, IsAuthenticated]
    sw_tags = ["Expenses"]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ExpenseFilter

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
        responses=response_total_expenses_schema_dict,
    )
    @action(
        url_path="total", methods=["GET"], detail=False, filterset_class=None
    )
    def total_expenses(self, request):
        qp = TotalExpensesSerializer(data=request.query_params)
        qp.is_valid(raise_exception=True)
        total_expenses = TotalExpenses(self.request).get_report()
        return Response(total_expenses, status=status.HTTP_200_OK)
