# C:\Users\Nassim\Documents\django-tripadvisor\tripadvisor\attractions\utils.py

import requests
from django.core.cache import cache
from django.conf import settings
from .models import Attraction, Photo, Review
import logging
from datetime import timedelta
from django.utils import timezone
from django.db import transaction
import json

logger = logging.getLogger(__name__)

API_KEY = settings.TRIPADVISOR_API_KEY
BASE_URL = 'https://api.content.tripadvisor.com/api/v1'

def sanitize_cache_key(endpoint, params):
    """
    Sanitize the cache key by replacing problematic characters.
    """
    sanitized_endpoint = endpoint.replace(':', '_').replace('/', '_')
    # Remplacer les guillemets et autres caractères spéciaux
    sanitized_params = json.dumps(params, sort_keys=True).replace('"', '').replace(' ', '')
    return f"{sanitized_endpoint}:{sanitized_params}"

def fetch_tripadvisor_data(endpoint, params):
    """
    Helper to fetch data from the TripAdvisor API with caching.
    """
    cache_key = sanitize_cache_key(endpoint, params)
    cached_data = cache.get(cache_key)

    if cached_data:
        logger.debug(f"Cache hit for key: {cache_key}")
        return cached_data

    logger.debug(f"Making request to TripAdvisor API: {endpoint} with params: {params}")
    try:
        response = requests.get(endpoint, params=params, timeout=10)
        logger.debug(f"Received response with status code: {response.status_code}")
        response.raise_for_status()
        data = response.json()
        logger.debug(f"TripAdvisor API response: {data}")  # Log complet de la réponse
        cache.set(cache_key, data, timeout=3600)  # Cache pour 1 heure
        logger.debug(f"Fetched and cached data for key: {cache_key}")
        return data
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching data from TripAdvisor: {e}")
    return None

def fetch_location_details(location_id):
    """
    Fetch detailed information about a location.
    """
    url = f"{BASE_URL}/location/{location_id}/details"
    return fetch_tripadvisor_data(url, {'key': API_KEY})

def fetch_location_photos(location_id):
    """
    Fetch photos related to a location.
    """
    url = f"{BASE_URL}/location/{location_id}/photos"
    return fetch_tripadvisor_data(url, {'key': API_KEY})

def fetch_location_reviews(location_id):
    """
    Fetch reviews for a location.
    """
    url = f"{BASE_URL}/location/{location_id}/reviews"
    return fetch_tripadvisor_data(url, {'key': API_KEY})

def fetch_nearby_attractions(lat, lng, radius, category='attractions', limit=10, radiusUnit='m'):
    """
    Fetch nearby attractions based on latitude, longitude, radius, and category.
    """
    url = f"{BASE_URL}/location/nearby_search"
    params = {
        'key': API_KEY,
        'latLong': f"{lat},{lng}",
        'radius': radius,
        'radiusUnit': radiusUnit,
        'category': category,
        'limit': limit
    }
    logger.debug(f"Fetching nearby attractions with URL: {url} and params: {params}")
    return fetch_tripadvisor_data(url, params)

def get_similar_attractions(attraction, limit=5):
    """
    Fetch and return similar attractions based on the given attraction's location.
    """
    logger.debug(f"Getting similar attractions for {attraction.name} (ID: {attraction.location_id})")
    latitude = attraction.latitude
    longitude = attraction.longitude
    category = attraction.category  # Utiliser la même catégorie pour les suggestions

    radius = 500  # Rayon de recherche en mètres, ajustez si nécessaire

    similar_attractions_data = fetch_nearby_attractions(latitude, longitude, radius, category=category, limit=limit)
    similar_attractions = []

    if similar_attractions_data and 'data' in similar_attractions_data:
        locations = similar_attractions_data.get('data', [])
        logger.debug(f"Found {len(locations)} attractions from API")
        for attr_data in locations:
            location_id = attr_data.get('location_id')
            if not location_id or location_id == attraction.location_id:
                logger.debug(f"Skipping location_id: {location_id}")
                continue

            # Vérifier si l'attraction existe dans la base de données
            attraction_obj = Attraction.objects.filter(location_id=location_id).first()
            if attraction_obj:
                logger.debug(f"Attraction {attraction_obj.name} exists in DB")
                # Mettre à jour si l'attraction est obsolète
                if (timezone.now() - attraction_obj.last_updated) > timedelta(days=7):
                    logger.debug(f"Attraction {attraction_obj.name} is outdated. Updating data.")
                    update_success = update_attraction_data(attraction_obj, location_id)
                    if not update_success:
                        logger.error(f"Failed to update attraction data for location_id: {location_id}")
            else:
                logger.debug(f"Attraction with location_id {location_id} not found. Creating new attraction.")
                # Créer l'attraction si elle n'existe pas
                created_attraction = create_attraction_data(location_id)
                if not created_attraction:
                    logger.error(f"Failed to create attraction data for location_id: {location_id}")
                    continue  # Passer si la création a échoué
                attraction_obj = created_attraction

            similar_attractions.append(attraction_obj)

    logger.debug(f"Returning {len(similar_attractions)} similar attractions")
    return similar_attractions

