from django.contrib.auth import authenticate
from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.exceptions import TokenError
from .serializers import RegisterSerializer, CustomTokenObtainPairSerializer
from datetime import timedelta
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse
from django.utils.decorators import method_decorator
import logging

logger = logging.getLogger(__name__)

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

@method_decorator(ensure_csrf_cookie, name='dispatch')
class GetCSRFToken(APIView):
    permission_classes = []  # Allow any

    def get(self, request):
        return JsonResponse({"detail": "CSRF cookie set"})

# User Account Creation
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            try:  # Added try-catch for creation errors
                user = serializer.save()
                tokens = get_tokens_for_user(user)
                
                response = Response(
                    {"access": tokens["access"]}, 
                    status=status.HTTP_201_CREATED
                )

                response.set_cookie(
                    key="refresh_token",
                    value=tokens["refresh"],
                    httponly=True,
                    secure=settings.USE_HTTPS,
                    samesite="Lax",
                    max_age=int(timedelta(days=7).total_seconds()),
                )
                return response

            except Exception as e:
                logger.error(f"User creation failed: {str(e)}", exc_info=True) 
                return Response(
                    {"error": "Account creation failed"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# User Authentication
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            response.set_cookie(
                key='refresh_token',
                value=response.data['refresh'],
                httponly=True,
                secure=settings.USE_HTTPS,
                samesite='Lax',
                max_age=int(timedelta(days=7).total_seconds()),
            )
            response.data.pop('refresh', None)
        
        return response

# Token Refresh
class CustomTokenRefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')

        if not refresh_token:
            return Response({"error": "Refresh token not found in cookies"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            new_access_token = str(token.access_token)

            return Response({"access": new_access_token}, status=status.HTTP_200_OK)

        except TokenError as e:
            return Response({"error": f"Invalid or expired refresh token: {str(e)}"}, status=status.HTTP_401_UNAUTHORIZED)

# User Logout
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')
        print("Refresh token:", refresh_token)
        
        if not refresh_token:  # Early return if no token
            return Response(
                {"error": "No refresh token provided"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            token = RefreshToken(refresh_token)
            token.check_blacklist()  # Verify token isn't already blacklisted
            token.blacklist()
            
            response = Response(
                {"message": "Logged out successfully"},
                status=status.HTTP_205_RESET_CONTENT)
            response.delete_cookie('refresh_token')
            return response
            
        except TokenError as e:
            # Case: Invalid/expired/already-blacklisted token
            response = Response(status=status.HTTP_205_RESET_CONTENT)
            response.delete_cookie('refresh_token')
            return response
            
        except Exception as e:
            print(f"Logout failed: {str(e)}")  # or logger.error(...)
            return Response(
                {"error": f"Logout failed: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )