import datetime

from django.db.models import Q, Sum
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from journal_api.core.custom_permissions import IsOwnerOrAdminOrReadOnly
from journal_api.models import Category, Expense
from journal_api.serializers import (
    CategorySerializer,
    ExpenseSerializer,
    UserSerializer,
)


class CreateUserView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserSerializer


class CategoryAPIViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsOwnerOrAdminOrReadOnly, IsAuthenticated]

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

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Expense.objects.all()
        elif self.request.user.is_authenticated:
            user = self.request.user
            return Expense.objects.filter(owner=user)
        return Expense.objects.all()

    @action(url_path="total", methods=["GET"], detail=False)
    def total_expenses(self, request):
        user = self.request.user
        category = self.request.query_params.get("category")
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")
        if not start_date:
            start_date = datetime.datetime(2020, 10, 17)
        if not end_date:
            end_date = datetime.datetime.now()
        params_dict = {
            "owner__id": user.id,
            "created_at__range": [start_date, end_date],
        }
        if category:
            params_dict["category"] = category
        total_expenses = (
            Expense.objects.filter(**params_dict)
            .values("amount")
            .aggregate(sum=Sum("amount"))
        )
        return Response(
            {"total expenses": total_expenses["sum"]}, status=status.HTTP_200_OK
        )
