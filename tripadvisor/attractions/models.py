# C:\Users\Nassim\Documents\django-tripadvisor\tripadvisor\attractions\models.py
from django.db import models

class Attraction(models.Model):
    location_id = models.CharField(max_length=100, unique=True, default="UNKNOWN")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    web_url = models.URLField(blank=True, null=True)
    address = models.JSONField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True)
    subcategory = models.CharField(max_length=255, blank=True, null=True)  # Peut contenir une chaîne vide ou une liste concaténée
    see_all_photos = models.URLField(blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    timezone = models.CharField(max_length=100, blank=True, null=True)
    price_level = models.CharField(max_length=50, blank=True, null=True)
    hours = models.JSONField(blank=True, null=True)
    cuisine = models.JSONField(blank=True, null=True)
    style = models.CharField(max_length=100, blank=True, null=True)
    trip_types = models.JSONField(blank=True, null=True)
    rating_image_url = models.URLField(blank=True, null=True)
    awards = models.JSONField(blank=True, null=True)
    rating = models.FloatField(blank=True, null=True)
    num_reviews = models.IntegerField(blank=True, null=True)
    ranking_data = models.JSONField(blank=True, null=True)  # Stockage des données de classement
    review_rating_count = models.JSONField(blank=True, null=True)  # Compte des ratings par niveau
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    write_review = models.URLField(blank=True, null=True)
    features = models.JSONField(blank=True, null=True)  # Fonctionnalités comme "Wheelchair Accessible"
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Photo(models.Model):
    attraction = models.ForeignKey(Attraction, related_name='photos', on_delete=models.CASCADE)
    url = models.URLField()
    caption = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.url


class Review(models.Model):
    attraction = models.ForeignKey(Attraction, related_name='reviews', on_delete=models.CASCADE)
    username = models.CharField(max_length=255)
    rating = models.FloatField()
    text = models.TextField(blank=True, null=True)
    published_date = models.DateTimeField()

    def __str__(self):
        return f"Review by {self.username} for {self.attraction.name}"
