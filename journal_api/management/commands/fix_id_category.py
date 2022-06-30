from django.core.management import BaseCommand
from django.db.models import Count, Max

from journal_api.core.utils import lock_table
from journal_api.models import Category


class Command(BaseCommand):
    def handle(self, **options):
        list_duplicated_objects = []
        duplicates_id = Category.objects.values('id').annotate(Count('id')) .order_by("id").filter(id__count__gt=1)
        for data in duplicates_id:
            duplicates = Category.objects.filter(id=data["id"])[:data["id__count"] - 1]
            for cat in duplicates:
                list_duplicated_objects.append(cat)
        with lock_table(Category):
            last_id = Category.objects.all().aggregate(
                largest=Max("id")
            )["largest"]
            for id_index, obj in enumerate(list_duplicated_objects, start=1):
                obj.id = last_id + id_index
            Category.objects.bulk_update(list_duplicated_objects, ["id"])

