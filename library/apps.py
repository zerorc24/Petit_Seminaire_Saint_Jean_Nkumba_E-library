from django.apps import AppConfig


class LibraryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'library'

    def ready(self):
        # ⚠️ Safe auto-admin creator (runs only on startup)
        from django.contrib.auth import get_user_model

        User = get_user_model()

        # Create default admin if none exists
        if not User.objects.filter(is_superuser=True).exists():
            user = User.objects.create_user(
                username="admin",
                email="admin@example.com",
                password="admin12345"
            )
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True

            # if your system uses approval
            if hasattr(user, "is_approved"):
                user.is_approved = True

            user.save()