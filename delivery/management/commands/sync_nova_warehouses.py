from django.core.management.base import BaseCommand

from delivery.tasks import sync_novaposhta_addresses


class Command(BaseCommand):
    help = "Run synchronization warehouses Nova Poshta"

    def handle(self, *args, **options):
        sync_novaposhta_addresses.delay()
        self.stdout.write("Task sync_novaposhta_warehouses started")
