# API Guide

The Provider MDM solution includes a FastAPI-based service to perform real-time provider matching against the graph database.

## 1. Starting the API

The API service is part of the Docker Compose stack. It starts automatically on port **8000**.

```bash
docker compose up -d
```

Check if it's running:
```bash
docker logs -f provider-api
```

## 2. API Documentation (Swagger UI)

Once running, you can access the interactive API documentation at:
**http://localhost:8000/docs**

## 3. Endpoints

### `POST /match`

Matches an incoming provider record against existing providers in the graph.

**Request Body** (`Provider` JSON):

Required fields: `npi`, `first_name`, `last_name`.
Optional fields: `email`, `phone`, `license_number`.

**Example Request:**

```bash
curl -X POST "http://localhost:8000/match" \
     -H "Content-Type: application/json" \
     -d '{
           "npi": "1234567890",
           "first_name": "Bob",
           "last_name": "Smith",
           "email": "bob.smith@hospital.org",
           "phone": "+15551234567"
         }'
```

**Response Example:**

Returns a list of potential matches, sorted by score (highest first).

```json
[
  {
    "provider1_npi": "1234567890",
    "provider2_npi": "1234567890",
    "match_score": 0.95,
    "match_type": "high",
    "matching_attributes": [
      "npi",
      "name",
      "email"
    ],
    "confidence_level": "high",
    "recommended_action": "merge"
  }
]
```

### `GET /health`

Health check endpoint.

```bash
curl http://localhost:8000/health
# {"status": "ok"}
```

## 4. Running Verification Test

A Python script is provided to verify the API functionality:

```bash
uv run tests/test_api.py
```
