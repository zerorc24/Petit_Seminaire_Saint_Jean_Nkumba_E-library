from django.db import models

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

    # External PDF (Google Drive, etc.)
    pdf_url = models.URLField(blank=True)

    # Optional cover
    cover_image = models.URLField(blank=True)

    def __str__(self):
        return f"{self.title} ({self.level})"