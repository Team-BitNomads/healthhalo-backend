from django.urls import path
from .views import WalletAPIView

urlpatterns = [
    path('', WalletAPIView.as_view(), name='wallet'),
]