import json
from openai import OpenAI
import base64
from django.conf import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def transcribe_audio(audio_file):
    """Convert audio to text using Whisper."""
    try:
        transcript = client.audio.transcriptions.create(
            file=audio_file,
            model="whisper-1",
            response_format="text"
        )
        return transcript
    except Exception as e:
        return None

def generate_health_response(user_context, prompt=None, image_file=None, audio_file=None):
    # 1. Process audio if provided (overrides text prompt)
    if audio_file:
        prompt = transcribe_audio(audio_file)
        if not prompt:
            return {"text": "Could not process audio. Please try again."}

    # 2. Detect missing fields
    missing_fields = [
        field for field in ["conditions", "allergies", "income_range"]
        if not user_context.get(field)
    ]
    reminder = (
        f"\n(For better advice, update your profile: {', '.join(missing_fields)}!)"
        if missing_fields else ""
    )

    # 3. System prompt with language flexibility
    system_prompt = f"""
    You are a health professional specializing in health insurance. Rules:
    1. Respond in the USER'S LANGUAGE (auto-detect from their input).
    2. For health queries, use: {user_context.get('conditions', [])}.
    3. For insurance queries:
    - If uninsured: Suggest plans with links.
    - If insured: Guide on current coverage.
    4. Format: Always return a JSON object with keys "text" and optional "links", for example: {{"text": "response"}}.
    5. Reminder: "{reminder}"
    """

    # 4. Prepare messages
    messages = [{"role": "system", "content": system_prompt}]
    
    if prompt:
        messages.append({"role": "user", "content": prompt})
    
    if image_file:
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        messages.append({
            "role": "user",
            "content": [{
                "type": "image_url",
                "image_url": f"data:image/jpeg;base64,{base64_image}"
            }]
        })

    # 5. Call OpenAI
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.3
        )
        ai_response = json.loads(response.choices[0].message.content)
        return {"text": ai_response.get("text", "No response generated")} | ai_response
    except Exception as e:
        return {"text": f"Error: {str(e)}"}