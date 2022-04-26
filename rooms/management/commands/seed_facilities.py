from django.core.management.base import BaseCommand
from rooms.models import Facility


class Command(BaseCommand):
    help = "This command creates facilities"

    # def add_arguments(self, parser):
    #     parser.add_argument("poll_ids", nargs="+", type=int)

    def handle(self, *args, **options):

        facilities = [
            "Step-free guest entrance",
            "Guest entrance wider than 32 inches",
            "Accessible parking spot",
            "Step-free path to the guest entrance",
            "Step-free bedroom access",
            "Bedroom entrance wider than 32 inches",
            "Step-free bathroom access",
            "Bathroom entrance wider than 32 inches",
            "Shower grab bar",
            "Toilet grab bar",
            "Step-free shower",
            "Adaptive equipment",
        ]

        for facility in facilities:
            Facility.objects.create(name=facility)
        self.stdout.write(self.style.SUCCESS("Facilites Created!"))
