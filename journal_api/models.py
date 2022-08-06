import datetime
import uuid as uuid
from decimal import Decimal

from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext as _
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel

from journal_api.core.utils import lock_table
from journal_api.core.validators import validate_positive


class User(AbstractUser):
    email = models.EmailField(_("email address"), blank=False, unique=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email


class Currency(models.Model):
    code = models.CharField(primary_key=True, max_length=3, unique=True)
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.code

    class Meta:
        verbose_name_plural = "Currencies"


class Category(MPTTModel):
    uuid = models.UUIDField(
        max_length=36, default=uuid.uuid4, primary_key=True, editable=False
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="categories",
    )
    name = models.CharField(max_length=100, verbose_name="Expense category")
    parent = TreeForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
    )
    id = models.IntegerField(editable=False)

    def save(self, *args, **kwargs):
        if self._state.adding:
            with lock_table(Category):
                last_id = Category.objects.all().aggregate(
                    largest=models.Max("id")
                )["largest"]
                if last_id is not None:
                    self.id = last_id + 1
                else:
                    self.id = 1

                super(Category, self).save(*args, **kwargs)
        else:
            super(Category, self).save(*args, **kwargs)

    class Meta:
        unique_together = ("owner", "name")
        verbose_name_plural = "Categories"

    class MPTTMeta:
        order_insertion_by = ["name"]

    def __str__(self):
        return self.name


class Expense(models.Model):
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="expenses"
    )
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[validate_positive]
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
    )
    currency = models.ForeignKey(
        Currency, on_delete=models.CASCADE, default="USD"
    )
    short_description = models.CharField(
        max_length=255, verbose_name="Short description", blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.owner} - {self.amount} - {self.category}"


class Limit(models.Model):
    class LimitType(models.TextChoices):
        WEEK = "W", _("Week")
        MONTH = "M", _("Month")
        CUSTOM = "C", _("Custom")

    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="limits"
    )
    type = models.CharField(
        max_length=50, choices=LimitType.choices, default=LimitType.MONTH
    )
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[validate_positive]
    )
    currency = models.ForeignKey(
        Currency, on_delete=models.CASCADE, default="USD"
    )
    custom_start_date = models.DateField(default=datetime.date.today)
    custom_end_date = models.DateField(default=datetime.date.today)
    notification_percent = models.DecimalField(
        max_digits=3,
        decimal_places=0,
        default=Decimal(80),
        validators=[MinValueValidator(50), MaxValueValidator(100)],
    )

    def __str__(self):
        return f"{self.owner} {self.type} limit"

    class Meta:
        unique_together = ("owner", "type")


class NotificationOfExceeding(models.Model):
    limit = models.ForeignKey(Limit, on_delete=models.CASCADE)
    exceeding = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    is_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.limit} - {self.exceeding} notification"

    class Meta:
        unique_together = ["limit", "exceeding"]
