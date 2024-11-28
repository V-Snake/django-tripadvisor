# C:\Users\Nassim\Documents\django-tripadvisor\tripadvisor\attractions\utils.py

import requests
from django.core.cache import cache
from .models import Attraction, Photo, Review
from django.utils import timezone
import logging
from django.conf import settings  # Importer les settings

logger = logging.getLogger(__name__)

API_KEY = settings.TRIPADVISOR_API_KEY  # Utiliser la clé API depuis settings
BASE_URL = 'https://api.content.tripadvisor.com/api/v1'

def fetch_tripadvisor_data(endpoint, params):
    """
    Helper to fetch data from the TripAdvisor API with caching.
    """
    cache_key = f"{endpoint}:{str(params)}"
    cached_data = cache.get(cache_key)

    if cached_data:
        logger.debug(f"Cache hit for key: {cache_key}")
        return cached_data

    try:
        response = requests.get(endpoint, params=params, timeout=10)  # Timeout de 10 secondes
        response.raise_for_status()  # Lève une exception pour les codes d'erreur HTTP
        data = response.json()
        cache.set(cache_key, data, timeout=3600)  # Cache pour 1 heure
        logger.debug(f"Fetched and cached data for key: {cache_key}")
        return data
    except requests.exceptions.Timeout:
        logger.error(f"Timeout while fetching data from TripAdvisor for key: {cache_key}")
    except requests.exceptions.RequestException as e:
        logger.error(f"RequestException while fetching data from TripAdvisor for key: {cache_key} - {e}")
    return None

def fetch_location_details(location_id):
    url = f"{BASE_URL}/location/{location_id}/details"
    return fetch_tripadvisor_data(url, {'key': API_KEY})

def fetch_location_photos(location_id):
    url = f"{BASE_URL}/location/{location_id}/photos"
    return fetch_tripadvisor_data(url, {'key': API_KEY})

def fetch_location_reviews(location_id):
    url = f"{BASE_URL}/location/{location_id}/reviews"
    return fetch_tripadvisor_data(url, {'key': API_KEY})

def fetch_nearby_attractions(lat, lng, radius, category='attractions'):
    """
    Fetch nearby attractions based on latitude, longitude, radius, and category.
    """
    url = f"{BASE_URL}/location/nearby_search"
    params = {
        'key': API_KEY,
        'latLong': f"{lat},{lng}",
        'radius': radius,
        'categories': category,
        'limit': 10
    }
    logger.debug(f"Fetching nearby attractions with params: {params}")
    return fetch_tripadvisor_data(url, params)
