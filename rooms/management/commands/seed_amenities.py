from django.core.management.base import BaseCommand
from rooms.models import Amenity


class Command(BaseCommand):
    help = "This command creates amenities"

    # def add_arguments(self, parser):
    #     parser.add_argument("poll_ids", nargs="+", type=int)

    def handle(self, *args, **options):
        amenities = [
            "Wifi",
            "Kitchen",
            "Self check-in",
            "Pool",
            "Hot tub",
            "Washer",
            "Dryer",
            "Air conditioning",
            "Heating",
            "Dedicated workspace",
            "Indoor fireplace",
            "Gym",
            "Breakfast",
            "Free parking",
            "EV charger",
            "Hair dryer",
            "Iron",
            "High chair",
            "Beachfront",
            "Waterfront",
            "Smoke alarm",
            "Carbon monoxide alarm",
        ]
        for a in amenities:
            Amenity.objects.create(name=a)
        self.stdout.write(self.style.SUCCESS("Amenities Created!"))
