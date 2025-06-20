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

def generate_health_response(user_data, prompt=None, image_file=None, audio_file=None):
    # 1. Process audio if provided (overrides text prompt)
    if audio_file:
        prompt = transcribe_audio(audio_file)
        if not prompt:
            return {"text": "Could not process audio. Please try again."}

    # 2. Detect missing fields
    missing_fields = [
        field for field in ["conditions", "allergies", "income_range"]
        if not user_data.get(field)
    ]
    reminder = (
        f"\n(For better advice, update your profile: {', '.join(missing_fields)}!)"
        if missing_fields else ""
    )

    # 3. System prompt with language flexibility
    system_prompt = f"""
    You are a friendly and intelligent health assistant. 

    You help users with:
    - General health questions (e.g., symptoms, prevention, wellness)
    - Health insurance advice if needed

    You have full access to the user's health profile via the `user_context`. 
    This includes fields such as:
    - Health conditions (e.g., asthma, diabetes)
    - Allergies
    - Income range
    - Lifestyle habits (e.g., is_smoker, alcohol_use, exercise_frequency, diet_type)
    - Medical history (e.g., surgeries, medications, family history)

    Use all this information to personalize your response. 
    If any of this data is missing, politely remind the user to update their profile for more accurate help at the end.

    Always respond in the user's language.
    Don't make your response with the same feel everytime, be friendly and don't sound too professional.

    ⚠️ Format your entire answer as a JSON object with this structure:
    {{
    "text": "Your complete answer here.",
    "links": ["optional helpful link"]
    }}

    (Only include 'links' if necessary. Output must be a valid JSON object.)
    {reminder}
    """

    # 4. Prepare messages
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "system", "content": f"Here is the user's health profile data:\n{json.dumps(user_data, indent=2, default=str)}"}
    ]
    
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
    
def generate_basic_health_response(prompt=None, image_file=None, audio_file=None):
    from openai import OpenAI
    import base64
    import json

    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    if audio_file:
        prompt = transcribe_audio(audio_file)
        if not prompt:
            return {"text": "Could not understand your voice message. Please try again."}

    system_prompt = """
    You are a helpful AI health assistant. Reply to any health-related question in simple terms.
    If the question is unclear, ask the user to clarify.
    Detect the language in the question and ensure to reply in that language.
    Always return a JSON object like this:
    {
      "text": "your reply",
      "links": ["optional", "relevant", "links"]
    }
    """

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

    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.4
        )
        ai_response = json.loads(response.choices[0].message.content)
        return {"text": ai_response.get("text", "No response generated")} | ai_response
    except Exception as e:
        return {"text": f"Error: {str(e)}"}
