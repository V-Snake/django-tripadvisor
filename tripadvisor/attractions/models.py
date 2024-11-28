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
    subcategory = models.CharField(max_length=255, blank=True, null=True)
    see_all_photos = models.URLField(blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
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
