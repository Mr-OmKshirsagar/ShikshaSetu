"""
Test script to assign a quiz and trigger email notification.
This will assign an existing quiz to a learner and verify email is sent.
"""

import requests
import json
from datetime import datetime

# API Configuration
BASE_URL = "http://localhost:8000/api/v1"

def login(email: str, password: str) -> str:
    """Login and get JWT token."""
    print(f"🔐 Logging in as {email}...")
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": email, "password": password}
    )
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print(f"✅ Login successful!")
        return token
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return None


def get_trainer_quizzes(token: str) -> list:
    """Get all quizzes for the trainer."""
    print("\n📚 Fetching trainer quizzes...")
    response = requests.get(
        f"{BASE_URL}/trainer/quizzes",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        quizzes = response.json()
        print(f"✅ Found {len(quizzes)} quizzes")
        return quizzes
    else:
        print(f"❌ Failed to fetch quizzes: {response.status_code}")
        return []


def get_learners(token: str) -> list:
    """Get list of learners from the system."""
    print("\n👥 Fetching learners...")
    
    # Try to get admin users list (if available)
    response = requests.get(
        f"{BASE_URL}/admin/users",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        users = response.json().get("users", [])
        # Filter for OFFICIALs (learners)
        learners = [u for u in users if u.get("access_role") == "OFFICIAL"]
        print(f"✅ Found {len(learners)} learners")
        return learners
    else:
        print(f"⚠️  Could not fetch users (not admin). Will use manual learner ID.")
        return []


def assign_quiz(token: str, quiz_id: str, learner_ids: list[str]) -> dict:
    """Assign a quiz to learners and trigger email notification."""
    print(f"\n📧 Assigning quiz {quiz_id} to {len(learner_ids)} learner(s)...")
    print(f"   Learner IDs: {learner_ids}")
    
    response = requests.post(
        f"{BASE_URL}/trainer/quizzes/{quiz_id}/assign",
        headers={"Authorization": f"Bearer {token}"},
        json={"learner_ids": learner_ids}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Quiz assigned successfully!")
        print(f"   {result['message']}")
        return result
    else:
        print(f"❌ Failed to assign quiz: {response.status_code}")
        print(f"   Response: {response.text}")
        return None


def main():
    print("=" * 70)
    print("🧪 EMAIL NOTIFICATION TEST - Quiz Assignment")
    print("=" * 70)
    
    # Configuration
    TRAINER_EMAIL = "trainer@test.com"
    TRAINER_PASSWORD = "Password123!"
    
    # Step 1: Login as trainer
    trainer_token = login(TRAINER_EMAIL, TRAINER_PASSWORD)
    if not trainer_token:
        print("\n❌ Cannot proceed without trainer login")
        print("   Make sure you have a trainer account in the database")
        print(f"   Email: {TRAINER_EMAIL}")
        print(f"   Password: {TRAINER_PASSWORD}")
        return
    
    # Step 2: Get trainer's quizzes
    quizzes = get_trainer_quizzes(trainer_token)
    if not quizzes:
        print("\n❌ No quizzes found for this trainer")
        print("   Please create and publish a quiz first via the UI")
        return
    
    # Find a PUBLISHED or ASSIGNED quiz
    available_quiz = None
    for quiz in quizzes:
        if quiz.get("status") in ["PUBLISHED", "ASSIGNED"]:
            available_quiz = quiz
            break
    
    if not available_quiz:
        print("\n❌ No published/assigned quiz found")
        print("   Available quizzes:")
        for q in quizzes:
            print(f"   - {q.get('title')} (Status: {q.get('status')})")
        print("\n   Please publish a quiz first")
        return
    
    print(f"\n✅ Selected quiz: {available_quiz.get('title')}")
    print(f"   Quiz ID: {available_quiz.get('id')}")
    print(f"   Status: {available_quiz.get('status')}")
    print(f"   Description: {available_quiz.get('description', 'No description')}")
    
    # Step 3: Get learners
    learners = get_learners(trainer_token)
    
    if not learners:
        print("\n⚠️  Please enter learner user ID manually:")
        learner_id = input("   Learner User ID: ").strip()
        if not learner_id:
            print("❌ No learner ID provided")
            return
        learner_ids = [learner_id]
    else:
        # Show first 5 learners
        print("\n📋 Available learners:")
        for i, learner in enumerate(learners[:5]):
            print(f"   {i+1}. {learner.get('full_name')} ({learner.get('email')})")
            print(f"      ID: {learner.get('_id')}")
        
        if len(learners) > 5:
            print(f"   ... and {len(learners) - 5} more")
        
        # Select first learner for testing
        selected_learner = learners[0]
        learner_ids = [selected_learner.get("_id")]
        print(f"\n✅ Will assign to: {selected_learner.get('full_name')} ({selected_learner.get('email')})")
    
    # Step 4: Assign quiz and send email
    print("\n" + "=" * 70)
    print("📧 TRIGGERING EMAIL NOTIFICATION")
    print("=" * 70)
    
    result = assign_quiz(trainer_token, available_quiz.get("id"), learner_ids)
    
    if result:
        print("\n" + "=" * 70)
        print("✅ TEST SUCCESSFUL!")
        print("=" * 70)
        print(f"Quiz: {available_quiz.get('title')}")
        print(f"Assigned to: {result.get('assigned_learners_count')} learner(s)")
        print(f"Status: {result.get('status')}")
        print(f"\n📧 {result.get('message')}")
        print("\n🔍 Check the learner's email inbox for the notification!")
        print("   (Don't forget to check spam/junk folder)")
    else:
        print("\n❌ TEST FAILED")
        print("   Check the error messages above")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
