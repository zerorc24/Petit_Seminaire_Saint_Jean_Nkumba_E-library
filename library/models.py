from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


# =========================================================
# 👤 CUSTOM USER MODEL (CLEAN + PROPER STATUS SYSTEM)
# =========================================================
class CustomUser(AbstractUser):

    email = models.EmailField(unique=True)

    is_verified = models.BooleanField(default=False)

    # ✔ USER STATUS SYSTEM (REPLACES is_approved)
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="pending"
    )

    # OTP (still useful for login verification)
    otp_code = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)

    REQUIRED_FIELDS = ["email"]

    def __str__(self):
        return self.username


# =========================================================
# 📚 BOOK MODEL
# =========================================================
class Book(models.Model):

    LEVEL_CHOICES = [
        ("S1", "S1"),
        ("S2", "S2"),
        ("S3", "S3"),
        ("S4", "S4"),
        ("S5", "S5"),
        ("S6", "S6"),
    ]

    title = models.CharField(max_length=255)
    subject = models.CharField(max_length=100)
    level = models.CharField(max_length=2, choices=LEVEL_CHOICES)

    pdf_url = models.URLField(blank=True, null=True)
    cover_image = models.URLField(blank=True, null=True)

    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.title} ({self.level})"