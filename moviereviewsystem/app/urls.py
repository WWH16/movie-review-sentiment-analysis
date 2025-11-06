from django.urls import path
from . import views

urlpatterns = [
    path('', views.main, name='main'),
    path('movies/', views.movies, name='movies'),
    path('review/<int:movie_id>/', views.movie_detail, name='movie_detail'),
    path('api/movies/', views.movie_list, name='movie_list'),
    path('api/movies/search/', views.movie_search_api, name='movie_search_api'),
    path('api/analyze-sentiment/', views.analyze_sentiment, name='analyze_sentiment'),
]