from .models import CustomUser
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    
    class Meta:
        model = CustomUser
        fields = ['username', 'password', 'phone', 'language']
    
    def validate_username(self, value):
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value
    
    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)  # Returns access/refresh tokens
        
        # Add user data
        user = self.user
        data.update({
            'username': user.username,
            'email': user.email,
            'phone': user.phone,
            'language': user.language,
        })
        return data