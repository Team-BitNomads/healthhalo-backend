from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from healthSubs.models import HealthProfile
from .models import Conversation
from .openai_utilis import generate_health_response

User = get_user_model()

class HealthChatbotView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        prompt = request.data.get("prompt")
        image_file = request.FILES.get("image")
        audio_file = request.FILES.get("audio")  # New audio input

        if not (prompt or image_file or audio_file):
            return Response({"error": "Provide text, image, or audio."}, status=400)

        try:
            health_profile = HealthProfile.objects.get(user=user)
            health_context = {
                **vars(health_profile),
                "bmi": health_profile.bmi,
                "is_complete": all([
                    health_profile.conditions,
                    health_profile.allergies,
                    health_profile.income_range,
                ]),
            }
        except HealthProfile.DoesNotExist:
            health_context = {"is_complete": False}

        ai_response = generate_health_response(
            user_context=health_context,
            prompt=prompt,
            image_file=image_file,
            audio_file=audio_file,  # Pass audio file
        )

        Conversation.objects.create(
            user=user,
            prompt=prompt or ("Audio Upload" if audio_file else "Image Upload"),
            response=ai_response,
        )
        return Response(ai_response)