import base64
import json
from datetime import timedelta
from django.utils import timezone
from openai import OpenAI
from django.conf import settings
from .models import Claim

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def validate_claim(claim):
    """AI claim verification with receipt OCR and fraud checks"""
    # Hardcoded fraud rules
    if claim.amount > 5000:
        return False, "Claim exceeds maximum allowed amount (5000)"

    if claim.user.health_profile.risk_level == 'high' and claim.amount > 2000:
        return False, "High-risk users have lower claim limits"

    recent_claims = Claim.objects.filter(
        user=claim.user,
        created_at__gte=timezone.now() - timedelta(days=30))
    if recent_claims.count() >= 3:
        return False, "Too many claims in the last 30 days"

    messages = [{
        "role": "system",
        "content": """Analyze this medical claim and return JSON with:
        - valid (boolean)
        - reason (str)
        - amount_match (boolean, if receipt exists)
        - date_valid (boolean)
        """
    }]

    messages.append({
        "role": "user",
        "content": f"""
        CLAIM DETAILS:
        - Amount: {claim.amount}
        - Reason: {claim.reason}
        - User Health Conditions: {claim.user.health_profile.conditions}
        """
    })

    if claim.receipt:
        try:
            with claim.receipt.open('rb') as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')

            messages.append({
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": f"data:image/jpeg;base64,{base64_image}"},
                    {"type": "text", "text": "Verify: 1. Amount matches 2. Date is recent 3. Items match claim reason"}
                ]
            })
        except Exception as e:
            return False, f"Receipt processing failed: {str(e)}"

    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.1
        )
        result = json.loads(response.choices[0].message.content)
    except Exception as e:
        return False, f"AI verification error: {str(e)}"

    if not result.get('valid'):
        return False, result.get('reason', 'AI rejection')

    if claim.receipt and not result.get('amount_match', False):
        return False, "Receipt amount doesn't match claim"

    return True, "Approved"
