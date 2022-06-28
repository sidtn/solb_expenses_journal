# Generated by Django 4.0.5 on 2022-06-27 13:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "journal_api",
            "0008_remove_expense_category_old_alter_expense_category",
        ),
    ]

    operations = [
        migrations.CreateModel(
            name="Currency",
            fields=[
                (
                    "code",
                    models.CharField(
                        max_length=3,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                ("name", models.CharField(max_length=100, unique=True)),
            ],
        ),
    ]