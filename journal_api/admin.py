from django.contrib import admin

from journal_api.models import Category, Currency, Expense, Limit, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "is_staff")
    ordering = ("email",)
    search_fields = ("username", "email")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "owner"]
    ordering = ["name"]
    search_fields = ["name"]


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ["category", "amount", "owner", "created_at"]
    ordering = ["category", "amount", "created_at"]
    search_fields = ["category", "owner"]


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ["code", "name"]
    ordering = ["code"]
    search_fields = ["code", "name"]


@admin.register(Limit)
class LimitAdmin(admin.ModelAdmin):
    list_display = [
        "owner",
        "type",
        "amount",
        "currency",
        "custom_start_date",
        "custom_end_date",
    ]
    ordering = ["owner"]
    search_fields = ["owner"]
