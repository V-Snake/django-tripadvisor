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

class AttractionSerializer(serializers.ModelSerializer):
    photos = PhotoSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)

    class Meta:
        model = Attraction
        fields = '__all__'

class NearbySearchSerializer(serializers.Serializer):
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    radius = serializers.IntegerField(min_value=1)
    profile = serializers.ChoiceField(choices=['local', 'tourist', 'professional'])
