from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.views import View
from django.utils.decorators import method_decorator
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.forms.models import model_to_dict
from healthSubs.models import HealthProfile
from .models import Conversation
from .openai_utilis import generate_health_response, generate_basic_health_response
import tempfile
import requests
import logging
from django.utils.xmlutils import SimplerXMLGenerator
from io import StringIO

User = get_user_model()

logger = logging.getLogger(__name__)

class HealthChatbotView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        prompt = request.data.get("prompt")
        image_file = request.FILES.get("image")
        audio_file = request.FILES.get("audio")

        if not (prompt or image_file or audio_file):
            return Response({"error": "Provide text, image, or audio."}, status=400)

        try:
            health_profile = HealthProfile.objects.get(user=user)
            profile_dict = model_to_dict(health_profile)
        except HealthProfile.DoesNotExist:
            profile_dict = {}

        ai_response = generate_health_response(
            user_data=profile_dict,
            prompt=prompt,
            image_file=image_file,
            audio_file=audio_file,
        )

        Conversation.objects.create(
            user=user,
            prompt=prompt or ("Audio Upload" if audio_file else "Image Upload"),
            response=ai_response,
        )
        return Response(ai_response)


@method_decorator(csrf_exempt, name='dispatch')
class TwilioWebhookView(View):
    def build_twiml_response(self, text, links=None):
        """Helper method to generate properly formatted TwiML"""
        stream = StringIO()
        xml = SimplerXMLGenerator(stream, "UTF-8")
        xml.startDocument()
        xml.startElement("Response", {})
        
        xml.startElement("Message", {})
        xml.characters(text)
        xml.endElement("Message")
        
        if links:
            for link in links:
                xml.startElement("Message", {})
                xml.characters(link)
                xml.endElement("Message")
                
        xml.endElement("Response")
        xml.endDocument()
        return stream.getvalue()

    def post(self, request):
        try:
            # Log incoming request for debugging
            logger.info(f"Incoming Twilio request: {request.POST.dict()}")

            from_number = request.POST.get("From")
            message_body = request.POST.get("Body")
            media_url = request.POST.get("MediaUrl0")
            media_type = request.POST.get("MediaContentType0")

            prompt = message_body.strip() if message_body else None
            image_file = None
            audio_file = None

            # Handle media if present
            if media_url and media_type:
                try:
                    logger.info(f"Processing media: {media_url} ({media_type})")
                    media_response = requests.get(media_url, timeout=5)
                    media_response.raise_for_status()
                    
                    with tempfile.NamedTemporaryFile(delete=True) as temp_file:
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
                except Exception as media_error:
                    logger.error(f"Media processing failed: {str(media_error)}")

            # Generate response (replace with your actual function)
            response_data = generate_basic_health_response(
                prompt=prompt,
                image_file=image_file,
                audio_file=audio_file
            )

            response_text = response_data.get("text", "Sorry, I couldn't generate a response.")
            links = response_data.get("links", [])

            # Build proper TwiML response
            twiml = self.build_twiml_response(response_text, links)
            logger.info(f"Sending TwiML response: {twiml}")

            return HttpResponse(twiml, content_type="application/xml")

        except Exception as e:
            logger.error(f"Error in Twilio webhook: {str(e)}", exc_info=True)
            # Return error response to Twilio
            error_twiml = self.build_twiml_response("An error occurred while processing your message")
            return HttpResponse(error_twiml, content_type="application/xml", status=200)