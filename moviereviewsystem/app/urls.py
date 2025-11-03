from django.urls import path
from . import views

urlpatterns = [
    path('', views.movies, name='movies'),
    path('main/', views.main, name='main'),
    path('api/movies/', views.movie_list, name='movie_list'),
]