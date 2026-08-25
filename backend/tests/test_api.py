from tests.conftest import client, login


def test_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    body = res.json()
    assert body["api"] == "healthy"
    assert body["database"] == "healthy"
    assert "data_mode" in body


def test_latest_energy():
    res = client.get("/api/energy/latest")
    assert res.status_code == 200
    assert isinstance(res.json(), list)
    assert len(res.json()) >= 1


def test_summary_uses_period_window():
    a = client.get("/api/summary", params={"period": "24h"}).json()
    b = client.get("/api/summary", params={"period": "7d"}).json()
    assert a["period"] == "24h"
    assert "start" in a and "end" in a
    assert b["total_energy_kwh"] >= a["total_energy_kwh"]
    assert "co2_factor_kg_per_kwh" in a


def test_invalid_department():
    res = client.get("/api/energy/trend/XYZ")
    assert res.status_code == 404


def test_invalid_period():
    res = client.get("/api/summary", params={"period": "2y"})
    assert res.status_code == 400


def test_authentication_success_and_failure():
    ok = client.post("/api/auth/login", json={"email": "admin@psit.ac.in", "password": "admin123"})
    assert ok.status_code == 200
    bad = client.post("/api/auth/login", json={"email": "admin@psit.ac.in", "password": "nope"})
    assert bad.status_code == 401


def test_permissions_admin_vs_viewer():
    viewer = login("viewer@psit.ac.in", "viewer123")
    res = client.post("/api/simulator/anomaly", headers={"Authorization": f"Bearer {viewer}"})
    assert res.status_code == 403
    admin = login()
    res = client.post("/api/simulator/anomaly?department=ME", headers={"Authorization": f"Bearer {admin}"})
    assert res.status_code == 200
    assert res.json()["event"]["anomaly"] is not None


def test_anomaly_detection_endpoint():
    admin = login()
    client.post("/api/simulator/anomaly?department=ME", headers={"Authorization": f"Bearer {admin}"})
    res = client.get("/api/anomalies")
    assert res.status_code == 200
    rows = res.json()
    assert len(rows) >= 1
    assert "reason" in rows[0]
    assert rows[0]["reason"] != "Anomaly detected."


def test_green_score_normalized():
    res = client.get("/api/scores")
    assert res.status_code == 200
    rows = res.json()
    assert len(rows) == 7
    for r in rows:
        assert 0 <= r["total_score"] <= 99
        assert "kwh_per_student" in r
        assert "kwh_per_sqm" in r
        assert "energy_efficiency" in r


def test_forecasting():
    res = client.get("/api/forecasts", params={"department": "CSE"})
    assert res.status_code == 200
    rows = res.json()
    assert len(rows) >= 1
    assert "predicted_kwh" in rows[0]
    assert "lower_bound" in rows[0]
    assert "upper_bound" in rows[0]


def test_device_status():
    res = client.get("/api/devices/status")
    assert res.status_code == 200
    body = res.json()
    assert "counts" in body
    assert len(body["devices"]) >= 7 * 5


def test_dashboard():
    res = client.get("/api/dashboard")
    assert res.status_code == 200
    body = res.json()
    assert "summary" in body
    assert body["campus"]
