from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from journal_api.models import Category, Currency, User


class TotalEndpointTest(APITestCase):
    URL = reverse("expense-total-expenses")
    URL_CREATE_EXPENSES = reverse("expense-list")

    fixtures = [
        "categories.json",
        "currencies.json",
        "users.json",
    ]

    def setUp(self):
        user = User.objects.get(username="dale77")
        self.client.force_authenticate(user)
        for _ in range(1, 6):
            data = {
                "category": "2f74be53-4638-4cea-88d2-5613e4620cec",
                "amount": _,
                "currency": "BYN"
            }
            self.client.post(self.URL_CREATE_EXPENSES, data=data)
        for _, currency in enumerate(["USD", "BYN", "EUR"], start=1):
            data = {
                "category": "2f74be53-4638-4cea-88d2-5613e4620cec",
                "amount": _,
                "currency": currency
            }
            self.client.post(self.URL_CREATE_EXPENSES, data=data)

    def test_get_total_expense_without_query_one_currency(self):
        response = self.client.get(self.URL).json()
        self.assertEqual(response["expenses"][0]["currency"], "BYN")
        self.assertEqual(response["expenses"][0]["total_expenses"], 17.0)

    def test_get_total_expenses_without_query_many_currencies(self):
        response = self.client.get(self.URL).json()
        self.assertEqual(len(response["expenses"]), 3)
        self.assertEqual(response["expenses"][2]["currency"], "USD")
        self.assertEqual(response["expenses"][2]["total_expenses"], 1.0)
