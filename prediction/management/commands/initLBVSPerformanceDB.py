from django.core.management.base import BaseCommand
from prediction.db.LBVSPerformanceData import initLBVSPerformanceDB


class Command(BaseCommand):
    help = 'init data in LBVSPerformanceTable'

    def handle(self, *args, **options):
        initLBVSPerformanceDB()
        self.stdout.write(self.style.SUCCESS('Successfully init data in LBVSPerformanceTable'))
