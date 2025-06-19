from rest_framework import serializers
from .models import HealthProfile
from rest_framework_simplejwt.authentication import JWTAuthentication

class HealthProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthProfile
        fields = '__all__'
        read_only_fields = ('user', 'risk_level', 'last_updated')
    
    def validate(self, data):
        """Custom validation for medical data"""
        if data.get('is_smoker') and data.get('exercise_frequency') == 'none':
            raise serializers.ValidationError(
                "Smokers should have at least some exercise. Please update lifestyle information."
            )
        return data

    def create(self, validated_data):
        """Auto-assign user from JWT token"""
        user = self.context['request'].user
        profile, created = HealthProfile.objects.update_or_create(
            user=user,
            defaults=validated_data
        )
        return profile