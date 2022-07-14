import datetime

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_recursive.fields import RecursiveField

from journal_api.models import Category, Currency, Expense, Limit, User


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )
        return user

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "password",
        )


class CategorySerializer(serializers.ModelSerializer):

    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    id = serializers.IntegerField(read_only=True)
    children = RecursiveField(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ("id", "uuid", "name", "owner", "parent", "children")


class ExpenseSerializer(serializers.ModelSerializer):

    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Expense
        fields = (
            "id",
            "amount",
            "currency",
            "created_at",
            "category",
            "short_description",
            "owner",
        )


class TotalExpensesSerializer(serializers.Serializer):
    category = serializers.PrimaryKeyRelatedField(
        required=False, queryset=Category.objects.all()
    )
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    currency = serializers.PrimaryKeyRelatedField(
        required=False, queryset=Currency.objects.all()
    )


class LimitSerializer(serializers.ModelSerializer):

    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Limit
        fields = "__all__"

    def validate(self, attrs):
        if attrs.get("custom_start_date") and attrs.get("custom_end_date"):
            if attrs.get("custom_start_date") > attrs.get("custom_end_date"):
                raise ValidationError(
                    detail={
                        "date_error": "the start date of the period cannot be later than the end date"
                    }
                )
            if attrs.get("custom_end_date") < datetime.date.today():
                raise ValidationError(
                    detail={"date_error": "the end date cannot be in the past"}
                )
        return attrs
