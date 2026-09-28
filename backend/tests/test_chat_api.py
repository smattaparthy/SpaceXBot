import pytest
from fastapi.testclient import TestClient
from openai import OpenAIError
from pinecone.errors import PineconeError

import app.main as main


CHUNKS = [
    {"score": 0.57, "text": "Dragon carries cargo and crew.", "file_name": "dragon_overview.txt", "chunk_id": 0},
    {"score": 0.28, "text": "Falcon 9 is reusable.", "file_name": "falcon9_overview.txt", "chunk_id": 0},
]


@pytest.fixture
def client(monkeypatch):
    calls = {}

    def fake_retrieve(question, top_k):
        calls["retrieve"] = (question, top_k)
        return CHUNKS

    def fake_answer(question, chunks):
        calls["answer"] = (question, chunks)
        return "Dragon is a spacecraft."

    monkeypatch.setattr(main, "retrieve_relevant_chunks", fake_retrieve)
    monkeypatch.setattr(main, "generate_answer", fake_answer)

    test_client = TestClient(main.app)
    test_client.calls = calls
    return test_client


def test_health(client):
    assert client.get("/").status_code == 200


def test_chat_returns_answer_and_sources(client):
    response = client.post("/chat", json={"question": "  What is Dragon?  "})

    assert response.status_code == 200
    assert response.json() == {
        "question": "What is Dragon?",
        "answer": "Dragon is a spacecraft.",
        "sources": [
            {"file_name": "dragon_overview.txt", "chunk_id": 0, "score": 0.57},
            {"file_name": "falcon9_overview.txt", "chunk_id": 0, "score": 0.28},
        ],
    }
    assert client.calls["retrieve"] == ("What is Dragon?", main.RETRIEVAL_TOP_K)
    assert client.calls["answer"] == ("What is Dragon?", CHUNKS)


@pytest.mark.parametrize("payload", [{"question": ""}, {"question": "   "}, {"question": "x" * 1001}, {}])
def test_chat_rejects_invalid_question(client, payload):
    assert client.post("/chat", json=payload).status_code == 422
    assert "retrieve" not in client.calls


@pytest.mark.parametrize("error", [OpenAIError("down"), PineconeError("down")])
def test_chat_retrieval_failure_returns_502(client, monkeypatch, error):
    def failing_retrieve(question, top_k):
        raise error

    monkeypatch.setattr(main, "retrieve_relevant_chunks", failing_retrieve)

    response = client.post("/chat", json={"question": "What is Dragon?"})

    assert response.status_code == 502
    assert response.json()["detail"] == "Could not search the knowledge base. Please try again."


def test_chat_answer_failure_returns_502(client, monkeypatch):
    def failing_answer(question, chunks):
        raise OpenAIError("down")

    monkeypatch.setattr(main, "generate_answer", failing_answer)

    response = client.post("/chat", json={"question": "What is Dragon?"})

    assert response.status_code == 502
    assert response.json()["detail"] == "Could not generate an answer. Please try again."
