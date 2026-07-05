from fastapi.testclient import TestClient

from backend.app.main import app


def run() -> None:
    client = TestClient(app)
    assert client.get("/api/health").status_code == 200
    login = client.post("/api/auth/login", json={"email": "arjun@voltnav.demo", "password": "voltnav123"})
    assert login.status_code == 200, login.text
    token = login.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    meta = client.get("/api/meta").json()
    assert "Tata Nexon EV Max" in meta["vehicles"]
    trip = client.post("/api/trips/plan", headers=headers, json={}).json()
    assert trip["distance_km"] > 300
    assert "prediction" in trip
    assert client.get("/api/analytics/summary", headers=headers).status_code == 200
    pdf = client.get(f"/api/trips/{trip['id']}/pdf", headers=headers)
    assert pdf.status_code == 200
    assert pdf.content.startswith(b"%PDF")
    print("VoltNav API checks passed")


if __name__ == "__main__":
    run()
