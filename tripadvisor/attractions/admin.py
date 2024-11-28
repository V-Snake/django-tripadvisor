# C:\Users\Nassim\Documents\django-tripadvisor\tripadvisor\attractions\admin.py

from django.contrib import admin
from .models import Attraction, Photo, Review

@admin.register(Attraction)
class AttractionAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'category', 'last_updated')
    search_fields = ('name', 'country', 'category')
    list_filter = ('country', 'category')


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('attraction', 'url')
    search_fields = ('attraction__name',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('attraction', 'username', 'rating', 'published_date')
    search_fields = ('attraction__name', 'username')
    list_filter = ('rating', 'published_date')
