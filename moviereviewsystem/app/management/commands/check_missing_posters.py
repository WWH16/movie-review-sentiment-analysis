from django.core.management.base import BaseCommand
from app.models import Movie   # ✅ import your model from the app


class Command(BaseCommand):
    help = 'Check ONLY movies with null poster_url'

    def handle(self, *args, **options):
        # Only count null poster_url movies
        null_movies = Movie.objects.filter(poster_url__isnull=True)
        null_count = null_movies.count()
        total_movies = Movie.objects.count()

        self.stdout.write("=" * 60)
        self.stdout.write("MISSING POSTERS REPORT")
        self.stdout.write("=" * 60)
        self.stdout.write(f"Total movies in database: {total_movies}")
        self.stdout.write(f"Movies WITH poster_url: {total_movies - null_count}")
        self.stdout.write(f"Movies WITH NULL poster_url: {null_count}")

        if null_count > 0:
            percentage = (null_count / total_movies) * 100
            self.stdout.write(f"Percentage without posters: {percentage:.1f}%")

            self.stdout.write("\nFirst 10 movies needing posters:")
            self.stdout.write("-" * 60)

            sample_movies = null_movies[:10]
            for i, movie in enumerate(sample_movies, 1):
                self.stdout.write(
                    f"{i:2d}. ID: {movie.id:6} | {movie.title:<40} | {movie.release_year or 'No year'}"
                )
        else:
            self.stdout.write(self.style.SUCCESS("🎉 All movies have poster URLs!"))

        self.stdout.write("=" * 60)
