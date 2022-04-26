from django.core.management.base import BaseCommand
from rooms.models import RoomType


class Command(BaseCommand):
    help = "This command creates Room Types"

    # def add_arguments(self, parser):
    #     parser.add_argument("poll_ids", nargs="+", type=int)

    def handle(self, *args, **options):
        roomtypes = [
            "House",
            "Apartment",
            "Bed and breakfast",
            "Boutique hotel",
            "Bungalow",
            "Cabin",
            "Chalet",
            "Condominium",
            "Cottage",
            "Guest suite",
            "Guesthouse",
            "Hostel",
            "Hotel",
            "Loft",
            "Serviced apartment",
            "Townhouse",
            "Villa",
            "Barn",
            "Boat",
            "Camper/RV",
            "Campsite",
            "Casa particular (Cuba)",
            "Castle",
            "Dome house",
            "Earth house",
            "Houseboat",
            "Minsu (Taiwan)",
            "Nature lodge",
            "Tiny house",
        ]

        for roomtype in roomtypes:
            RoomType.objects.create(name=roomtype)
        self.stdout.write(self.style.SUCCESS("Room Types Created!"))
