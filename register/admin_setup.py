from decimal import Decimal
from django.contrib.auth import get_user_model


def ensure_default_admin():
    """Ensure a default admin account exists with fixed credentials."""
    User = get_user_model()
    defaults = {
        'email': 'admin1@example.com',
        'is_staff': True,
        'is_superuser': True,
        'currency': 'GBP',
        'balance': Decimal('500.00'),
    }

    admin, created = User.objects.get_or_create(username='admin1', defaults=defaults)

    if created:
        admin.set_password('admin1')
        admin.save()
        return admin

    updated = False
    if not admin.check_password('admin1'):
        admin.set_password('admin1')
        updated = True

    for field, value in defaults.items():
        if getattr(admin, field) != value:
            setattr(admin, field, value)
            updated = True

    if updated:
        admin.save()

    return admin
