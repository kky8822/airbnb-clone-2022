import os
import random
from django.core.management.base import BaseCommand
from django.contrib.admin.utils import flatten
from django_seed import Seed
from rooms import models as rooms_models
from users import models as users_models
from config import settings


class Command(BaseCommand):
    help = "This command creates Room"

    def add_arguments(self, parser):
        parser.add_argument(
            "--number", default=1, type=int, help="How many rooms do you want to create"
        )

    def handle(self, *args, **options):
        number = options.get("number")
        seeder = Seed.seeder()
        all_users = users_models.User.objects.all()
        room_types = rooms_models.RoomType.objects.all()
        seeder.add_entity(
            rooms_models.Room,
            number,
            {
                "name": lambda x: seeder.faker.address(),
                "host": lambda x: random.choice(all_users),
                "room_type": lambda x: random.choice(room_types),
                "price": lambda x: random.randint(100, 5000),
                "guests": lambda x: random.randint(1, 5),
                "beds": lambda x: random.randint(1, 5),
                "bedrooms": lambda x: random.randint(1, 5),
                "baths": lambda x: random.randint(1, 5),
            },
        )
        created_rooms = seeder.execute()
        created_clean = flatten(list(created_rooms.values()))
        amenities = rooms_models.Amenity.objects.all()
        facilities = rooms_models.Facility.objects.all()
        house_rules = rooms_models.HouseRule.objects.all()

        for pk in created_clean:
            room = rooms_models.Room.objects.get(pk=pk)
            for i in range(3, random.randint(10, 17)):
                photoname = random.choice(
                    os.listdir(os.path.join(settings.MEDIA_ROOT, "room_photos"))
                )
                rooms_models.Photo.objects.create(
                    caption=seeder.faker.sentence(),
                    room=room,
                    file=f"room_photos/{photoname}",
                )
            for i in range(random.randint(3, len(amenities))):
                room.amenities.add(amenities[random.randint(0, len(amenities) - 1)])
            for i in range(random.randint(3, len(facilities))):
                room.facilities.add(facilities[random.randint(0, len(facilities) - 1)])
            for i in range(random.randint(0, len(house_rules))):
                room.house_rules.add(
                    house_rules[random.randint(0, len(house_rules) - 1)]
                )

        self.stdout.write(self.style.SUCCESS(f"{number} rooms Created!"))
