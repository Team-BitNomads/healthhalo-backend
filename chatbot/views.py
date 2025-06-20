from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from healthSubs.models import HealthProfile
from .models import Conversation
from .openai_utilis import generate_health_response, generate_basic_health_response
from django.views import View
from django.utils.decorators import method_decorator
from django.core.files.uploadedfile import InMemoryUploadedFile
import tempfile
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import requests

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

@method_decorator(csrf_exempt, name='dispatch')
class TwilioWebhookView(View):
    def post(self, request):
        from_number = request.POST.get("From")
        message_body = request.POST.get("Body")
        media_url = request.POST.get("MediaUrl0")
        media_type = request.POST.get("MediaContentType0")

        prompt = message_body.strip() if message_body else None
        image_file = None
        audio_file = None

        if media_url and media_type:
            media_response = requests.get(media_url)
            temp_file = tempfile.NamedTemporaryFile(delete=True)
            temp_file.write(media_response.content)
            temp_file.seek(0)

            if media_type.startswith("image"):
                image_file = InMemoryUploadedFile(
                    temp_file, None, 'image.jpg', media_type, temp_file.tell(), None
                )
            elif media_type.startswith("audio"):
                audio_file = InMemoryUploadedFile(
                    temp_file, None, 'audio.mp3', media_type, temp_file.tell(), None
                )

        response_data = generate_basic_health_response(
            prompt=prompt,
            image_file=image_file,
            audio_file=audio_file
        )

        response_text = response_data.get("text", "Sorry, I couldn’t generate a response.")
        links = response_data.get("links", [])

        # Construct TwiML XML
        twiml = f"""
        <Response>
            <Message>{response_text}</Message>
        </Response>
        """

        # If links exist, append them as extra messages
        if links:
            twiml = "<Response>"
            twiml += f"<Message>{response_text}</Message>"
            for link in links:
                twiml += f"<Message>{link}</Message>"
            twiml += "</Response>"

        return HttpResponse(twiml, content_type="text/xml")