from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_generate_validate_flow():
    payload = {
        "seed": "abc",
        "request_id": "req-1",
        "name_uniqueness_required": True,
    }
    r = client.post("/generateTechnique", json=payload)
    assert r.status_code == 200
    data = r.json()
    md = data["machine_data"]
    human = data["human_text"]

    r2 = client.post("/validateTechnique", json={"machine_data": md, "human_text": human})
    assert r2.status_code == 200
    vrep = r2.json()
    assert "score" in vrep

    if vrep["pass"]:
        r3 = client.post("/finalizeTechnique", json={"machine_data": md, "human_text": human, "attempts_history": [vrep]})
        assert r3.status_code == 200
        f = r3.json()
        assert f["ingestion_ready"] in [True, False]


def test_ingest_contract():
    payload = {
        "seed": "abc",
        "request_id": "req-2",
        "name_uniqueness_required": True,
    }
    r = client.post("/generateTechnique", json=payload)
    data = r.json()
    env = {"machine_data": data["machine_data"], "human_text": data["human_text"]}
    r2 = client.post("/ingestTechnique", json=env)
    assert r2.status_code == 200
    j = r2.json()
    assert "ingestion_log_id" in j