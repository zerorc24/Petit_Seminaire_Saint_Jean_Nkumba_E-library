import csv
import os
from django.core.management.base import BaseCommand
from library.models import Book

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
CSV_PATH = os.path.join(BASE_DIR, 'library', 'data', 'books.csv')

class Command(BaseCommand):
    help = 'Bulk import books from books.csv'

    def handle(self, *args, **options):
        if not os.path.exists(CSV_PATH):
            self.stdout.write(self.style.ERROR(f'CSV file not found at {CSV_PATH}'))
            return

        created = 0

        with open(CSV_PATH, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                # Skip empty rows
                if not row["title"] or not row["pdf_url"]:
                    continue

                Book.objects.create(
                    title=row["title"].strip(),
                    subject=row["subject"].strip(),
                    level=row["level"].strip(),
                    pdf_url=row["pdf_url"].strip(),
                )
                created += 1

        self.stdout.write(self.style.SUCCESS(f'{created} books imported successfully!'))