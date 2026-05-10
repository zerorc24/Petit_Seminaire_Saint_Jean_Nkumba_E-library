from django.db import migrations
from django.contrib.auth import get_user_model


def create_admin(apps, schema_editor):
    User = get_user_model()

    if not User.objects.filter(username="adminllmm").exists():
        user = User.objects.create_user(
            username="adminllmm",
            email="leomugisha84@gmail.com",
            password="Codex100magni"
        )
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save()


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_admin),
    ]