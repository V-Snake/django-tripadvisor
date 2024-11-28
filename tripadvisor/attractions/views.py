# C:\Users\Nassim\Documents\django-tripadvisor\tripadvisor\attractions\views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Attraction, Photo, Review
from .serializers import AttractionSerializer, NearbySearchSerializer
from .utils import (
    fetch_location_details,
    fetch_location_photos,
    fetch_location_reviews,
    fetch_nearby_attractions
)
from django.utils import timezone
from django.db import transaction
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

class AttractionDetailUpdate(APIView):
    def get(self, request, location_id):
        """
        Get details of a specific attraction.
        """
        attraction = Attraction.objects.filter(location_id=location_id).first()
        if attraction:
            # Update the attraction if it's outdated (e.g., older than 7 days)
            if self.is_outdated(attraction):
                self.update_attraction_data(attraction, location_id)
            serializer = AttractionSerializer(attraction)
            return Response(serializer.data)

        # Fetch data from TripAdvisor API
        success = self.create_attraction_data(location_id)
        if success:
            attraction = Attraction.objects.get(location_id=location_id)
            serializer = AttractionSerializer(attraction)
            return Response(serializer.data)
        else:
            return Response({'error': 'Attraction not found or unable to fetch data'}, status=status.HTTP_404_NOT_FOUND)

    def is_outdated(self, attraction):
        """
        Check if the attraction data is outdated.
        """
        return (timezone.now() - attraction.last_updated) > timedelta(days=7)

    @transaction.atomic
    def create_attraction_data(self, location_id):
        details = fetch_location_details(location_id)
        if details:
            try:
                attraction, created = Attraction.objects.update_or_create(
                    location_id=details['location_id'],
                    defaults={
                        'name': details.get('name', ''),
                        'description': details.get('description', ''),
                        'web_url': details.get('web_url', ''),
                        'address': details.get('address_obj', {}),
                        'latitude': details.get('latitude'),
                        'longitude': details.get('longitude'),
                        'category': details.get('category', {}).get('name', ''),
                        'subcategory': ', '.join([sub['name'] for sub in details.get('subcategory', [])]),
                        'see_all_photos': details.get('see_all_photos', ''),
                        'country': details.get('address_obj', {}).get('country', ''),
                        'last_updated': timezone.now()
                    }
                )

                # Fetch and save photos
                photos_data = fetch_location_photos(location_id)
                if photos_data and 'data' in photos_data:
                    for photo in photos_data['data']:
                        Photo.objects.update_or_create(
                            attraction=attraction,
                            url=photo['images']['original']['url'],
                            defaults={
                                'caption': photo.get('caption', '')
                            }
                        )

                # Fetch and save reviews
                reviews_data = fetch_location_reviews(location_id)
                if reviews_data and 'data' in reviews_data:
                    for review in reviews_data['data']:
                        Review.objects.update_or_create(
                            attraction=attraction,
                            username=review['user']['username'],
                            published_date=review['published_date'],
                            defaults={
                                'rating': review.get('rating', 0),
                                'text': review.get('text', '')
                            }
                        )
                return True
            except Exception as e:
                logger.error(f"Error saving attraction data: {e}")
                return False
        return False

    @transaction.atomic
    def update_attraction_data(self, attraction, location_id):
        """
        Update existing attraction data.
        """
        details = fetch_location_details(location_id)
        if details:
            try:
                # Update attraction fields
                attraction.name = details.get('name', '')
                attraction.description = details.get('description', '')
                attraction.web_url = details.get('web_url', '')
                attraction.address = details.get('address_obj', {})
                attraction.latitude = details.get('latitude')
                attraction.longitude = details.get('longitude')
                attraction.category = details.get('category', {}).get('name', '')
                attraction.subcategory = ', '.join([sub['name'] for sub in details.get('subcategory', [])])
                attraction.see_all_photos = details.get('see_all_photos', '')
                attraction.country = details.get('address_obj', {}).get('country', '')
                attraction.last_updated = timezone.now()
                attraction.save()

                # Update photos
                photos_data = fetch_location_photos(location_id)
                if photos_data and 'data' in photos_data:
                    existing_photos = set(attraction.photos.values_list('url', flat=True))
                    for photo in photos_data['data']:
                        url = photo['images']['original']['url']
                        if url not in existing_photos:
                            Photo.objects.create(
                                attraction=attraction,
                                url=url,
                                caption=photo.get('caption', '')
                            )

                # Update reviews
                reviews_data = fetch_location_reviews(location_id)
                if reviews_data and 'data' in reviews_data:
                    existing_reviews = set(attraction.reviews.values_list('username', 'published_date'))
                    for review in reviews_data['data']:
                        username = review['user']['username']
                        published_date = review['published_date']
                        if (username, published_date) not in existing_reviews:
                            Review.objects.create(
                                attraction=attraction,
                                username=username,
                                published_date=published_date,
                                rating=review.get('rating', 0),
                                text=review.get('text', '')
                            )
                return True
            except Exception as e:
                logger.error(f"Error updating attraction data: {e}")
                return False
        return False

