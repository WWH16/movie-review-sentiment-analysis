from django.urls import path
from . import views

urlpatterns = [
    # Homepage
    path('', views.main, name='main'),

    # Movies browser page
    path('movies/', views.movies, name='movies'),

    # API endpoints
    path('api/movies/search/', views.movie_search_api, name='movie_search_api'),
    path('api/movies/', views.movie_list, name='movie_list'),

    # Add your other URLs here (review page, etc.)
    # path('review/<int:movie_id>/', views.review, name='review'),
]