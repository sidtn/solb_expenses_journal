from decimal import Decimal
from unittest.mock import patch

from django.urls import reverse
from rest_framework.test import APITestCase

from journal_api.models import User


class TotalEndpointTest(APITestCase):
    URL = reverse("expense-total-expenses")
    URL_CREATE_EXPENSES = reverse("expense-list")

    fixtures = [
        "users.json",
        "categories.json",
        "currencies.json",
        "expenses.json",
    ]

    def setUp(self):
        user = User.objects.get(username="testuser")
        self.client.force_authenticate(user)

    def test_get_total_expense_without_query(self):
        response = self.client.get(self.URL).json()
        self.assertEqual(len(response["expenses"]), 2)
        self.assertEqual(response["category"], "all")
        self.assertEqual(
            response["expenses"][0]["category_name"], "Auto maintenance"
        )
        self.assertEqual(response["expenses"][1]["category_name"], "Movies")
        self.assertEqual(len(response["expenses"][1]["cat_expenses"]), 3)

    def test_add_new_expense_without_parent_category(self):
        data = {
            "category": "03035046-b756-48ae-80ae-bbae865e8891",
            "amount": 100,
            "currency": "USD",
        }
        self.client.post(self.URL_CREATE_EXPENSES, data, format="json")
        response = self.client.get(self.URL).json()
        self.assertEqual(len(response["expenses"]), 3)

    def test_add_new_expense_with_parent_category(self):
        data = {
            "category": "be45c7c8-a8a8-408b-a7e9-7b2806a93251",
            "amount": 100,
            "currency": "USD",
        }
        self.client.post(self.URL_CREATE_EXPENSES, data, format="json")
        response = self.client.get(self.URL).json()
        self.assertEqual(len(response["expenses"]), 2)
        self.assertEqual(len(response["expenses"][1]["cat_expenses"]), 4)
        self.assertEqual(
            response["expenses"][1]["cat_expenses"][2]["category_name"],
            "Movies, Popcorn",
        )

    def test_get_total_expense_with_query_category(self):
        url = self.URL + "?category=52ca4a0e-5b0c-4451-98c7-e7e0c45997de"
        response = self.client.get(url).json()
        self.assertEqual(len(response["expenses"]), 1)
        self.assertEqual(
            response["category"], "52ca4a0e-5b0c-4451-98c7-e7e0c45997de"
        )

    def test_get_total_expense_with_query_end_date(self):
        url = self.URL + "?end_date=2022-07-01"
        response = self.client.get(url).json()
        self.assertEqual(len(response["expenses"]), 0)

    @patch("journal_api.core.services.currency_converter")
    def test_get_total_expense_with_query_currency(
        self, mock_currency_converter
    ):
        mock_currency_converter.return_value = Decimal(1.0)
        url = self.URL + "?currency=USD"
        response = self.client.get(url).json()
        self.assertEqual(
            response["expenses"][0]["cat_expenses"][0]["in_USD"], 1000.0
        )
        mock_currency_converter.return_value = Decimal(0.5)
        response = self.client.get(url).json()
        self.assertEqual(
            response["expenses"][0]["cat_expenses"][0]["in_USD"], 500.0
        )