@transaction.atomic
def create_attraction_data(location_id):
    """
    Create attraction data by fetching from TripAdvisor API.
    """
    logger.debug(f"Creating attraction data for location_id: {location_id}")
    details = fetch_location_details(location_id)
    
    # Log the keys of the response for debugging
    if details:
        logger.debug(f"Response keys: {list(details.keys())}")
    else:
        logger.debug("No response received from TripAdvisor API.")
    
    if details and 'location_id' in details:
        try:
            # Traitement des détails
            subcategory = details.get('subcategory', '')
            if isinstance(subcategory, list):
                subcategory = ', '.join([sub.get('localized_name', '') for sub in subcategory if 'localized_name' in sub])
            elif isinstance(subcategory, str):
                subcategory = subcategory  # Peut être vide

            attraction, created = Attraction.objects.update_or_create(
                location_id=details.get('location_id', ''),
                defaults={
                    'name': details.get('name', ''),
                    'description': details.get('description', ''),
                    'web_url': details.get('web_url', ''),
                    'address': details.get('address_obj', {}),
                    'latitude': float(details.get('latitude')) if details.get('latitude') else None,
                    'longitude': float(details.get('longitude')) if details.get('longitude') else None,
                    'category': details.get('category', {}).get('name', ''),
                    'subcategory': subcategory,
                    'see_all_photos': details.get('see_all_photos', ''),
                    'country': details.get('address_obj', {}).get('country', ''),
                    'timezone': details.get('timezone', ''),
                    'price_level': details.get('price_level', ''),
                    'hours': details.get('hours', {}),
                    'cuisine': details.get('cuisine', []),
                    'style': details.get('style', ''),
                    'trip_types': details.get('trip_types', []),
                    'rating_image_url': details.get('rating_image_url', ''),
                    'awards': details.get('awards', []),
                    'ranking_data': details.get('ranking_data', {}) or {},  # Assurez-vous que c'est un dict
                    'review_rating_count': details.get('review_rating_count', {}) or {},  # Assurez-vous que c'est un dict
                    'email': details.get('email', ''),
                    'phone': details.get('phone', ''),
                    'website': details.get('website', ''),
                    'write_review': details.get('write_review', ''),
                    'features': details.get('features', []),
                    'last_updated': timezone.now()
                }
            )

            logger.debug(f"Attraction {attraction.name} {'created' if created else 'updated'}.")

            # Fetch and save photos
            photos_data = fetch_location_photos(location_id)
            if photos_data and 'data' in photos_data and len(photos_data['data']) > 0:
                logger.debug(f"Fetching {len(photos_data['data'])} photos for attraction {attraction.name}.")
                for photo in photos_data['data']:
                    Photo.objects.update_or_create(
                        attraction=attraction,
                        url=photo['images']['original']['url'],
                        defaults={'caption': photo.get('caption', '')}
                    )

            # Fetch and save reviews
            reviews_data = fetch_location_reviews(location_id)
            if reviews_data and 'data' in reviews_data and len(reviews_data['data']) > 0:
                logger.debug(f"Fetching {len(reviews_data['data'])} reviews for attraction {attraction.name}.")
                total_rating = 0
                review_count = 0
                for review in reviews_data['data']:
                    review_obj, created = Review.objects.update_or_create(
                        attraction=attraction,
                        username=review['user']['username'],
                        published_date=review['published_date'],
                        defaults={
                            'rating': float(review.get('rating', 0)),
                            'text': review.get('text', '')
                        }
                    )
                    total_rating += review_obj.rating
                    review_count += 1

                # Calculate average rating and number of reviews
                if review_count > 0:
                    attraction.rating = total_rating / review_count
                    attraction.num_reviews = review_count
                    attraction.save()
                    logger.debug(f"Attraction {attraction.name} updated with average rating {attraction.rating} based on {attraction.num_reviews} reviews.")
            else:
                attraction.rating = None
                attraction.num_reviews = 0
                attraction.save()
                logger.debug(f"Attraction {attraction.name} has no reviews.")

            return attraction
        except Exception as e:
            logger.error(f"Error creating attraction: {e}")
            return None
    else:
        logger.error(f"No details found for location_id: {location_id}. Response: {details}")
        return None

