import requests
import time
from django.core.management.base import BaseCommand
from app.models import Movie
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.db import transaction


class Command(BaseCommand):
    help = 'Fetch movie posters from TMDb API'

    def fetch_movie_poster(self, movie_data):
        movie, api_key, image_base = movie_data
        try:
            endpoint = 'tv' if movie.type == 'TV Show' else 'movie'
            params = {
                'api_key': api_key,
                'query': movie.title,
                'year': movie.release_year
            }

            response = requests.get(f'https://api.themoviedb.org/3/search/{endpoint}', params=params)
            data = response.json()

            if data.get('results'):
                result = data['results'][0]
                poster_path = result.get('poster_path')
                backdrop_path = result.get('backdrop_path')

                updates = {}
                if poster_path:
                    updates['poster_url'] = f'{image_base}{poster_path}'
                if backdrop_path:
                    updates['backdrop_url'] = f'{image_base}{backdrop_path}'

                return movie, updates, None
            else:
                return movie, None, 'Not found'

        except Exception as e:
            return movie, None, str(e)

    def handle(self, *args, **options):
        api_key = '7b995d3c6fd91a2284b4ad8cb390c7b8'
        image_base = 'https://image.tmdb.org/t/p/w500'

        movies = Movie.objects.filter(poster_url__isnull=True)
        total = movies.count()

        self.stdout.write(f'Fetching posters for {total} movies...')

        # Prepare movie data for threading
        movie_data = [(movie, api_key, image_base) for movie in movies]

        successful = 0
        failed = 0
        processed = 0

        # Use ThreadPoolExecutor for concurrent requests
        with ThreadPoolExecutor(max_workers=10) as executor:  # Adjust workers as needed
            future_to_movie = {executor.submit(self.fetch_movie_poster, data): data[0] for data in movie_data}

            for future in as_completed(future_to_movie):
                movie = future_to_movie[future]
                processed += 1

                try:
                    result_movie, updates, error = future.result()

                    if updates:
                        # Bulk update in transaction
                        with transaction.atomic():
                            for field, value in updates.items():
                                setattr(movie, field, value)
                            movie.save()
                        successful += 1
                        self.stdout.write(f'[{processed}/{total}] ✓ {movie.title}')
                    else:
                        failed += 1
                        self.stdout.write(f'[{processed}/{total}] ✗ {movie.title} - {error}')

                except Exception as e:
                    failed += 1
                    self.stdout.write(f'[{processed}/{total}] ERROR: {movie.title} - {str(e)}')

        self.stdout.write(self.style.SUCCESS(
            f'Complete! Successful: {successful}, Failed: {failed}, Total: {total}'
        ))