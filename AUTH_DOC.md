
# 🛡️ Authentication System Documentation

## 📘 Overview
This documentation covers the JWT-based authentication system for the **HealthBackEnd** Django project, with React frontend integration examples.

---

## 📚 Table of Contents
- [API Endpoints](#api-endpoints)
- [Request/Response Examples](#requestresponse-examples)
- [Frontend Integration](#frontend-integration)
- [Security Considerations](#security-considerations)
- [Frontend Utilities](#frontend-utilities)

---

## 🔗 API Endpoints

**Base URL:** `/api/user-auth/`

| Endpoint           | Method | Description                   | Auth Required                |
|--------------------|--------|-------------------------------|------------------------------|
| `signup/`          | POST   | Register new user             | ❌ No                        |
| `login/`           | POST   | Authenticate user             | ❌ No                        |
| `csrf/`            | GET    | Get CSRF token cookie         | ❌ No                        |
| `token/refresh/`   | POST   | Refresh access token          | ✅ Uses refresh token cookie |
| `token/verify/`    | POST   | Verify token validity         | ❌ No                        |
| `logout/`          | POST   | Logout and clear tokens       | ✅ Yes                       |

---

## 📬 Request/Response Examples

### 1. 🧾 User Registration

**Endpoint:** `POST /api/user-auth/signup/`  
**Request:**

```json
{
  "username": "newuser",
  "password": "securepassword123",
  "phone": "1234567890",
  "language": "English"
}
```

**Successful Response:**

```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

> ⚠️ Also sets HTTP-only `refresh_token` cookie.

**React Example:**

```js
const registerUser = async (userData) => {
  try {
    const response = await fetch('/api/user-auth/signup/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken'),
      },
      body: JSON.stringify(userData),
      credentials: 'include'
    });
    return await response.json();
  } catch (error) {
    console.error('Registration failed:', error);
  }
};
```

---

### 2. 🔐 User Login

**Endpoint:** `POST /api/user-auth/login/`  
**Request:**

```json
{
  "username": "existinguser",
  "password": "userpassword123"
}
```

**Response:**

```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "username": "existinguser",
  "email": "user@example.com",
  "phone": "1234567890",
  "language": "English"
}
```

> ⚠️ Sets HTTP-only `refresh_token` cookie.

**React Example:**

```js
const loginUser = async (credentials) => {
  try {
    await fetch('/api/user-auth/csrf/', { credentials: 'include' });

    const response = await fetch('/api/user-auth/login/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
      },
      body: JSON.stringify(credentials),
      credentials: 'include'
    });
    return await response.json();
  } catch (error) {
    console.error('Login failed:', error);
  }
};
```

---

### 3. 🔁 Token Refresh

**Endpoint:** `POST /api/user-auth/token/refresh/`

**Uses:** Refresh token cookie

**Response:**

```json
{
  "access": "new.access.token.here..."
}
```

**React Example:**

```js
const refreshAccessToken = async () => {
  try {
    const response = await fetch('/api/user-auth/token/refresh/', {
      method: 'POST',
      credentials: 'include'
    });
    return await response.json();
  } catch (error) {
    console.error('Token refresh failed:', error);
  }
};
```

---

### 4. 🔒 Protected API Request

**React Example:**

```js
const fetchProtectedData = async (accessToken) => {
  try {
    const response = await fetch('/api/protected-endpoint/', {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
      }
    });
    return await response.json();
  } catch (error) {
    console.error('Request failed:', error);
  }
};
```

---

### 5. 🚪 Logout

**Endpoint:** `POST /api/user-auth/logout/`

**React Example:**

```js
const logoutUser = async () => {
  try {
    await fetch('/api/user-auth/logout/', {
      method: 'POST',
      credentials: 'include'
    });
    // Clear frontend auth state here
  } catch (error) {
    console.error('Logout failed:', error);
  }
};
```

---

## 🛡️ Security Considerations

- **CSRF Protection:**
  - Required for all state-changing requests.
  - Fetch from `/api/user-auth/csrf/` with
  ```js
  fetch('/api/user-auth/csrf/', {
    credentials: 'include'  // ensures cookies are sent and received
  });
  ```
  Do this immediately the react app loads so the cookie is stored and this `'X-CSRFToken': getCookie('csrftoken')` can access it's content
- **JWT Storage:**
  - Access token: store in memory or React state (never localStorage)
  - Refresh token: sent and stored via HTTP-only cookies
- **Token Rotation:**
  - Tokens are rotated on each refresh
  - Compromised tokens are blacklisted
- **Secure Flags:**
  - Cookies use `HttpOnly`, `Secure`, and `SameSite=Lax`

---

## ⚙️ Frontend Utilities

### 🍪 Cookie Helper

```js
function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}
```

---

### 🔄 Auth Context Example

```js
import { createContext, useState } from 'react';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [accessToken, setAccessToken] = useState(null);
  const [user, setUser] = useState(null);

  return (
    <AuthContext.Provider value={{ accessToken, user }}>
      {children}
    </AuthContext.Provider>
  );
};
```

---

### 🧠 Axios Interceptor Example

```js
import axios from 'axios';

const api = axios.create({
  baseURL: '/api/',
  withCredentials: true
});

api.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const { access } = await refreshAccessToken();
        setAccessToken(access);
        originalRequest.headers['Authorization'] = `Bearer ${access}`;
        return api(originalRequest);
      } catch (refreshError) {
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);
```

© 2025 HealthApp API Docs