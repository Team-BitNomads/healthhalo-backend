
# 🧠 Health Chatbot API Documentation

This chatbot API provides intelligent, context-aware responses to users' health and insurance-related queries using text, audio, or image inputs. Responses are generated via OpenAI's GPT-4-turbo model.

---

## 🔐 Authentication

This endpoint is **protected**. You must be authenticated (via token or session) to access it.

Make sure to send the `Authorization` header:

```
Authorization: Bearer <your_access_token>
```

---

## 📍 Endpoint

```
POST /api/chatbot/
```

---

## 📤 Request Parameters

Send a `multipart/form-data` request. At least one of the following fields is required:

| Field      | Type                     | Required | Description                                              |  
|------------|--------------------------|----------|----------------------------------------------------------|
| `prompt`   | string                   | Optional | Text-based question or description                       |
| `image`    | file (image/jpeg or png) | Optional | Upload image related to the query (e.g., skin condition) |
| `audio`    | file (mp3, m4a, etc.)    | Optional | Upload voice input to be transcribed                     |

📝 **At least one of** `prompt`, `image`, or `audio` **must be provided.**

---

## 📥 Example Request (Text)

```bash
curl -X POST /api/health-sub/ \
  -H "Authorization: Bearer <your_token>" \
  -F "prompt=What health plan should I consider if I have asthma?"
```

---

## 📥 Example Request (Audio)

```bash
curl -X POST /api/health-sub/ \
  -H "Authorization: Bearer <your_token>" \
  -F "audio=@/path/to/audio.m4a"
```

---

## 📥 Example Request (Image)

```bash
curl -X POST /api/health-sub/ \
  -H "Authorization: Bearer <your_token>" \
  -F "image=@/path/to/image.jpg"
```

---

## ✅ Successful Response

Returns a JSON object with the AI-generated message and optional helpful links.

```json
{
  "text": "Since you mentioned asthma and you're uninsured, consider MedShield Plan B which offers respiratory coverage.",
  "links": [
    "https://example.com/planb-details"
  ]
}
```

---

## ⚠️ Error Responses

| Status | Message                                       | Reason                          |
|--------|-----------------------------------------------|---------------------------------|
| 400    | `{"error": "Provide text, image, or audio."}` | No input provided               |
| 401    | Authentication error                          | Missing or invalid token        |
| 500    | `{"text": "Error: <details>"}`                | Internal error or API failure   |

---

## 🧠 Behind the Scenes

- If `audio` is sent, it’s transcribed using **OpenAI Whisper**.
- If `image` is sent, it’s encoded and sent to **GPT-4 with vision**.
- Responses are context-aware — user health profile is used to improve accuracy.
- Conversation history is saved automatically per user.

---

## 📦 Response Format (Always JSON)

```json
{
  "text": "string",
  "links": ["url1", "url2"] // optional
}
```

---

## 🔄 Notes

- User health profiles (conditions, allergies, income range) improve accuracy.
- AI can detect language from input and respond accordingly.

---

## 👨‍💻 Maintainer


© 2025 HealthHalo API Docs
