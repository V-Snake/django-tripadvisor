# C:\Users\Nassim\Documents\django-tripadvisor\tripadvisor\attractions\serializers.py

from rest_framework import serializers
from .models import Attraction, Photo, Review

class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ['url', 'caption']

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['username', 'rating', 'text', 'published_date']

class RankingDataSerializer(serializers.Serializer):
    geo_location_id = serializers.IntegerField(required=False, allow_null=True)
    ranking_string = serializers.CharField(required=False, allow_blank=True)
    geo_location_name = serializers.CharField(required=False, allow_blank=True)
    ranking_out_of = serializers.IntegerField(required=False, allow_null=True)
    ranking = serializers.IntegerField(required=False, allow_null=True)

class ReviewRatingCountSerializer(serializers.Serializer):
    one = serializers.IntegerField(source='1', required=False, allow_null=True)
    two = serializers.IntegerField(source='2', required=False, allow_null=True)
    three = serializers.IntegerField(source='3', required=False, allow_null=True)
    four = serializers.IntegerField(source='4', required=False, allow_null=True)
    five = serializers.IntegerField(source='5', required=False, allow_null=True)

class AttractionSerializer(serializers.ModelSerializer):
    photos = PhotoSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    ranking_data = RankingDataSerializer(required=False, allow_null=True)
    review_rating_count = ReviewRatingCountSerializer(required=False, allow_null=True)
    
    class Meta:
        model = Attraction
        fields = [
            'location_id',
            'name',
            'description',
            'web_url',
            'address',
            'latitude',
            'longitude',
            'category',
            'subcategory',
            'see_all_photos',
            'country',
            'timezone',
            'price_level',
            'hours',
            'cuisine',
            'style',
            'trip_types',
            'rating_image_url',
            'awards',
            'rating',
            'num_reviews',
            'ranking_data',
            'review_rating_count',
            'email',
            'phone',
            'website',
            'write_review',
            'features',
            'last_updated',
            'photos',
            'reviews'
            # Supprimé 'similar_attractions' pour l'instant
        ]

class NearbySearchSerializer(serializers.Serializer):
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    radius = serializers.IntegerField()
    profile = serializers.ChoiceField(choices=['local', 'tourist', 'professional'])
