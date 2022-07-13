import datetime

from journal_api.core.currency_converter import (
    BadResponseFromCurrencyAPI,
    currency_converter,
)
from journal_api.models import Category, Expense


class TotalExpenses:
    def __init__(self, request):
        self.user = request.user
        self.category = request.query_params.get("category")
        self.start_date = request.query_params.get("start_date")
        self.end_date = request.query_params.get("end_date")
        self.currency = request.query_params.get("currency")

    @staticmethod
    def create_exp_dict(expense):
        cat_exp_dict = {
            "category_uuid": expense.category.uuid,
            "category_name": expense.category.name,
            "cat_expenses": [],
        }
        return cat_exp_dict

    @staticmethod
    def get_parent_name(category):
        category_name = ""
        ancestors = category.get_ancestors(include_self=True)
        for cat in ancestors:
            category_name += f"{cat.name}, "
        return category_name.rstrip(", ")

    def get_filter_dict(self):
        if not self.start_date:
            self.start_date = datetime.datetime(2020, 1, 1)
        if not self.end_date:
            self.end_date = datetime.datetime.now()
        filter_dict = {
            "created_at__range": [self.start_date, self.end_date],
        }
        if self.category:
            filter_dict["category__in"] = Category.objects.get(
                uuid=self.category
            ).get_descendants(include_self=True)
        else:
            self.category = "all"

        return filter_dict

    def get_report(self):
        expenses = (
            Expense.objects.filter(
                owner__id=self.user.id, **self.get_filter_dict()
            )
        ).order_by("category__level")
        report = {
            "start_date": self.start_date,
            "end_date": self.end_date,
            "category": self.category,
            "expenses": [],
        }
        showed_cat = []
        for exp in expenses:
            if exp.category not in showed_cat:
                family_expenses = expenses.filter(
                    category__in=exp.category.get_descendants(
                        include_self=True
                    )
                )
                exp_dict = self.create_exp_dict(exp)
                cat_amount = 0
                for f_exp in family_expenses:
                    sub_cat_exp_dict = {
                        "date": f_exp.created_at,
                        "category_uuid": f_exp.category.uuid,
                        "category_name": f_exp.category.name
                        if f_exp.category.get_level() == 0
                        else self.get_parent_name(f_exp.category),
                        "short_description": f_exp.short_description,
                        f_exp.currency.code: f_exp.amount,
                    }

                    exp_dict["cat_expenses"].append(sub_cat_exp_dict)
                    if self.currency:
                        try:
                            convert_to_currency = round(
                                f_exp.amount
                                * currency_converter(
                                    f_exp.currency.code, self.currency
                                ),
                                2,
                            )
                            sub_cat_exp_dict[
                                f"in_{self.currency}"
                            ] = convert_to_currency
                            cat_amount += convert_to_currency
                        except BadResponseFromCurrencyAPI:
                            sub_cat_exp_dict[f"in_{self.currency}"] = None
                    showed_cat.append(f_exp.category)
                if cat_amount:
                    exp_dict[f"amount_in_{self.currency}"] = cat_amount
                report["expenses"].append(exp_dict)

        return report


class TotalExpensesForEmail(TotalExpenses):
    def __init__(self, user, currency, start_date=None, end_date=None):
        self.user = user
        self.start_date = start_date
        self.end_date = end_date
        self.currency = currency
        self.category = None
