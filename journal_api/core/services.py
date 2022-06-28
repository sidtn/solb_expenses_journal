import datetime
from decimal import Decimal

from django.db.models import Sum

from journal_api.models import Expense
from journal_api.core.currency_converter import currency_converter, BadResponseFromCurrencyAPI


def get_total_expenses(request):

    """
    :param request:
    :return: total expenses by time, category and currency.
    Returns the result for the user's currencies, if it is not explicitly specified in the query parameters.
    """

    user = request.user
    category = request.query_params.get("category")
    start_date = request.query_params.get("start_date")
    end_date = request.query_params.get("end_date")
    currency = request.query_params.get("currency")
    convert_to = request.query_params.get("convertto")
    if not start_date:
        start_date = datetime.datetime(2020, 1, 1)
    if not end_date:
        end_date = datetime.datetime.now()
    params_dict = {
        "created_at__range": [start_date, end_date],
    }
    if category:
        params_dict["category"] = category
    if currency:
        params_dict["currency"] = currency
        total_expenses = (
            Expense.objects.filter(owner__id=user.id, **params_dict)
            .values("amount")
            .aggregate(sum=Sum("amount"))
        )
        report = {
            "start_date": start_date,
            "end_date": end_date,
            "category": category,
            "currency": currency,
            "total_expenses": total_expenses["sum"],
        }
        if convert_to and total_expenses["sum"]:
            to_currency = convert_to
            try:
                convert_result = currency_converter(currency, to_currency, total_expenses["sum"])
                report[f"sum in {to_currency}"] = round(convert_result, 2)
            except BadResponseFromCurrencyAPI:
                report[f"sum in {to_currency}"] = "conversion is not available now"
        return report

    expenses = []
    user_expenses_currencies = (
        Expense.objects.filter(owner__id=user.id).values("currency").distinct()
    )
    for currency in user_expenses_currencies:
        total = (
            Expense.objects.filter(
                owner__id=user.id, **params_dict, currency=currency["currency"]
            )
            .values("amount")
            .aggregate(sum=Sum("amount"))
        )
        if total["sum"]:
            expenses.append(
                {
                    "currency": currency["currency"],
                    "total_expenses": total["sum"],
                }
            )
    expenses_by_currency = {
        "start_date": start_date,
        "end_date": end_date,
        "category": category,
        "expenses": expenses,
    }
    if convert_to:
        to_currency = convert_to
        try:
            sum_in_other_currency = 0
            for exp in expenses:
                from_currency = exp.get("currency")
                amount = exp.get("total_expenses")
                if amount:
                    convert_result = currency_converter(from_currency, to_currency, amount)
                else:
                    convert_result = 0
                sum_in_other_currency += convert_result
            expenses_by_currency[f"sum in {to_currency}"] = round(sum_in_other_currency, 2)
        except BadResponseFromCurrencyAPI:
            expenses_by_currency[f"sum in {to_currency}"] = "conversion is not available now"

    return expenses_by_currency
