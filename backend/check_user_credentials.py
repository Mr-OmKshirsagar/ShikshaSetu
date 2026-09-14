"""Check if user credentials exist in the database."""
import sys
from pymongo import MongoClient
from app.auth.security import verify_password
from app.core.config import get_settings

def check_user(email: str, password: str):
    """Check if user with given credentials exists."""
    settings = get_settings()
    
    print("=" * 70)
    print("USER CREDENTIALS CHECK")
    print("=" * 70)
    print(f"Email: {email}")
    print(f"Database: {settings.mongodb_uri.split('@')[1] if '@' in settings.mongodb_uri else 'local'}")
    print()
    
    # Connect to MongoDB
    try:
        client = MongoClient(settings.mongodb_uri)
        db = client[settings.mongodb_database]
        
        # Find user by email (case-insensitive)
        user = db.users.find_one({"email": {"$regex": f"^{email}$", "$options": "i"}})
        
        if not user:
            print("❌ USER NOT FOUND")
            print(f"   No user with email: {email}")
            print()
            print("📋 Available TRAINER users in database:")
            print("-" * 70)
            
            trainers = db.users.find({"access_role": "TRAINER"})
            trainer_count = 0
            for trainer in trainers:
                trainer_count += 1
                print(f"{trainer_count}. {trainer.get('full_name', 'N/A')}")
                print(f"   Email: {trainer.get('email')}")
                print(f"   Employee ID: {trainer.get('employee_id', 'N/A')}")
                print(f"   Status: {trainer.get('status', 'N/A')}")
                print()
            
            if trainer_count == 0:
                print("   No TRAINER users found!")
                print()
                print("💡 Available users by role:")
                all_users = db.users.find().limit(10)
                for idx, u in enumerate(all_users, 1):
                    print(f"   {idx}. {u.get('email')} - {u.get('access_role')} - {u.get('full_name')}")
            
            return False
        
        print("✅ USER FOUND")
        print(f"   Name: {user.get('full_name')}")
        print(f"   Email: {user.get('email')}")
        print(f"   Role: {user.get('access_role')}")
        print(f"   Status: {user.get('status')}")
        print(f"   Employee ID: {user.get('employee_id', 'N/A')}")
        print()
        
        # Check if user is active
        if user.get('status') != 'active':
            print("❌ USER IS NOT ACTIVE")
            print(f"   Status: {user.get('status')}")
            return False
        
        # Verify password
        print("🔐 Checking password...")
        password_hash = user.get('password_hash', '')
        
        if verify_password(password, password_hash):
            print("✅ PASSWORD CORRECT")
            print()
            print("=" * 70)
            print("✅ CREDENTIALS ARE VALID")
            print("=" * 70)
            print()
            print("You can login with:")
            print(f"  Email: {user.get('email')}")
            print(f"  Password: {password}")
            return True
        else:
            print("❌ PASSWORD INCORRECT")
            print()
            print("💡 The user exists but the password doesn't match.")
            print("   You may need to reset the password or use the correct one.")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        client.close()


if __name__ == "__main__":
    # Default credentials from the screenshot
    email = "trainer@shikshasetu.gov.in"
    password = "Password@123"
    
    if len(sys.argv) > 1:
        email = sys.argv[1]
    if len(sys.argv) > 2:
        password = sys.argv[2]
    
    check_user(email, password)
