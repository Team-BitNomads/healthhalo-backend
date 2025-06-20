from django.urls import path
from .views import HealthChatbotView, TwilioWebhookView

urlpatterns = [
    path('', HealthChatbotView.as_view(), name="health-chatbot"),
    path("twilio-hook/", TwilioWebhookView.as_view(), name="twilio-webhook"),
]