@transaction.atomic
def update_attraction_data(attraction, location_id):
    """
    Update attraction data by fetching from TripAdvisor API.
    """
    logger.debug(f"Updating attraction data for location_id: {location_id}")
    details = fetch_location_details(location_id)
    
    # Log the keys of the response for debugging
    if details:
        logger.debug(f"Response keys: {list(details.keys())}")
    else:
        logger.debug("No response received from TripAdvisor API.")
    
    if details and 'location_id' in details:
        try:
            # Traitement des détails
            subcategory = details.get('subcategory', '')
            if isinstance(subcategory, list):
                subcategory = ', '.join([sub.get('localized_name', '') for sub in subcategory if 'localized_name' in sub])
            elif isinstance(subcategory, str):
                subcategory = subcategory  # Peut être vide

            # Mise à jour des champs de l'attraction
            attraction.name = details.get('name', '')
            attraction.description = details.get('description', '')
            attraction.web_url = details.get('web_url', '')
            attraction.address = details.get('address_obj', {})
            attraction.latitude = float(details.get('latitude')) if details.get('latitude') else None
            attraction.longitude = float(details.get('longitude')) if details.get('longitude') else None
            attraction.category = details.get('category', {}).get('name', '')
            attraction.subcategory = subcategory
            attraction.see_all_photos = details.get('see_all_photos', '')
            attraction.country = details.get('address_obj', {}).get('country', '')
            attraction.timezone = details.get('timezone', '')
            attraction.price_level = details.get('price_level', '')
            attraction.hours = details.get('hours', {})
            attraction.cuisine = details.get('cuisine', [])
            attraction.style = details.get('style', '')
            attraction.trip_types = details.get('trip_types', [])
            attraction.rating_image_url = details.get('rating_image_url', '')
            attraction.awards = details.get('awards', [])
            attraction.ranking_data = details.get('ranking_data', {}) or {}
            attraction.review_rating_count = details.get('review_rating_count', {}) or {}
            attraction.email = details.get('email', '')
            attraction.phone = details.get('phone', '')
            attraction.website = details.get('website', '')
            attraction.write_review = details.get('write_review', '')
            attraction.features = details.get('features', [])
            attraction.last_updated = timezone.now()
            attraction.save()

            logger.debug(f"Attraction {attraction.name} fields updated.")

            # Mise à jour des photos
            photos_data = fetch_location_photos(location_id)
            if photos_data and 'data' in photos_data and len(photos_data['data']) > 0:
                logger.debug(f"Fetching {len(photos_data['data'])} photos for attraction {attraction.name}.")
                existing_photos = set(attraction.photos.values_list('url', flat=True))
                for photo in photos_data['data']:
                    url = photo['images']['original']['url']
                    if url not in existing_photos:
                        Photo.objects.create(
                            attraction=attraction,
                            url=url,
                            caption=photo.get('caption', '')
                        )
                        logger.debug(f"Added new photo: {url}")

            # Mise à jour des reviews
            reviews_data = fetch_location_reviews(location_id)
            if reviews_data and 'data' in reviews_data and len(reviews_data['data']) > 0:
                logger.debug(f"Fetching {len(reviews_data['data'])} reviews for attraction {attraction.name}.")
                total_rating = 0
                review_count = 0
                existing_reviews = set(attraction.reviews.values_list('username', 'published_date'))
                for review in reviews_data['data']:
                    username = review['user']['username']
                    published_date = review['published_date']
                    if (username, published_date) not in existing_reviews:
                        Review.objects.create(
                            attraction=attraction,
                            username=username,
                            published_date=published_date,
                            rating=float(review.get('rating', 0)),
                            text=review.get('text', '')
                        )
                        logger.debug(f"Added new review by {username} on {published_date}")
                    # Recalcul des ratings
                    review_obj = attraction.reviews.filter(username=username, published_date=published_date).first()
                    if review_obj:
                        total_rating += review_obj.rating
                        review_count += 1

                # Calculer la note moyenne et le nombre de reviews
                if review_count > 0:
                    attraction.rating = total_rating / review_count
                    attraction.num_reviews = review_count
                    attraction.save()
                    logger.debug(f"Attraction {attraction.name} updated with average rating {attraction.rating} based on {attraction.num_reviews} reviews.")
            else:
                attraction.rating = None
                attraction.num_reviews = 0
                attraction.save()
                logger.debug(f"Attraction {attraction.name} has no reviews.")

            return True
        except Exception as e:
            logger.error(f"Error updating attraction data: {e}")
            return False
    else:
        logger.error(f"No details found for location_id: {location_id}. Response: {details}")
        return False
