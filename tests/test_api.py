from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


# -------------------------------------------------
# Health Check
# -------------------------------------------------

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert data["agent"] == "ready"
    assert isinstance(data["tools"], list)


# -------------------------------------------------
# Chat API – List Query
# -------------------------------------------------

def test_chat_list_query():
    payload = {
        "query": "Which initiatives in 2024 are related to breastfeeding support?"
    }

    response = client.post("/api/chat", json=payload)
    assert response.status_code == 200

    data = response.json()

    assert data["tool"] == "list"
    assert "results" in data
    assert isinstance(data["results"], list)
    assert len(data["results"]) > 0


# -------------------------------------------------
# Chat API – Aggregation Query
# -------------------------------------------------

def test_chat_aggregation_query():
    payload = {
        "query": "Count initiatives by classification level"
    }

    response = client.post("/api/chat", json=payload)
    assert response.status_code == 200

    data = response.json()

    assert data["tool"] == "aggregation"
    assert "results" in data
    assert isinstance(data["results"], list)

    # Validate aggregation shape
    first_row = data["results"][0]
    assert "CLASSIFICATION_LEVEL" in first_row
    assert "count" in first_row


# -------------------------------------------------
# Chat API – Invalid Query (Error Path)
# -------------------------------------------------

def test_chat_invalid_query():
    payload = {
        "query": "Do aggregation on non existing column foo bar"
    }

    response = client.post("/api/chat", json=payload)

    # Error must be controlled (no 500 stack trace)
    assert response.status_code in (400, 422)

    data = response.json()
    assert "detail" in data


# -------------------------------------------------
# Chat API – Empty Input
# -------------------------------------------------

def test_chat_empty_query():
    payload = {
        "query": ""
    }

    response = client.post("/api/chat", json=payload)
    assert response.status_code in (400, 422)
