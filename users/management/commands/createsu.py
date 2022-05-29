from django.core.management.base import BaseCommand
from users.models import User


class Command(BaseCommand):

    help = "This command creates superuser"

    def handle(self, *args, **options):
        admin = User.objects.get_or_none(username="kky8822_admin@gmail.com")
        if not admin:
            User.objects.create_superuser(
                "kky8822_admin@gmail.com", "kky8822_admin@gmail.com", "kky19121143"
            )
            self.stdout.write(self.style.SUCCESS(f"Superuser Created"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Superuser Exists"))
