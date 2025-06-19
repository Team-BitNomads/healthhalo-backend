from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import HealthProfile
from .serializers import HealthProfileSerializer

class HealthProfileAPI(generics.RetrieveUpdateAPIView):
    serializer_class = HealthProfileSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'put', 'patch']  # Disable delete

    def get_object(self):
        """Get or create profile for authenticated user"""
        return HealthProfile.objects.get_or_create(user=self.request.user)[0]

    def perform_update(self, serializer):
        """Auto-calculate risk level on update"""
        instance = serializer.save()
        self._calculate_risk_level(instance)

    def _calculate_risk_level(self, profile):
        """Medical-grade risk assessment"""
        risk_score = 0
        
        # Medical Conditions (CDC weights)
        condition_weights = {
            'Diabetes': 3,
            'Hypertension': 2,
            'HIV/AIDS': 4,
            'Cancer': 5,
            'Asthma': 1
        }
        risk_score += sum(condition_weights.get(cond, 0) for cond in profile.conditions)

        # Lifestyle Factors
        if profile.is_smoker: risk_score += 3
        if profile.alcohol_use: risk_score += 2
        if profile.exercise_frequency == 'none': risk_score += 2
        if profile.sleep_hours and profile.sleep_hours < 6: risk_score += 1

        # Family History
        family_weights = {
            'Heart Disease': 2,
            'Diabetes': 1,
            'Cancer': 2
        }
        risk_score += sum(family_weights.get(cond, 0) for cond in profile.family_history)

        # Weight Status
        if profile.weight_category == 'overweight': risk_score += 1
        elif profile.weight_category == 'obese': risk_score += 2

        # Determine final level
        if risk_score >= 8:
            profile.risk_level = 'high'
        elif risk_score >= 4:
            profile.risk_level = 'medium'
        else:
            profile.risk_level = 'low'
        
        profile.save()