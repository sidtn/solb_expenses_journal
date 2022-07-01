import datetime
from journal_api.core.currency_converter import (
    BadResponseFromCurrencyAPI,
    currency_converter,
)
from journal_api.models import Expense


class TotalExpenses:

    def __init__(self, request):
        self.user = request.user
        self.category = request.query_params.get("category")
        self.start_date = request.query_params.get("start_date")
        self.end_date = request.query_params.get("end_date")
        self.currency = request.query_params.get("currency")

    def get_filter_dict(self):
        if not self.start_date:
            self.start_date = datetime.datetime(2020, 1, 1)
        if not self.end_date:
            self.end_date = datetime.datetime.now()
        filter_dict = {
            "created_at__range": [self.start_date, self.end_date],
        }
        if self.category:
            filter_dict["category"] = self.category
        else:
            self.category = "all"

        return filter_dict

    def create_exp_dict(self, expense):
        exp_dict = {
            "date": expense.created_at,
            "category_uuid": expense.category.uuid,
            "category_name": expense.category.name,
            expense.currency.code: expense.amount,
        }
        if self.currency:
            try:
                in_request_currency = round(currency_converter(expense.currency.code, self.currency) * expense.amount, 2)
            except BadResponseFromCurrencyAPI:
                in_request_currency = None
            exp_dict[f"in_{self.currency}"] = in_request_currency
        exp_dict["children"] = []
        return exp_dict

    def get_report(self):
        expenses = (
            Expense.objects.filter(owner__id=self.user.id, **self.get_filter_dict())
        ).order_by("category__level")
        report = {
            "start_date": self.start_date,
            "end_date": self.end_date,
            "category": self.category,
            "expenses": []
        }
        for exp in expenses:
            exp_dict = self.create_exp_dict(exp)
            report["expenses"].append(exp_dict)
            for i in expenses:
                if i.category in exp.category.get_children():
                    d = self.create_exp_dict(i)
                    exp_dict["children"].append(d)

        return report








