from django.shortcuts import render
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import Movie


# Homepage
def main(request):
    return render(request, 'main.html')
def movies(request):
    return render(request, 'movies.html')


# Simple movie listing (API endpoint)
def movie_list(request):
    movies = Movie.objects.all().values(
        'id', 'title', 'release_year', 'type', 'rating', 'listed_in', 'description'
    )
    return JsonResponse(list(movies), safe=False)


# Paginated and searchable movie browser (for frontend)
def browse_movies(request):
    search_query = request.GET.get('q', '').strip()

    # Get all movies
    movies = Movie.objects.all()

    # Optional search filter
    if search_query:
        movies = movies.filter(title__icontains=search_query)

    # Order by release year (newest first) and then by title
    movies = movies.order_by('-release_year', 'title')

    # Pagination (24 movies per page for better grid layout)
    paginator = Paginator(movies, 24)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }

    return render(request, 'movies.html', context)