class NearbySearch(APIView):
    def post(self, request):
        """
        Search for nearby attractions based on user profile and location.
        """
        serializer = NearbySearchSerializer(data=request.data)
        if serializer.is_valid():
            # Récupérer les données validées
            latitude = serializer.validated_data['latitude']
            longitude = serializer.validated_data['longitude']
            radius = serializer.validated_data['radius']
            profile = serializer.validated_data['profile']

            logger.debug(f"Received NearbySearch request with latitude={latitude}, longitude={longitude}, radius={radius}, profile={profile}")

            # Map profiles to categories
            profile_categories = {
                'local': ['restaurants'],
                'tourist': ['hotels', 'attractions', 'restaurants'],
                'professional': ['restaurants', 'hotels', 'geos']  # Ajout de 'geos' pour les professionnels
            }

            categories = profile_categories.get(profile.lower())
            if not categories:
                logger.error(f"Invalid profile: {profile}")
                return Response({'error': 'Invalid profile'}, status=status.HTTP_400_BAD_REQUEST)

            # Fetch nearby attractions for each category and combine results
            attractions_list = []
            fetched_location_ids = set()
            for category in categories:
                logger.debug(f"Fetching category: {category}")
                attractions_data = fetch_nearby_attractions(latitude, longitude, radius, category=category)
                if attractions_data and 'data' in attractions_data:
                    for attr_data in attractions_data['data']:
                        location_id = attr_data.get('location_id')
                        if not location_id:
                            continue

                        if location_id in fetched_location_ids:
                            continue  # Skip duplicates

                        fetched_location_ids.add(location_id)

                        # Check if the attraction exists
                        attraction = Attraction.objects.filter(location_id=location_id).first()
                        if attraction:
                            # Update if the attraction is outdated
                            if self.is_outdated(attraction):
                                self.update_attraction_data(attraction, location_id)
                        else:
                            # Create new attraction data
                            success = self.create_attraction_data(location_id)
                            if not success:
                                continue  # Skip if unable to create attraction
                            attraction = Attraction.objects.get(location_id=location_id)

                        attractions_list.append(attraction)

                        # Limit to 10 results
                        if len(attractions_list) >= 10:
                            break
                else:
                    logger.debug(f"No data returned for category: {category}")
                if len(attractions_list) >= 10:
                    break

            logger.debug(f"Found {len(attractions_list)} attractions for NearbySearch")

            serializer = AttractionSerializer(attractions_list, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            logger.error(f"NearbySearchSerializer validation failed: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def is_outdated(self, attraction):
        """
        Check if the attraction data is outdated.
        """
        return (timezone.now() - attraction.last_updated) > timedelta(days=7)

    @transaction.atomic
    def create_attraction_data(self, location_id):
        """
        Create attraction data by fetching from TripAdvisor API.
        """
        # Reuse the method from AttractionDetailUpdate
        view = AttractionDetailUpdate()
        return view.create_attraction_data(location_id)

    @transaction.atomic
    def update_attraction_data(self, attraction, location_id):
        """
        Update attraction data by fetching from TripAdvisor API.
        """
        # Reuse the method from AttractionDetailUpdate
        view = AttractionDetailUpdate()
        return view.update_attraction_data(attraction, location_id)
