# C:\Users\Nassim\Documents\django-tripadvisor\tripadvisor\attractions\urls.py

from django.urls import path
from .views import AttractionDetailUpdate, NearbySearch

urlpatterns = [
    path('nearby/', NearbySearch.as_view(), name='nearby-attractions'),
    path('<str:location_id>/', AttractionDetailUpdate.as_view(), name='attraction-detail'),
]
