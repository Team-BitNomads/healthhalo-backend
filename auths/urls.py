from django.urls import path
from rest_framework_simplejwt.views import TokenVerifyView
from auths.views import RegisterView, CustomTokenObtainPairView, LogoutView, GetCSRFToken, CustomTokenRefreshView

urlpatterns = [
    # Auth Endpoints
    path('signup/', RegisterView.as_view(), name='signup'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('csrf/', GetCSRFToken.as_view(), name='get_csrf_token'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # JWT Utility Endpoints
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]