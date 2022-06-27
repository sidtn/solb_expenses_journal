import datetime

from django.db.models import Sum

from journal_api.models import Expense


def get_total_expenses(request):

    """
    :param request:
    :return: total expenses by time and by category.
    Returns the result for the user's currencies, if it is not explicitly specified in the query parameters.
    """

    user = request.user
    category = request.query_params.get("category")
    start_date = request.query_params.get("start_date")
    end_date = request.query_params.get("end_date")
    currency = request.query_params.get("currency")
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
        return {
            "start_date": start_date,
            "end_date": end_date,
            "currency": currency,
            "total_expenses": total_expenses["sum"],
        }
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
        expenses.append(
            {
                "currency": currency["currency"],
                "total_expenses": total["sum"],
            }
        )
    expenses_by_currency = {
        "start_date": start_date,
        "end_date": end_date,
        "expenses": expenses,
    }

    return expenses_by_currency
