import os

from django.core.management.base import BaseCommand

from apps.core.models.base_user import BaseUser


class Command(BaseCommand):
    help = 'Create initial admin and staff users from environment variables'

    def handle(self, *args, **options):
        self._create_user(
            email=os.environ.get('ADMIN_EMAIL', 'admin@rebank.com'),
            password=os.environ.get('ADMIN_PASSWORD', 'admin1234'),
            is_superuser=True,
            is_staff=True,
            label='Admin',
        )
        self._create_user(
            email=os.environ.get('STAFF_EMAIL', 'staff@rebank.com'),
            password=os.environ.get('STAFF_PASSWORD', 'staff1234'),
            is_superuser=False,
            is_staff=True,
            label='Staff',
        )

    def _create_user(self, email, password, is_superuser, is_staff, label):
        if BaseUser.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING(f'{label} "{email}" already exists — skipped.'))
            return

        user = BaseUser.objects.create_superuser(email=email, password=password) if is_superuser else BaseUser.objects._create_user(
            email=email,
            password=password,
            is_staff=True,
            is_active=True,
            is_superuser=False,
        )
        self.stdout.write(self.style.SUCCESS(f'{label} "{email}" created successfully.'))
