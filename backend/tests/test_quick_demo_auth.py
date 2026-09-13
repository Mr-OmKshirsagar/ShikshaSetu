"""Regression tests for Quick Demo Access authentication and RBAC."""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.auth.security import verify_password
from app.users import repository


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_demo_accounts_password_hash(client):
    """Verify that all demo personas have valid password hashes for Password123! in the database."""
    db = app.state.database
    demo_emails = [
        "official@shikshasetu.gov.in",
        "trainer@shikshasetu.gov.in",
        "admin@shikshasetu.gov.in",
        "edu.officer@shikshasetu.gov.in",
    ]
    for email in demo_emails:
        user = repository.get_user_by_email(db, email)
        assert user is not None, f"Demo user {email} must exist in database"
        assert verify_password("Password123!", user.get("password_hash", "")), (
            f"Password123! must verify against password_hash for {email}"
        )
        assert not verify_password("WrongPassword123!", user.get("password_hash", "")), (
            f"Wrong password must not verify for {email}"
        )


def test_admin_quick_login_flow(client):
    """Verify that MoSPI Admin logs in with Password123! and receives ADMIN access_role."""
    res = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@shikshasetu.gov.in", "password": "Password123!"},
    )
    assert res.status_code == 200, f"Admin login failed: {res.text}"
    data = res.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    user = data["user"]
    assert user["email"] == "admin@shikshasetu.gov.in"
    assert user["access_role"] == "ADMIN"

    # Verify that admin token can access /admin/dashboard
    token = data["access_token"]
    dash_res = client.get(
        "/api/v1/admin/dashboard",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert dash_res.status_code == 200, f"Admin dashboard request failed: {dash_res.text}"
    dash_data = dash_res.json()
    assert "total_officials" in dash_data
    assert "total_users" in dash_data


def test_official_and_trainer_quick_login_flow(client):
    """Verify that Statistical Officer and NSSTA Trainer quick logins work and produce correct roles."""
    # Official
    off_res = client.post(
        "/api/v1/auth/login",
        json={"email": "official@shikshasetu.gov.in", "password": "Password123!"},
    )
    assert off_res.status_code == 200
    off_data = off_res.json()
    assert off_data["user"]["access_role"] == "OFFICIAL"

    # Trainer
    trn_res = client.post(
        "/api/v1/auth/login",
        json={"email": "trainer@shikshasetu.gov.in", "password": "Password123!"},
    )
    assert trn_res.status_code == 200
    trn_data = trn_res.json()
    assert trn_data["user"]["access_role"] == "TRAINER"


def test_non_admin_cannot_access_admin_dashboard(client):
    """Verify RBAC: Official and Trainer tokens are rejected by /admin/dashboard with 403."""
    off_res = client.post(
        "/api/v1/auth/login",
        json={"email": "official@shikshasetu.gov.in", "password": "Password123!"},
    )
    off_token = off_res.json()["access_token"]

    dash_res = client.get(
        "/api/v1/admin/dashboard",
        headers={"Authorization": f"Bearer {off_token}"},
    )
    assert dash_res.status_code == 403, "Official token must be rejected from admin dashboard"

    trn_res = client.post(
        "/api/v1/auth/login",
        json={"email": "trainer@shikshasetu.gov.in", "password": "Password123!"},
    )
    trn_token = trn_res.json()["access_token"]

    trn_dash_res = client.get(
        "/api/v1/admin/dashboard",
        headers={"Authorization": f"Bearer {trn_token}"},
    )
    assert trn_dash_res.status_code == 403, "Trainer token must be rejected from admin dashboard"
