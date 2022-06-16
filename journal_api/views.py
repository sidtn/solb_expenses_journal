from django.contrib.auth.models import User
from rest_framework import viewsets, permissions
from rest_framework.generics import CreateAPIView

from journal_api.core.custom_permissions import IsOwnerOrAdminOrReadOnly
from journal_api.models import Category, Expense
from journal_api.serializers import CategorySerializer, ExpenseSerializer, UserSerializer


class CreateUserView(CreateAPIView):
    model = User
    permission_classes = [permissions.AllowAny]
    serializer_class = UserSerializer


class CategoryAPIViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    permission_classes = [IsOwnerOrAdminOrReadOnly]
    serializer_class = CategorySerializer


class ExpenseAPIViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
