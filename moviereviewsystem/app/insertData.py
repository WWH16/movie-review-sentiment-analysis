import os
import django
import csv
from pathlib import Path

# --- Set up Django environment ---
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moviereviewsystem.settings')
django.setup()

# --- Import model only after Django is ready ---
from .models import Movie
from django.conf import settings


def run():
    csv_path = Path(settings.BASE_DIR) / 'netflix_titles.csv'  # Make sure 'movies.csv' is at BASE_DIR
    if not csv_path.exists():
        print(f"❌ CSV file not found at: {csv_path}")
        return

    with open(csv_path, encoding='utf-8') as file:
        reader = csv.DictReader(file)
        count = 0
        for row in reader:
            Movie.objects.get_or_create(
                show_id=row['show_id'],
                defaults={
                    'type': row['type'],
                    'title': row['title'],
                    'director': row.get('director') or None,
                    'cast': row.get('cast') or None,
                    'country': row.get('country') or None,
                    'date_added': row.get('date_added') or None,
                    'release_year': int(row['release_year']) if row['release_year'] else None,
                    'rating': row.get('rating') or None,
                    'duration': row.get('duration') or None,
                    'listed_in': row.get('listed_in') or None,
                    'description': row.get('description') or None,
                }
            )
            count += 1
        print(f"✅ Successfully imported {count} movie records!")


if __name__ == "__main__":
    run()
