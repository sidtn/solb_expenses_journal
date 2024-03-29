# Generated by Django 4.0.5 on 2022-06-24 17:34

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('journal_api', '0004_alter_expense_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='id',
            field=models.IntegerField(editable=False),
        ),
        migrations.AlterField(
            model_name='category',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
    ]
