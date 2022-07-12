from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from journal_api.models import Category, Currency, Limit, User


class UserTests(APITestCase):

    fixtures = ["users.json", "currencies.json"]

    def test_create_user_without_email(self):
        url = reverse("register")
        data = {"username": "test", "password": "password"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user(self):
        url = reverse("register")
        data = {
            "username": "test",
            "email": "test@email.com",
            "password": "password",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.get(username="test").username, "test")
        self.assertEqual(
            User.objects.get(email="test@email.com").email, "test@email.com"
        )
        self.assertIsNotNone(
            Limit.objects.filter(owner__email="test@email.com")
        )

    def test_login_user(self):
        user = User.objects.get(username="testuser")
        self.client.force_authenticate(user)
        response = self.client.get(reverse("category-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(reverse("expense-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CategoryTests(APITestCase):

    fixtures = ["users.json", "currencies.json"]

    def setUp(self):
        user = User.objects.get(username="testuser")
        self.client.force_authenticate(user)

    def test_get_categories_authenticated(self):
        url = reverse("category-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_category(self):
        url = reverse("category-list")
        data = {"name": "testcategory"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "testcategory")


class ExpenseTests(APITestCase):

    fixtures = [
        "users.json",
        "categories.json",
        "currencies.json",
    ]

    def test_get_expenses_no_authenticated(self):
        url = reverse("expense-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_expenses_authenticated(self):
        url = reverse("expense-list")
        user = User.objects.get(username="testuser")
        self.client.force_authenticate(user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_expense(self):
        url = reverse("expense-list")
        user = User.objects.get(username="testuser")
        self.client.force_authenticate(user)
        data = {
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


class LimitTest(APITestCase):

    fixtures = ["users.json", "currencies.json"]

    def setUp(self):
        user = User.objects.get(username="testuser")
        self.client.force_authenticate(user)

    def test_get_to_limits(self):
        url = reverse("limits")
        response = self.client.get(url).json()
        self.assertEqual(response["currency"], "USD")
        self.assertEqual(response["limit_per_week"], None)

    def test_put_to_limits(self):
        url = reverse("limits")
        data = {
            "currency": "BYN",
            "limit_per_week": 1000,
            "limit_per_month": 4000,
        }
        response = self.client.put(url, data, format="json").json()
        print(response)
        self.assertEqual(response["limit_per_week"], "1000.00")
        self.assertEqual(response["limit_per_month"], "4000.00")
        self.assertEqual(response["currency"], "BYN")
