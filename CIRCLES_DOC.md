
# Circles Feature - Complete System README & API Documentation

---

## Introduction

Welcome to the Circles feature! This document explains everything you need to understand and build the frontend for the Circles system, as well as use the backend API endpoints effectively.

This README is designed for both developers and non-technical readers to get a full grasp of the feature.

---

## How the Circles System Works

The Circles system allows users to create or join groups called “circles” where members contribute a fixed amount of money regularly (weekly or monthly). Members can also file claims to withdraw from the circle’s collective balance.

### Core Concepts

- **Circle**: A group with a name, description, fixed contribution amount, contribution frequency, and balance.
- **Membership**: Represents a user’s participation in a circle, tracking join date, payment history, and status.
- **Contribution**: Each payment made by a member into the circle.
- **Claim**: A request by a member to withdraw money from the circle, subject to validation and approval.
- **Wallet & Transactions**: Each user has a wallet tracking their available funds. Contributions and claims move money between wallets and circles.
- **Claim Lock Period**: New members must wait a certain number of days before filing claims.
- **Automatic Contributions**: The system automatically deducts contributions based on frequency and user wallet balance.
- **AI Validation**: Claims are checked using AI (OpenAI GPT) for legitimacy and fraud detection.

---

## Data Flow Summary

1. **User creates or joins a circle**. Creator is automatically added as a member.
2. **Members contribute a fixed amount regularly** (weekly/monthly). Contributions update user wallet and circle balance.
3. **System enforces contributions automatically** via a background task.
4. **Members can file claims to withdraw funds**, which undergo multiple validations including AI fraud checks.
5. **Approved claims transfer funds** from the circle balance back to the user wallet.
6. **Members with unpaid contributions receive warnings and can be removed and refunded.**

---

## Backend API Endpoints

Base URL: `/api/circles/`

| Endpoint                         | Method | Description                                    |
|---------------------------------|--------|------------------------------------------------|
| `/`                             | GET    | List all circles user belongs to                |
| `/`                             | POST   | Create a new circle                             |
| `/<int:pk>/`                    | GET    | Retrieve details of a specific circle          |
| `/<int:pk>/`                    | PUT/PATCH | Update or delete a specific circle            |
| `/<int:circle_id>/members/`     | GET    | List members of a circle                        |
| `/<int:circle_id>/contribute/`  | POST   | Submit a contribution to a circle               |
| `/<int:circle_id>/claim/`       | POST   | File a claim for withdrawal from a circle      |

---

## Detailed Endpoint Usage with React Router Integration

### 1. List & Create Circles

- **URL:** `/api/circles/`
- **GET:** List all circles user is a member of.
- **POST:** Create a new circle. User becomes creator and member.

#### Example React usage:

```jsx
// Fetch all circles
useEffect(() => {
  fetch('/api/circles/', {
    method: 'GET',
    headers: { 'Authorization': `Bearer ${token}` }
  })
  .then(res => res.json())
  .then(data => setCircles(data))
  .catch(console.error);
}, []);

// Create a new circle
const createCircle = async (circleData) => {
  const response = await fetch('/api/circles/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(circleData)
  });
  if (response.ok) {
    const newCircle = await response.json();
    setCircles(prev => [...prev, newCircle]);
  } else {
    const error = await response.json();
    alert(`Error: ${JSON.stringify(error)}`);
  }
};
```

#### Possible responses:

- **Success (GET):** Array of circle objects with members, contributions, claims embedded.
- **Success (POST):** Newly created circle object.
- **Error:** Authentication error or validation error if required fields missing.

---

### 2. Circle Details, Update, Delete

- **URL:** `/api/circles/:circleId/` (replace `:circleId` with actual ID)
- **Methods:** GET, PUT, PATCH, DELETE

#### Example React usage:

```jsx
// Fetch details for circle with ID 5
useEffect(() => {
  fetch(`/api/circles/${circleId}/`, {
    headers: { 'Authorization': `Bearer ${token}` }
  })
  .then(res => res.json())
  .then(setCircleDetails)
  .catch(console.error);
}, [circleId]);
```

- Update and delete operations are similar, using PUT/PATCH and DELETE methods respectively.

---

### 3. List Members of a Circle

- **URL:** `/api/circles/:circleId/members/`
- **Method:** GET

#### React example:

```jsx
fetch(`/api/circles/${circleId}/members/`, {
  headers: { 'Authorization': `Bearer ${token}` }
})
.then(res => res.json())
.then(setMembers)
.catch(console.error);
```

---

### 4. Contribute to a Circle

- **URL:** `/api/circles/:circleId/contribute/`
- **Method:** POST

- The amount is fixed per circle; no need to pass it in the request body.

#### React example:

```jsx
const contribute = async () => {
  const response = await fetch(`/api/circles/${circleId}/contribute/`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` }
  });
  if (response.ok) {
    alert('Contribution successful!');
  } else {
    const error = await response.json();
    alert(`Error: ${JSON.stringify(error)}`);
  }
};
```

---

### 5. File a Claim

- **URL:** `/api/circles/:circleId/claim/`
- **Method:** POST
- **Body:** JSON with `amount` (decimal), `reason` (string), optionally a `receipt` file upload (multipart/form-data required).

#### React example (using fetch with FormData for file upload):

```jsx
const fileClaim = async (amount, reason, receiptFile) => {
  const formData = new FormData();
  formData.append('amount', amount);
  formData.append('reason', reason);
  if (receiptFile) formData.append('receipt', receiptFile);

  const response = await fetch(`/api/circles/${circleId}/claim/`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
    body: formData,
  });
  if (response.ok) {
    alert('Claim filed successfully!');
  } else {
    const error = await response.json();
    alert(`Error: ${JSON.stringify(error)}`);
  }
};
```

---

## Frontend Pages / Components To Build

| Page/Component Name    | Route                        | Purpose / Functionality                                   |
|-----------------------|------------------------------|----------------------------------------------------------|
| **CirclesList**       | `/circles`                   | Show all circles user belongs to; button to create new. |
| **CircleDetail**      | `/circles/:circleId`         | Show circle info, contributions, claims summary.         |
| **CircleMembers**     | `/circles/:circleId/members` | List all active members of the circle.                    |
| **ContributionForm**  | Integrated in CircleDetail   | Submit contribution to circle.                            |
| **ClaimForm**         | Integrated in CircleDetail   | Submit claim with amount, reason, and optional receipt.  |

- Use React Router `<Route path="/circles/:circleId" ... />` to navigate between pages.
- Store and pass `circleId` via URL params for API calls.
- Handle API errors gracefully with alerts or UI messages.

---

## Important Notes

- **Authentication:** All endpoints require JWT Bearer tokens in `Authorization` header.
- **API Errors:** Pay attention to 400/401/403/404 responses and show appropriate messages.
- **Automatic Contributions:** The backend runs a Celery task enforcing automatic deductions; frontend does not trigger this.
- **Claim Validation:** Claims are validated both by business logic and AI-powered fraud checks.
- **Data Format:** Use JSON for most POST bodies, except for file uploads (use multipart/form-data).

---

## Summary

This documentation equips frontend developers with everything needed to build, connect, and interact with the Circles backend API. It also explains the full system concept for any stakeholder to understand how the Circles feature functions end-to-end.

Feel free to extend and customize UI components, add notifications, or improve error handling as needed.

---

## 👨‍💻 Maintainer


© 2025 HealthHalo API Docs

