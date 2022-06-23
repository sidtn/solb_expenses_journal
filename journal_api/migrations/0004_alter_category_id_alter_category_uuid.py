# Generated by Django 4.0.5 on 2022-06-23 18:19

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('journal_api', '0003_alter_expense_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='id_backup',
            field=models.IntegerField(null=True),
        ),
        migrations.RunSQL("UPDATE journal_api_category SET id_backup = id"),
        migrations.RemoveField(
            model_name='category',
            name='id'
        ),
        migrations.AlterField(
            model_name='category',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
        migrations.RenameField(
            model_name='category',
            old_name='id_backup',
            new_name='id'
        )
    ]
