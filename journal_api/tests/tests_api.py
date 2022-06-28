from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from journal_api.models import Category, Currency, User


class UserTests(APITestCase):
    def test_create_user_without_email(self):
        url = reverse("register")
        data = {"username": "testuser", "password": "testpassword"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user(self):
        url = reverse("register")
        data = {
            "username": "testuser",
            "email": "test@email.com",
            "password": "testpassword",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            User.objects.get(username="testuser").username, "testuser"
        )
        self.assertEqual(
            User.objects.get(email="test@email.com").email, "test@email.com"
        )

    def test_login_user(self):
        user = User.objects.create_user(
            "testuser", "test@email.com", "testpassword"
        )
        self.client.force_authenticate(user)
        response = self.client.get(reverse("category-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(reverse("expense-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CategoryTests(APITestCase):

    fixtures = [
        "categories.json",
        "users.json",
    ]

    def test_get_categories_no_authenticated(self):
        url = reverse("category-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_categories_authenticated(self):
        url = reverse("category-list")
        user = User.objects.get(username="dale77")
        self.client.force_authenticate(user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_category(self):
        url = reverse("category-list")
        user = User.objects.get(username="dale77")
        self.client.force_authenticate(user)
        data = {"owner": user.pk, "name": "testcategory"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "testcategory")


class ExpenseTests(APITestCase):

    fixtures = [
        "categories.json",
        "currencies.json",
        "expenses.json",
        "users.json",
    ]

    def test_get_expenses_no_authenticated(self):
        url = reverse("expense-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_expenses_authenticated(self):
        url = reverse("expense-list")
        user = User.objects.create_user(
            "testuser", "test@email.com", "testpassword"
        )
        self.client.force_authenticate(user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_expense(self):
        url = reverse("expense-list")
        user = User.objects.create_user(
            "testuser", "test@email.com", "testpassword"
        )
        self.client.force_authenticate(user)
        data = {
            "owner": user.pk,
            "amount": 10.25,
            "currency": Currency.objects.first().pk,
            "category": Category.objects.first().pk,
            "short_description": "too much water",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["amount"], "10.25")
        self.assertEqual(
            response.data["category"], Category.objects.first().pk
        )
        self.assertEqual(response.data["short_description"], "too much water")

    def test_get_total_expense_without_query(self):
        url = reverse("expense-total-expenses")
        user = User.objects.get(username="dale77")
        self.client.force_authenticate(user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["expenses"]), 3)

    def test_get_total_expense_with_query(self):
        url = reverse("expense-total-expenses") + "?currency=USD"
        user = User.objects.get(username="dale77")
        self.client.force_authenticate(user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_expenses"], Decimal("4985.00"))
