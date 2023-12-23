from django.core.management import BaseCommand
from payments.models import Item
class Command(BaseCommand):
    def handle(self, *args, **options):
        for i in range(1):
            Item.objects.create(
                name=f"T-shirt{i}",
                description=f"beautiful t-shirt{i}",
                price=7
            )