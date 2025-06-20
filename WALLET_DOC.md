# 🏦 Wallet System API Documentation

This documentation provides an overview of the Wallet System API built with Django Rest Framework (DRF). The system supports top-ups and withdrawals, handles user authentication with JWT, and interacts with the frontend via a React Router SPA.

---

## 📁 Endpoints

| Method | Endpoint        | Description                                | Auth Required  |
|--------|------------------|-------------------------------------------|----------------|
| GET    | `/api/wallet/`   | Retrieve wallet & transaction history     |       ✅       |
| POST   | `/api/wallet/`   | Create a top-up or withdrawal transaction |       ✅       |

---

## 🔐 Authentication

All endpoints require JWT **Access Tokens** in the Authorization header.

```http
Authorization: Bearer <your-access-token>
```

Ensure the access token is obtained via your authentication flow.

---

## 📨 API Usage

### 🔍 Get Wallet Info

```http
GET /api/wallet/
```

#### Response

```json
{
  "wallet": {
    "id": 1,
    "balance": "700.00",
    "created_at": "2025-06-20T07:27:36.038501Z",
    "updated_at": "2025-06-20T07:36:10.936290Z",
    "transactions": [
      {
        "id": 1,
        "amount": "500.00",
        "transaction_type": "topup",
        "timestamp": "2025-06-20T07:27:36.885003Z",
        "description": "Initial deposit"
      }
    ]
  }
}
```

---

### 💸 Post a Transaction

```http
POST /api/wallet/
```

#### Headers

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

#### Body

```json
{
  "amount": 200.00,
  "transaction_type": "topup",
  "description": "Optional description"
}
```

#### Successful Response

```json
{
  "id": 1,
  "balance": "500.00",
  "created_at": "2025-06-20T07:27:36.038501Z",
  "updated_at": "2025-06-20T07:38:51.714214Z",
  "transactions": []
}
```

---

## 🧪 cURL Examples

### Top-Up

```bash
curl -X POST /api/wallet/ \
  -H "Authorization: Bearer <your-access-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 200.00,
    "transaction_type": "topup",
    "description": "Additional funds"
}'
```

### Withdrawal

```bash
curl -X POST /api/wallet/ \
  -H "Authorization: Bearer <your-access-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 200.00,
    "transaction_type": "withdrawal",
    "description": "Purchasing item"
}'
```

---

## ⚛️ React Frontend Integration (React Router)

### 📁 `api/wallet.ts`

```ts
import axios from "axios";

const API_URL = "/api/wallet/";

export const getWallet = async (token: string) => {
  return await axios.get(API_URL, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
};

export const postTransaction = async (
  token: string,
  amount: number,
  transaction_type: "topup" | "withdrawal",
  description?: string
) => {
  return await axios.post(API_URL, {
    amount,
    transaction_type,
    description,
  }, {
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });
};
```
---

## 👨‍💻 Maintainer


© 2025 HealthHalo API Docs
