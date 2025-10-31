# reviews/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.main, name='main'),  # Default route for the app
    path('movies/', views.movies, name='movies'),  # Route to submit a review
]
