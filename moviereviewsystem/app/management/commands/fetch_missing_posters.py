import requests
import threading
from concurrent.futures import ThreadPoolExecutor
from django.core.management.base import BaseCommand
from app.models import Movie  # ✅ correct import for your app
from time import sleep

# TMDB API base URL
TMDB_API_KEY = "7b995d3c6fd91a2284b4ad8cb390c7b8"  # 🔒 replace with your actual key
TMDB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"

# Threading lock to avoid console output overlap
lock = threading.Lock()


def fetch_movie_data(movie):
    """Fetch and update poster/backdrop URLs for a single movie."""
    params = {
        "api_key": TMDB_API_KEY,
        "query": movie.title,
        "year": movie.release_year,
    }

    try:
        response = requests.get(TMDB_SEARCH_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if not data.get("results"):
            with lock:
                print(f"⚠️ No results found for: {movie.title}")
            return False

        result = data["results"][0]
        poster_path = result.get("poster_path")
        backdrop_path = result.get("backdrop_path")

        if poster_path:
            movie.poster_url = f"{TMDB_IMAGE_BASE}{poster_path}"
        if backdrop_path:
            movie.backdrop_url = f"{TMDB_IMAGE_BASE}{backdrop_path}"

        movie.save(update_fields=["poster_url", "backdrop_url"])

        with lock:
            print(f"✅ Updated: {movie.title}")
        return True

    except Exception as e:
        with lock:
            print(f"❌ Error fetching {movie.title}: {e}")
        return False


class Command(BaseCommand):
    help = "Fetch missing posters and backdrops from TMDB API for movies missing URLs."

    def add_arguments(self, parser):
        parser.add_argument(
            "--threads", type=int, default=5,
            help="Number of threads to use (default: 5)"
        )
        parser.add_argument(
            "--batch-size", type=int, default=50,
            help="Number of movies to process per batch (default: 50)"
        )
        parser.add_argument(
            "--dry-run", action="store_true",
            help="Simulate fetch without saving changes"
        )

    def handle(self, *args, **options):
        threads = options["threads"]
        batch_size = options["batch_size"]
        dry_run = options["dry_run"]

        missing_movies = Movie.objects.filter(
            poster_url__isnull=True
        ) | Movie.objects.filter(poster_url="")

        total_missing = missing_movies.count()
        self.stdout.write(f"🎬 Found {total_missing} movies missing posters/backdrops")

        if total_missing == 0:
            self.stdout.write("✅ All movies already have posters.")
            return

        movies = list(missing_movies)
        total_batches = (total_missing + batch_size - 1) // batch_size

        for batch_idx in range(total_batches):
            batch = movies[batch_idx * batch_size:(batch_idx + 1) * batch_size]
            self.stdout.write(f"🚀 Processing batch {batch_idx + 1}/{total_batches} ({len(batch)} movies)")

            if dry_run:
                for movie in batch:
                    print(f"🧩 Would fetch: {movie.title} ({movie.release_year})")
                continue

            with ThreadPoolExecutor(max_workers=threads) as executor:
                results = list(executor.map(fetch_movie_data, batch))

            successful = sum(results)
            self.stdout.write(f"✅ Batch {batch_idx + 1} complete: {successful}/{len(batch)} updated")

            # Pause between batches to avoid TMDB rate limit
            sleep(2)

        self.stdout.write("🎉 Done fetching all missing movie posters and backdrops.")
