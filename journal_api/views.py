from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework import viewsets
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from journal_api.core.custom_permissions import IsOwnerOrAdminOrReadOnly
from journal_api.models import Category, Expense
from journal_api.serializers import (CategorySerializer, ExpenseSerializer,
                                     UserSerializer)


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
