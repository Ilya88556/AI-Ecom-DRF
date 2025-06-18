from django.core.management.base import BaseCommand

from delivery.tasks import sync_novaposhta_areas


class Command(BaseCommand):
    help = "Run synchronization areas Nova Poshta"

    def handle(self, *args, **options):
        sync_novaposhta_areas.delay()
        self.stdout.write("Task sync_novaposhta_areas started")
