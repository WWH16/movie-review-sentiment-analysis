from django.urls import path
from . import views

urlpatterns = [
    path('main/', views.main, name='main'),
    path('', views.movies, name='movies'),
    path('browse/', views.browse_movies, name='browse_movies'),
    path('api/movies/', views.movie_list, name='movie_list'),
]
