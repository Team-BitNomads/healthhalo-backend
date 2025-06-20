from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/user-auth/', include('auths.urls')),
    path('api/health-sub/', include('healthSubs.urls')),
    path('api/chatbot/', include('chatbot.urls')),
    path('api/wallet/', include('wallets.urls')),
    path('api/circles/', include('circles.urls')),
]