from rest_framework import serializers

from journal_api.models import Category, Expense, User


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

    class Meta:
        model = Category
        fields = ("uuid", "id", "name", "owner")


class ExpenseSerializer(serializers.ModelSerializer):

    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Expense
        fields = (
            "id",
            "amount",
            "created_at",
            "category",
            "short_description",
            "owner",
        )
