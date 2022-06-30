from django.core.management import BaseCommand
from django.db.models import Count, Max

from journal_api.core.lock_tables import lock_table
from journal_api.models import Category


class Command(BaseCommand):
    def handle(self, **options):
        duplicates_id = Category.objects.values('id').annotate(Count('id')) .order_by("id").filter(id__count__gt=1)
        count = 1
        for data in duplicates_id:
            duplicates = Category.objects.filter(id=data["id"])[:data["id__count"] - 1]
            count += 1
            for cat in duplicates:
                with lock_table(Category):
                    last_id = Category.objects.all().aggregate(
                        largest=Max("id")
                    )["largest"]
                    cat.id = last_id + 1
                    cat.save()
            print(f"{count} from {len(duplicates_id)} has been updated")
