from rest_framework import serializers
from rest_framework_recursive.fields import RecursiveField

from journal_api.models import Category, Currency, Expense, User


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
    convertto = serializers.PrimaryKeyRelatedField(
        required=False, queryset=Currency.objects.all()
    )
