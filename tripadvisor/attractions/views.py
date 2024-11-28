from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from .models import Attraction
from .serializers import AttractionSerializer, NearbySearchSerializer
from .utils import (
    fetch_nearby_attractions,
    create_attraction_data,
    update_attraction_data
)
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

class NearbySearch(APIView):
    """
    Search for nearby attractions based on user profile and location.
    """
    def post(self, request):
        logger.debug(f"Received NearbySearch request with data: {request.data}")
        serializer = NearbySearchSerializer(data=request.data)
        if serializer.is_valid():
            # Retrieve validated data
            latitude = serializer.validated_data['latitude']
            longitude = serializer.validated_data['longitude']
            radius = serializer.validated_data['radius']
            profile = serializer.validated_data['profile']

            logger.debug(f"Parameters - Latitude: {latitude}, Longitude: {longitude}, Radius: {radius}, Profile: {profile}")

            # Map profiles to categories
            profile_categories = {
                'local': ['restaurants'],
                'tourist': ['hotels', 'attractions', 'restaurants'],
                'professional': ['hotels']
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
                attractions_data = fetch_nearby_attractions(latitude, longitude, radius, category=category, limit=10)
                if attractions_data and 'data' in attractions_data:
                    logger.debug(f"Found {len(attractions_data['data'])} attractions from API for category: {category}")
                    for attr_data in attractions_data['data']:
                        location_id = attr_data.get('location_id')
                        if not location_id or location_id in fetched_location_ids:
                            logger.debug(f"Skipping location_id: {location_id} (already fetched or invalid)")
                            continue

                        fetched_location_ids.add(location_id)

                        # Check if the attraction exists in the database
                        attraction_obj = Attraction.objects.filter(location_id=location_id).first()
                        if attraction_obj:
                            logger.debug(f"Attraction {attraction_obj.name} exists in DB")
                            # Update if the attraction is outdated
                            if self.is_outdated(attraction_obj):
                                logger.debug(f"Attraction {attraction_obj.name} is outdated. Updating data.")
                                update_success = update_attraction_data(attraction_obj, location_id)
                                if not update_success:
                                    logger.error(f"Failed to update attraction data for location_id: {location_id}")
                        else:
                            logger.debug(f"Attraction with location_id {location_id} not found. Creating data.")
                            # Create attraction if it doesn't exist
                            created_attraction = create_attraction_data(location_id)
                            if not created_attraction:
                                logger.error(f"Failed to create attraction data for location_id: {location_id}")
                                continue  # Skip if creation failed
                            attraction_obj = created_attraction

                        attractions_list.append(attraction_obj)
                else:
                    logger.debug(f"No data returned for category: {category}")

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
        outdated = (timezone.now() - attraction.last_updated) > timedelta(days=7)
        logger.debug(f"Attraction {attraction.name} outdated: {outdated}")
        return outdated


class AttractionDetailUpdate(generics.RetrieveUpdateAPIView):
    """
    Retrieve and update details of a specific attraction based on location_id.
    """
    serializer_class = AttractionSerializer
    lookup_field = 'location_id'

    def get_queryset(self):
        return Attraction.objects.all()

    def retrieve(self, request, *args, **kwargs):
        location_id = kwargs.get('location_id')
        # Try to get the attraction from the database
        attraction = Attraction.objects.filter(location_id=location_id).first()
        
        if attraction:
            serializer = self.get_serializer(attraction)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            # Fetch data from the TripAdvisor API and create the attraction
            created_attraction = create_attraction_data(location_id)
            if created_attraction:
                serializer = self.get_serializer(created_attraction)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {"detail": "Attraction not found or failed to fetch details."},
                    status=status.HTTP_404_NOT_FOUND
                )
