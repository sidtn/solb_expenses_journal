from django.contrib import admin

from journal_api.models import Category, Expense, User


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


# @admin.register(Expense)
# class ExpenseAdmin(admin.ModelAdmin):
#     list_display = ["category", "amount", "owner", "created_at"]
#     ordering = ["category", "amount", "created_at"]
#     search_fields = ["category", "owner"]
