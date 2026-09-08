# PHASE 5E — ROLE MIGRATION & AUDIT NOTES

**System:** ShikshaSetu Core Platform  
**Scope:** Civil Service Role Resolution, Competency Mapping & Demo Accounts  
**Date:** 2026-09-06

---

## 1. Audit of Active & Seeded Accounts

We audited the core user accounts across system seeds and integration fixtures:

| Account / Identifier | Department | Designation | Resolved Role | Resolution Method | Dependencies / Risks |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`ap17052005@gmail.com`** (Demo Officer) | `Ministry of Education` | `Teacher` | `EDUCATION_OFFICER` | Exact designation in MOE taxonomy | Valid & Resolved. No fallback used. |
| **`official@shikshasetu.gov.in`** | `National Sample Survey Office (NSSO)` | `Statistical Officer` | `STATISTICAL_OFFICER` | Exact designation in MOSPI taxonomy | Valid & Resolved. No fallback used. |
| **`edu.officer@shikshasetu.gov.in`** | `Ministry of Education` | `Teacher` | `EDUCATION_OFFICER` | Exact designation in MOE taxonomy | Valid & Resolved. No fallback used. |
| **`meity.officer@shikshasetu.gov.in`** | `Ministry of Electronics & IT` | `Informatics Officer / Scientist 'B'` | `INFORMATICS_OFFICER` | Exact designation in MeitY taxonomy | Valid & Resolved. No fallback used. |
| **`finance.officer@shikshasetu.gov.in`** | `Ministry of Finance` | `Accounts Officer (AAO / AO)` | `FINANCE_ACCOUNTS_OFFICER` | Exact designation in MOF taxonomy | Valid & Resolved. No fallback used. |
| **`trainer@shikshasetu.gov.in`** | `NSSTA` | `Senior Faculty & Trainer` | `STATISTICAL_OFFICER` (faculty baseline) | Exact designation in NSSTA taxonomy | Valid & Resolved. |
| **`admin@shikshasetu.gov.in`** | `MoSPI HQ` | `Director (Capability)` | `STATISTICAL_OFFICER` (admin baseline) | Exact designation in MoSPI taxonomy | Valid & Resolved. |

---

## 2. Unresolved User Handling & Administrative Workflow

For users whose Department / Designation does not match any configured role taxonomy:
1. **Resolution Result:** Returns `None` (UNRESOLVED).
2. **Impact on Competency Requirements:** No arbitrary competency requirements or skill gaps are assigned.
3. **Impact on Recommendations:** No false or leaked recommendations are generated.
4. **Impact on Historical Evidence:** All previously recorded learning and assessment evidence remains completely preserved and immutable.
5. **Administrative Resolution:** Authorized administrators can assign a valid role via:
   `POST /api/v1/admin/users/{user_id}/assign-role`
   ```json
   {
     "role_id": "60c72b2f9b1d8b2bad000001",
     "department": "Ministry of Education",
     "designation": "Teacher"
   }
   ```
   This formally assigns the role and reconciles active competency profiles without mutating historical evidence.
