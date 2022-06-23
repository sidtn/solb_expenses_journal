# Generated by Django 4.0.5 on 2022-06-23 12:11

from django.db import migrations, models, transaction
import uuid


def create_uuid(apps, schema_editor):
    Category = apps.get_model("journal_api", "Category")
    objs = [obj for obj in Category.objects.filter(uuid=None)]
    with transaction.atomic():
        for obj in objs:
            obj.uuid = uuid.uuid4()
        Category.objects.bulk_update(objs, ["uuid"])


class Migration(migrations.Migration):

    dependencies = [
        ('journal_api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='uuid',
            field=models.UUIDField(editable=False, null=True),
        ),
        migrations.RunPython(create_uuid, reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
            model_name='category',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
        )
    ]