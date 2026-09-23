"""
Seed script for initial Government Talent & Opportunity Network opportunities.
Creates realistic sample opportunities for MoSPI and allied departments
and provisions demo user talent preferences for seamless discovery testing.
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.config import get_settings
from app.core.database import initialize_database, close_database
from app.talent.models import OpportunityType, OpportunityStatus, VisibilityLevel


SAMPLE_OPPORTUNITIES = [
    {
        "title": "Senior Trainer — Statistical Sampling & Estimation Methodology",
        "description": "National Statistical Systems Training Academy (NSSTA) requires experienced Statistical Officers to serve as certified faculty trainers for the upcoming national probability sampling capacity-building initiative.",
        "department_name": "Ministry of Statistics & Programme Implementation (MoSPI)",
        "ministry_name": "Ministry of Statistics & Programme Implementation",
        "opportunity_type": OpportunityType.TRAINER,
        "location": "NSSTA Greater Noida / Hybrid",
        "is_remote": True,
        "required_roles": ["Statistical Officer", "Senior Statistical Officer (SSO)", "Junior Statistical Officer (JSO)", "Senior Faculty & Trainer"],
        "required_designations": ["Statistical Officer", "Senior Statistical Officer", "Junior Statistical Officer", "Senior Faculty & Trainer"],
        "required_competencies": [
            {
                "competency_code": "STAT_SAMPLING",
                "minimum_level": 2.0,
                "importance": 1.0
            },
            {
                "competency_code": "STAT_SURVEY_DESIGN",
                "minimum_level": 2.0,
                "importance": 0.85
            }
        ],
        "minimum_experience_years": 2,
        "status": OpportunityStatus.PUBLISHED,
        "start_date": datetime.utcnow() + timedelta(days=15),
        "end_date": datetime.utcnow() + timedelta(days=45),
        "application_deadline": datetime.utcnow() + timedelta(days=10),
        "created_by": "000000000000000000000001",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "published_at": datetime.utcnow()
    },
    {
        "title": "Subject Matter Expert — National Socio-Economic Sample Surveys",
        "description": "Expert advisory panel for quality audit, sampling frame validation, and field questionnaire reviews across central socio-economic statistical surveys.",
        "department_name": "Ministry of Statistics & Programme Implementation (MoSPI)",
        "ministry_name": "Ministry of Statistics & Programme Implementation",
        "opportunity_type": OpportunityType.SUBJECT_MATTER_EXPERT,
        "location": "New Delhi / Remote",
        "is_remote": True,
        "required_roles": ["Statistical Officer", "Senior Statistical Officer (SSO)", "Senior Faculty & Trainer"],
        "required_designations": ["Statistical Officer", "Senior Statistical Officer", "Senior Faculty & Trainer"],
        "required_competencies": [
            {
                "competency_code": "STAT_DATA_QUALITY_FRAMEWORKS",
                "minimum_level": 2.0,
                "importance": 1.0
            },
            {
                "competency_code": "STAT_SAMPLING",
                "minimum_level": 2.0,
                "importance": 0.90
            }
        ],
        "minimum_experience_years": 2,
        "status": OpportunityStatus.PUBLISHED,
        "start_date": datetime.utcnow() + timedelta(days=20),
        "end_date": datetime.utcnow() + timedelta(days=90),
        "application_deadline": datetime.utcnow() + timedelta(days=14),
        "created_by": "000000000000000000000001",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "published_at": datetime.utcnow()
    },
    {
        "title": "Faculty Mentor — Field Survey Quality & Digital Data Capture",
        "description": "Mentorship programme to guide junior field staff on tablet-based survey enumeration (CAPI), non-sampling error reduction, and field supervision.",
        "department_name": "Ministry of Statistics & Programme Implementation (MoSPI)",
        "ministry_name": "Ministry of Statistics & Programme Implementation",
        "opportunity_type": OpportunityType.MENTOR,
        "location": "Regional Training Centres",
        "is_remote": False,
        "required_roles": ["Statistical Officer", "Junior Statistical Officer (JSO)", "Senior Faculty & Trainer"],
        "required_designations": ["Statistical Officer", "Junior Statistical Officer", "Senior Faculty & Trainer"],
        "required_competencies": [
            {
                "competency_code": "STAT_SURVEY_DESIGN",
                "minimum_level": 2.0,
                "importance": 1.0
            }
        ],
        "minimum_experience_years": 1,
        "status": OpportunityStatus.PUBLISHED,
        "start_date": datetime.utcnow() + timedelta(days=30),
        "end_date": datetime.utcnow() + timedelta(days=60),
        "application_deadline": datetime.utcnow() + timedelta(days=20),
        "created_by": "000000000000000000000001",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "published_at": datetime.utcnow()
    },
    {
        "title": "Master Trainer — Land Records Modernization & Mutation Workflows",
        "description": "State Administrative Training Institute requires experienced revenue officials to train grassroots administrative staff on automated mutation registries and digitised land records.",
        "department_name": "Department of Revenue & Land Records",
        "ministry_name": "Ministry of Revenue",
        "opportunity_type": OpportunityType.TRAINER,
        "location": "State Administrative Institute",
        "is_remote": False,
        "required_roles": ["Talathi", "Revenue Inspector"],
        "required_designations": ["Talathi", "Revenue Inspector"],
        "required_competencies": [
            {
                "competency_code": "REV_LAND_RECORDS",
                "minimum_level": 2.0,
                "importance": 1.0
            }
        ],
        "minimum_experience_years": 2,
        "status": OpportunityStatus.PUBLISHED,
        "start_date": datetime.utcnow() + timedelta(days=15),
        "end_date": datetime.utcnow() + timedelta(days=45),
        "application_deadline": datetime.utcnow() + timedelta(days=10),
        "created_by": "000000000000000000000001",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "published_at": datetime.utcnow()
    }
]


def seed_talent_opportunities():
    settings = get_settings()
    client, db = initialize_database(settings.mongodb_uri, settings.mongodb_database)
    try:
        print("[CLEANUP] Removing test / garbage opportunities (e.g. mjm)...")
        del_res = db.government_opportunities.delete_many({
            "$or": [
                {"title": {"$regex": "^mjm", "$options": "i"}},
                {"title": {"$regex": "test", "$options": "i"}},
                {"description": {"$regex": "m b,n,", "$options": "i"}}
            ]
        })
        print(f"  - Deleted {del_res.deleted_count} test opportunities.")

        print("[SEED] Seeding government opportunities...")
        for opp in SAMPLE_OPPORTUNITIES:
            existing = db.government_opportunities.find_one({"title": opp["title"]})
            if not existing:
                db.government_opportunities.insert_one(opp)
                print(f"  + Created opportunity: {opp['title']}")
            else:
                # Update with current required roles and competencies
                db.government_opportunities.update_one(
                    {"_id": existing["_id"]},
                    {"$set": {
                        "required_roles": opp["required_roles"],
                        "required_designations": opp["required_designations"],
                        "required_competencies": opp["required_competencies"],
                        "department_name": opp["department_name"],
                        "opportunity_type": opp["opportunity_type"],
                        "status": OpportunityStatus.PUBLISHED
                    }}
                )
                print(f"  = Updated opportunity: {opp['title']}")

        # Provision Talent Preferences for demo users so they match
        print("[SEED] Provisioning demo users with opt-in talent preferences...")
        demo_emails = [
            {
                "email": "official@shikshasetu.gov.in",
                "prefs": {
                    "opt_in_enabled": True,
                    "available_for_opportunities": True,
                    "visibility_level": VisibilityLevel.AUTHORIZED_DEPARTMENTS,
                    "authorized_departments": [
                        "Ministry of Statistics & Programme Implementation (MoSPI)",
                        "National Statistical Systems Training Academy (NSSTA)",
                        "Department of Revenue & Land Records"
                    ],
                    "opportunity_types": [
                        OpportunityType.TRAINER,
                        OpportunityType.MENTOR,
                        OpportunityType.SUBJECT_MATTER_EXPERT,
                        OpportunityType.WORKSHOP,
                        OpportunityType.CAPACITY_BUILDING,
                        OpportunityType.ADVISORY,
                        OpportunityType.KNOWLEDGE_SHARING
                    ],
                    "updated_at": datetime.utcnow()
                }
            },
            {
                "email": "trainer@shikshasetu.gov.in",
                "prefs": {
                    "opt_in_enabled": True,
                    "available_for_opportunities": True,
                    "visibility_level": VisibilityLevel.AUTHORIZED_DEPARTMENTS,
                    "authorized_departments": [
                        "Ministry of Statistics & Programme Implementation (MoSPI)",
                        "National Statistical Systems Training Academy (NSSTA)"
                    ],
                    "opportunity_types": [
                        OpportunityType.TRAINER,
                        OpportunityType.MENTOR,
                        OpportunityType.WORKSHOP,
                        OpportunityType.CAPACITY_BUILDING
                    ],
                    "updated_at": datetime.utcnow()
                }
            }
        ]

        for item in demo_emails:
            u = db.users.find_one({"email": item["email"]})
            if u:
                db.talent_preferences.update_one(
                    {"user_id": u["_id"]},
                    {"$set": item["prefs"]},
                    upsert=True
                )
                print(f"  + Opted in demo user: {item['email']} ({u.get('full_name')})")

        print("[SEED] Government Talent & Opportunity Network seed complete.")
    finally:
        close_database(client)


if __name__ == "__main__":
    seed_talent_opportunities()
