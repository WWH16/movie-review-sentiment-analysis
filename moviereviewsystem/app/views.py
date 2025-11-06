from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.db.models import Q
from .models import Movie


def movies(request):
    """Movies browser page with filtering and pagination"""
    type_filter = request.GET.get('type', '').strip().lower()

    # Get all movies
    movies_list = Movie.objects.all()

    # Apply type filter
    if type_filter and type_filter != 'all':
        type_mapping = {'movie': 'Movie', 'tv': 'TV Show'}
        db_type = type_mapping.get(type_filter)
        if db_type:
            movies_list = movies_list.filter(type=db_type)

    # Order by release year (newest first) then title
    movies_list = movies_list.order_by('-release_year', 'title')

    # Pagination with error handling
    paginator = Paginator(movies_list, 24)
    page_number = request.GET.get('page', 1)

    try:
        page_obj = paginator.page(page_number)
    except (EmptyPage, PageNotAnInteger):
        page_obj = paginator.page(1)

    context = {
        'page_obj': page_obj,
        'type_filter': type_filter if type_filter else 'all',
        'total_movies': paginator.count,
    }

    return render(request, 'movies.html', context)


def movie_search_api(request):
    """API endpoint for movie title search"""
    query = request.GET.get('q', '').strip()

    # Validate limit parameter
    try:
        limit = min(int(request.GET.get('limit', 8)), 50)  # Max 50
    except (ValueError, TypeError):
        limit = 8

    # Require minimum 2 characters
    if not query or len(query) < 2:
        return JsonResponse([], safe=False)

    try:
        # Search by title only
        movies = Movie.objects.filter(
            title__icontains=query
        ).order_by('-release_year', 'title')[:limit]

        # Build results
        results = [{
            'id': m.id,
            'title': m.title,
            'release_year': m.release_year,
            'type': m.type,
            'rating': m.rating,
            'poster_url': m.poster_url,
        } for m in movies]

        return JsonResponse(results, safe=False)

    except Exception as e:
        return JsonResponse({'error': 'Search failed'}, status=500)


def main(request):
    """Homepage"""
    return render(request, 'main.html')


def movie_list(request):
    """API endpoint for all movies"""
    try:
        movies = Movie.objects.all().values(
            'id', 'title', 'release_year', 'type', 'rating',
            'listed_in', 'description', 'poster_url', 'backdrop_url'
        )
        return JsonResponse(list(movies), safe=False)
    except Exception as e:
        return JsonResponse({'error': 'Failed to fetch movies'}, status=500)