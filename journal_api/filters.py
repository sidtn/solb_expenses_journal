from django_filters import rest_framework as filters

from journal_api.models import Category, Currency, Expense


class CategoryFilter(filters.FilterSet):
    name = filters.CharFilter(field_name="name", lookup_expr="icontains")

    class Meta:
        model = Category
        fields = ["name"]


class ExpenseFilter(filters.FilterSet):
    currency = filters.CharFilter(
        field_name="currency__code", lookup_expr="iexact"
    )
    amount_gt = filters.NumberFilter(field_name="amount", lookup_expr="gt")

    class Meta:
        models = Expense
        fields = ["currency", "amount"]
