
# Health Profile API Documentation

This API allows authenticated users to **retrieve** and **update** their health profile. The system uses this data to compute a `risk_level` score based on medical, lifestyle, and family history factors.

---

## 🔒 Authentication

All requests require a valid **JWT access token** in the `Authorization` header.

**Header format:**
```
Authorization: Bearer <access_token>
```

The token should be retrieved from login and stored securely in localStorage or memory. Example in React:

```js
const token = localStorage.getItem("access_token");
const headers = {
  Authorization: `Bearer ${token}`
};
```

---

## 📍 Endpoint

**URL:** `/api/health-sub/`  
**Methods Supported:** `GET`, `PUT`  
**Requires Authentication:** ✅ Yes (JWT)  
**Content-Type:** `application/json` (for PUT)

---

## 📤 GET Request

### ✅ Retrieve your health profile

React Fetch Example:
```js
fetch("/api/health-sub/", {
  method: "GET",
  headers: {
    Authorization: `Bearer ${localStorage.getItem("access_token")}`
  }
})
  .then(res => res.json())
  .then(data => console.log(data));
```

---

## 📥 PUT Request

### ✏️ Create or update your health profile

If a profile doesn't exist, one will be created automatically. This request **must include all fields**.

React Axios Example:
```js
import axios from 'axios';

axios.put("/api/health-sub/", {
  full_name: "Complete Test User",
  date_of_birth: "1985-08-20",
  gender: "F",
  marital_status: "Married",
  occupation: "Software Engineer",
  location: "Lagos",
  income_range: "100,000-200,000",
  weight_category: "healthy",
  height_cm: 170,
  weight_kg: 65,
  conditions: ["Hypertension", "Asthma"],
  medications: ["Ventolin", "Propranolol"],
  allergies: ["Penicillin"],
  surgeries: ["Appendectomy"],
  family_history: ["Diabetes", "Heart Disease"],
  is_smoker: false,
  alcohol_use: true,
  exercise_frequency: "3-5",
  diet_type: "balanced",
  sleep_hours: 7,
  knows_blood_pressure: true,
  bp_checked_recently: true,
  nearest_facility: "City General Hospital",
  facility_distance: "30 mins – 1 hour",
  has_insurance: true,
  insurance_details: "Company Gold Plan"
}, {
  headers: {
    Authorization: `Bearer ${localStorage.getItem("access_token")}`
  }
})
.then(response => console.log(response.data));
```

---

## 📦 Sample JSON Response

```json
{
  "id": 4,
  "full_name": "Complete Test User",
  "date_of_birth": "1985-08-20",
  "gender": "F",
  "marital_status": "Married",
  "occupation": "Software Engineer",
  "location": "Lagos",
  "income_range": "100,000-200,000",
  "weight_category": "healthy",
  "height_cm": 170,
  "weight_kg": 65,
  "conditions": ["Hypertension", "Asthma"],
  "medications": ["Ventolin", "Propranolol"],
  "allergies": ["Penicillin"],
  "surgeries": ["Appendectomy"],
  "family_history": ["Diabetes", "Heart Disease"],
  "is_smoker": false,
  "alcohol_use": true,
  "exercise_frequency": "3-5",
  "diet_type": "balanced",
  "sleep_hours": 7,
  "knows_blood_pressure": true,
  "bp_checked_recently": true,
  "nearest_facility": "City General Hospital",
  "facility_distance": "30 mins – 1 hour",
  "has_insurance": true,
  "insurance_details": "Company Gold Plan",
  "risk_level": "high",
  "last_updated": "2025-06-19T16:06:11.288870Z",
  "user": 2
}
```

---

## ℹ️ Notes

- Risk level is calculated automatically on each update
- All fields must be sent on `PUT` request
- No `POST`, `DELETE`, or partial update via `PATCH` is supported at this time
- Frontend must ensure token is included in every request using appropriate storage and headers

---

© 2025 HealthApp API Docs