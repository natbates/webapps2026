from django.apps import AppConfig


class RegisterConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'register'
    verbose_name = 'Register'

    def ready(self):
        from django.db.models.signals import post_migrate
        from register.admin_setup import ensure_default_admin

        def create_default_admin(sender, **kwargs):
            ensure_default_admin()

        post_migrate.connect(create_default_admin, sender=self)
