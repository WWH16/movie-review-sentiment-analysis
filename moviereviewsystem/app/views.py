from django.shortcuts import render
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Q
from .models import Movie

# Homepage
def main(request):
    return render(request, 'main.html')

# Movies browser page
def movies(request):
    search_query = request.GET.get('q', '').strip()

    # Get all movies from database
    movies_list = Movie.objects.all()

    # Optional search filter
    if search_query:
        movies_list = movies_list.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(listed_in__icontains=search_query) |
            Q(director__icontains=search_query) |
            Q(cast__icontains=search_query)
        )

    # Order by release year (newest first) and then by title
    movies_list = movies_list.order_by('-release_year', 'title')

    # Pagination (24 movies per page for better grid layout)
    paginator = Paginator(movies_list, 24)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'total_movies': movies_list.count(),
    }

    return render(request, 'movies.html', context)

# Simple movie listing (API endpoint)
def movie_list(request):
    movies = Movie.objects.all().values(
        'id', 'title', 'release_year', 'type', 'rating', 'listed_in', 'description', 'poster_url', 'backdrop_url'
    )
    return JsonResponse(list(movies), safe=False)