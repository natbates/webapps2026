from django.core.management.base import BaseCommand

from register.admin_setup import ensure_default_admin


class Command(BaseCommand):
    help = 'Ensure the default admin account exists with username admin and password password123.'

    def handle(self, *args, **options):
        admin = ensure_default_admin()
        self.stdout.write(self.style.SUCCESS(f'Default admin ensured: {admin.username}'))
