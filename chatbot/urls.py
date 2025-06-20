from django.urls import path
from .views import HealthChatbotView

urlpatterns = [
    path("", HealthChatbotView.as_view(), name="health-chatbot"),
]