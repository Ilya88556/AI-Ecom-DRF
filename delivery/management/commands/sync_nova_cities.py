from django.core.management.base import BaseCommand

from delivery.tasks import sync_novaposhta_cities


class Command(BaseCommand):
    help = "Run synchronization cities Nova Poshta"

    def handle(self, *args, **options):
        sync_novaposhta_cities.delay()
        self.stdout.write("Task sync_novaposhta_cities started")
