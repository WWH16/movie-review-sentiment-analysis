from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from .models import Movie
import os
import joblib
import pandas as pd
import json
import re
import string
import nltk
from nltk.corpus import stopwords

# Ensure NLTK stopwords are available
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

STOP_WORDS = set(stopwords.words("english"))


def clean_text_manual(text):
    """
    Manual text cleaning function to show preprocessing
    """
    if not text:
        return ""

    # Apply cleaning steps
    text = re.sub("<.*?>", "", text)  # remove HTML tags
    text = re.sub("[%s]" % re.escape(string.punctuation), "", text)  # remove punctuation
    text = re.sub("\d+", "", text)  # remove numbers
    text = text.lower()  # lowercase

    # Remove stopwords
    text = " ".join([word for word in text.split() if word not in STOP_WORDS])
    return text


# Load the model once when the server starts
MODEL_PATH = os.path.join(settings.BASE_DIR, 'model', 'sentiment_classification_pipeline_new.pkl')

try:
    sentiment_pipeline = joblib.load(MODEL_PATH)
    MODEL_LOADED = True
    print("✅ Sentiment model loaded successfully!")
except Exception as e:
    sentiment_pipeline = None
    MODEL_LOADED = False
    print(f"❌ Error loading sentiment model: {e}")


@csrf_exempt
@require_http_methods(["POST"])
def analyze_sentiment(request):
    """
    API endpoint to analyze sentiment of a movie review
    """
    if not MODEL_LOADED:
        return JsonResponse({
            'error': 'Sentiment model not available',
            'sentiment': 'unknown',
            'confidence': 0
        }, status=503)

    try:
        # Parse JSON data
        data = json.loads(request.body)
        review_text = data.get('review', '').strip()

        if not review_text:
            return JsonResponse({
                'error': 'No review text provided',
                'sentiment': 'unknown',
                'confidence': 0
            }, status=400)

        # Clean the text manually (to show in results)
        cleaned_text = clean_text_manual(review_text)

        # Create a pandas Series for the input (as expected by your pipeline)
        review_series = pd.Series([review_text])

        # Get prediction (0 = negative, 1 = positive)
        prediction = sentiment_pipeline.predict(review_series)[0]

        # Get prediction probabilities for confidence score
        probabilities = sentiment_pipeline.predict_proba(review_series)[0]
        confidence = max(probabilities) * 100  # Convert to percentage

        # Convert to sentiment labels
        sentiment = 'positive' if prediction == 1 else 'negative'

        return JsonResponse({
            'sentiment': sentiment,
            'confidence': round(confidence, 2),
            'prediction': int(prediction),
            'cleaned_text': cleaned_text,  # Send cleaned text to frontend
            'original_text': review_text,  # Send original text too
            'probabilities': {
                'negative': round(probabilities[0] * 100, 2),
                'positive': round(probabilities[1] * 100, 2)
            }
        })

    except Exception as e:
        return JsonResponse({
            'error': f'Analysis failed: {str(e)}',
            'sentiment': 'unknown',
            'confidence': 0
        }, status=500)


def main(request):
    """Homepage with sentiment analysis"""
    return render(request, 'main.html')


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


def movie_detail(request, movie_id):
    """Movie detail view"""
    movie = get_object_or_404(Movie, id=movie_id)

    context = {
        'movie': movie,
    }

    return render(request, 'review.html', context)


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