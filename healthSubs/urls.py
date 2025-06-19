from django.urls import path
from .views import HealthProfileAPI

urlpatterns = [
    path('', HealthProfileAPI.as_view(), name='health-profile'),
]