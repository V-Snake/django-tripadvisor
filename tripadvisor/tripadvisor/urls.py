#C:\Users\Nassim\Documents\django-tripadvisor\tripadvisor\tripadvisor\urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/attractions/', include('attractions.urls')),
]
