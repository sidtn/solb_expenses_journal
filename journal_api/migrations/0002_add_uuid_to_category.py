# Generated by Django 4.0.5 on 2022-06-22 18:49

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('journal_api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name="category",
            name="uuid",
            field=models.UUIDField(editable=False, null=True),
        ),
    ]
