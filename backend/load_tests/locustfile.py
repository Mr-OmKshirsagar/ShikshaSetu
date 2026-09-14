"""
Locust load-testing suite for ShikshaSetu SIH 2026 prototype.
Defines realistic user personas with realistic think times (1-3s).
Tokens are acquired at test start to respect the 10/min SlowAPI login rate limiter.
"""

import json
import logging
import requests
from locust import HttpUser, task, between, events

logger = logging.getLogger("locust_shikshasetu")

# Cache tokens across virtual users within the Locust process
AUTH_TOKENS = {
    "OFFICIAL": None,
    "TRAINER": None,
    "ADMIN": None,
}

PERSONA_CREDENTIALS = {
    "OFFICIAL": ("official@shikshasetu.gov.in", "Password123!"),
    "TRAINER": ("trainer@shikshasetu.gov.in", "Password123!"),
    "ADMIN": ("admin@shikshasetu.gov.in", "Password123!"),
}


def acquire_token(host: str, role: str) -> str:
    """Acquires and caches a JWT for a demo role."""
    if AUTH_TOKENS[role]:
        return AUTH_TOKENS[role]
    email, pwd = PERSONA_CREDENTIALS[role]
    login_url = f"{host.rstrip('/')}/api/v1/auth/login"
    res = requests.post(login_url, json={"email": email, "password": pwd}, timeout=15)
    if res.status_code != 200:
        raise RuntimeError(f"Authentication failed for {role} ({email}): {res.status_code} {res.text}")
    token = res.json()["access_token"]
    AUTH_TOKENS[role] = token
    return token


# ==============================================================================
# SCENARIO A: OFFICIAL LEARNER (Weight: 70)
# ==============================================================================

class OfficialUser(HttpUser):
    weight = 70
    wait_time = between(1.0, 3.0)

    def on_start(self):
        token = acquire_token(self.host, "OFFICIAL")
        self.headers = {"Authorization": f"Bearer {token}"}

    @task(4)
    def view_dashboard(self):
        """Simulates an Official reviewing their core competency profile & recommendations."""
        self.client.get("/api/v1/competencies/me", headers=self.headers, name="/competencies/me")
        self.client.get("/api/v1/skill-gaps/me", headers=self.headers, name="/skill-gaps/me")
        self.client.get("/api/v1/recommendations/me", headers=self.headers, name="/recommendations/me")

    @task(3)
    def view_learning_pathways(self):
        """Simulates browsing iGOT courses and assigned assessments."""
        self.client.get("/api/v1/learning-activities", headers=self.headers, name="/learning-activities")
        self.client.get("/api/v1/quizzes/assigned", headers=self.headers, name="/quizzes/assigned")
        self.client.get("/api/v1/igot/courses", headers=self.headers, name="/igot/courses")

    @task(1)
    def view_profile(self):
        """Simulates viewing profile details."""
        self.client.get("/api/v1/users/me", headers=self.headers, name="/users/me")


# ==============================================================================
# SCENARIO B: NSSTA TRAINER (Weight: 20)
# ==============================================================================

class TrainerUser(HttpUser):
    weight = 20
    wait_time = between(1.5, 3.5)

    def on_start(self):
        token = acquire_token(self.host, "TRAINER")
        self.headers = {"Authorization": f"Bearer {token}"}

    @task(3)
    def view_trainer_dashboard(self):
        """Reviews studio metrics, materials count, and recent activity."""
        self.client.get("/api/v1/trainer/dashboard", headers=self.headers, name="/trainer/dashboard")

    @task(2)
    def inspect_materials_and_questions(self):
        """Reviews curriculum materials and question bank."""
        self.client.get("/api/v1/trainer/materials", headers=self.headers, name="/trainer/materials")
        self.client.get("/api/v1/trainer/questions", headers=self.headers, name="/trainer/questions")
        self.client.get("/api/v1/trainer/quizzes", headers=self.headers, name="/trainer/quizzes")

    @task(1)
    def inspect_learners(self):
        """Inspects learner cohort progress and attempts."""
        self.client.get("/api/v1/trainer/learners", headers=self.headers, name="/trainer/learners")


# ==============================================================================
# SCENARIO C: MOSPI ADMIN (Weight: 10)
# ==============================================================================

class AdminUser(HttpUser):
    weight = 10
    wait_time = between(2.0, 4.0)

    def on_start(self):
        token = acquire_token(self.host, "ADMIN")
        self.headers = {"Authorization": f"Bearer {token}"}

    @task(3)
    def view_admin_dashboard(self):
        """Monitors workforce competency health and executive metrics."""
        self.client.get("/api/v1/admin/dashboard", headers=self.headers, name="/admin/dashboard")

    @task(2)
    def view_workforce_distribution(self):
        """Inspects department workforce distribution."""
        self.client.get("/api/v1/admin/workforce", headers=self.headers, name="/admin/workforce")

    @task(1)
    def view_competency_analytics(self):
        """Reviews organization-wide competency analytics and gaps."""
        self.client.get("/api/v1/admin/competencies", headers=self.headers, name="/admin/competencies")
        self.client.get("/api/v1/admin/skill-gaps", headers=self.headers, name="/admin/skill-gaps")
