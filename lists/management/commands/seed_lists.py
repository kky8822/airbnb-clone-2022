import random
from django.core.management.base import BaseCommand
from django.contrib.admin.utils import flatten
from django_seed import Seed
from lists import models as lists_models
from users import models as users_models
from rooms import models as rooms_models

NAME = "lists"


class Command(BaseCommand):
    help = f"This command creates {NAME}"

    def add_arguments(self, parser):
        parser.add_argument(
            "--number",
            default=1,
            type=int,
            help=f"How many {NAME} do you want to create",
        )

    def handle(self, *args, **options):
        number = options.get("number")
        seeder = Seed.seeder()
        users = users_models.User.objects.all()
        rooms = rooms_models.Room.objects.all()

        seeder.add_entity(
            lists_models.List,
            number,
            {
                "user": lambda x: random.choice(users),
            },
        )
        created = seeder.execute()
        cleaned = flatten(list(created.values()))
        for pk in cleaned:
            tg = lists_models.List.objects.get(pk=pk)
            to_add = rooms[random.randint(0, 10) : random.randint(20, 50)]
            tg.rooms.add(*to_add)

        self.stdout.write(self.style.SUCCESS(f"{number} {NAME} Created!"))
