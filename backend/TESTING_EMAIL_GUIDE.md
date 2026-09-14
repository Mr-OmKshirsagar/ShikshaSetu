# 📧 Testing Email Notifications - Step by Step Guide

## Prerequisites

✅ Backend server is running on `http://localhost:8000`  
✅ SMTP configured in `.env` file (Gmail setup complete)  
✅ You have a trainer account and at least one learner account  

---

## Method 1: Test via Web UI (Recommended)

### Step 1: Login as Trainer
1. Open your browser to `http://localhost:3000/auth/login` (or your frontend URL)
2. Login with your **trainer account** credentials
3. You should see the Trainer Dashboard

### Step 2: Check Your Quizzes
1. Navigate to **"Quiz Studio"** or **"Published Quizzes"**
2. Find a quiz with status **PUBLISHED** or **ASSIGNED**
3. If you don't have any published quizzes:
   - Create a new quiz with approved questions
   - Click **"Publish"** button to make it available for assignment

### Step 3: Assign Quiz to Learner
1. Click on the quiz you want to assign
2. Look for **"Assign to Learners"** button or similar
3. Select one or more learners from the list
4. Click **"Confirm Assignment"**

### Step 4: Check Results
**In the UI:**
- You should see a success message like:  
  `"Quiz successfully assigned to 2 learner(s). Email notifications sent: 2"`

**In the learner's inbox:**
- Check the email address of the assigned learner(s)
- Look for an email with subject: **"New Quiz Assigned: [Quiz Title]"**
- If not in inbox, check spam/junk folder

**Backend logs:**
- Check the backend terminal output for logs like:
  ```
  INFO: Quiz {quiz_id} assigned to {count} learners. Emails sent: {count}/...
  ```

---

## Method 2: Test via API (Advanced)

### Prerequisites
You need to know:
- Trainer email and password
- A published quiz ID
- Learner user ID(s)

### Option A: Using the provided script

```bash
cd backend
python test_email_assignment.py
```

The script will:
1. Login as trainer
2. Fetch available quizzes
3. Fetch learners
4. Assign quiz and send emails
5. Show success/failure status

### Option B: Manual API Testing with cURL

#### 1. Login as Trainer
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "your-trainer@email.com", "password": "YourPassword"}'
```

Save the `access_token` from the response.

#### 2. Get Your Quizzes
```bash
curl -X GET http://localhost:8000/api/v1/trainer/quizzes \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

Find a quiz with `"status": "PUBLISHED"` and copy its `id`.

#### 3. Get Learner IDs
You need to know the MongoDB `_id` of the learner user(s).

#### 4. Assign Quiz
```bash
curl -X POST http://localhost:8000/api/v1/trainer/quizzes/{QUIZ_ID}/assign \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"learner_ids": ["LEARNER_USER_ID_1", "LEARNER_USER_ID_2"]}'
```

**Expected Response:**
```json
{
  "quiz_id": "...",
  "assigned_learners_count": 2,
  "status": "ASSIGNED",
  "message": "Quiz successfully assigned to 2 learner(s). Email notifications sent: 2"
}
```

---

## Method 3: Quick SMTP Test (Verify Email Setup)

Before testing quiz assignment, verify your SMTP setup:

```bash
cd backend
python test_smtp_connection.py your-test-email@example.com
```

This will:
- Check SMTP configuration
- Send a test email to the provided address
- Confirm email delivery

**Expected Output:**
```
🔧 Testing SMTP Email Configuration...
------------------------------------------------------------
✅ Email service is ENABLED
   Host: smtp.gmail.com
   Port: 587
   User: ap17052005@gmail.com
   From: <ap17052005@gmail.com>

📧 Sending test email to: your-test-email@example.com

✅ Test email sent successfully!
   Check the inbox of your-test-email@example.com
```

---

## Troubleshooting

### Email Not Received?

**Check 1: Spam/Junk Folder**
- Gmail often filters automated emails
- Check the spam/junk folder first

**Check 2: Backend Logs**
Look for errors in the terminal running the backend:
```
ERROR: Failed to send email to learner@example.com: ...
```

**Check 3: SMTP Credentials**

**Check 4: Gmail App Password**
- Regular Gmail password won't work with SMTP
- You need a 16-character App Password
- Generate at: https://myaccount.google.com/apppasswords
- Requires 2-Factor Authentication enabled

**Check 5: Firewall**
- Some networks block port 587
- Try from a different network if blocked

### Quiz Assignment Fails?

**Error: "Cannot assign a DRAFT quiz"**
- Solution: Publish the quiz first using the "Publish" button

**Error: "Quiz not found or not owned by trainer"**
- Solution: Make sure you're using a quiz created by the logged-in trainer

**Error: "Invalid learner IDs"**
- Solution: Use valid MongoDB ObjectId values for learner user IDs

---

## Sample Email Content

Learners will receive an email like this:

**Subject:** New Quiz Assigned: Python Fundamentals Quiz

**Body:**
```
Hello John Doe,

You have been assigned a new quiz by Dr. Jane Smith.

Quiz: Python Fundamentals Quiz
Description: Test your Python knowledge

Please log in to ShikshaSetu to access and complete the quiz.

Best regards,
ShikshaSetu Team
```

---

## Verification Checklist

- [ ] Backend server running (`http://localhost:8000`)
- [ ] SMTP test successful (test_smtp_connection.py)
- [ ] Trainer logged in to UI
- [ ] Quiz published (status = PUBLISHED)
- [ ] Learner account exists with valid email
- [ ] Quiz assigned via UI
- [ ] Success message shows email count
- [ ] Email received in learner's inbox (or spam)
- [ ] Backend logs show "Emails sent: X/Y"

---

## Quick Test Workflow (< 2 minutes)

1. **Verify SMTP:**
   ```bash
   cd backend
   python test_smtp_connection.py your-email@example.com
   ```

2. **Open UI:**
   - Go to trainer dashboard
   - Select a published quiz
   - Click "Assign" button

3. **Select Learner:**
   - Choose any learner with a valid email
   - Click confirm

4. **Check Result:**
   - Look for success message in UI
   - Check learner's email inbox (or spam)
   - Check backend terminal logs

---

## Support

If emails are still not working after following this guide:

1. Check backend logs for detailed error messages
2. Verify Gmail App Password is correct
3. Try test_smtp_connection.py with different email
4. Ensure 2FA is enabled on Gmail account
5. Check if port 587 is accessible from your network

**Backend running at:** http://localhost:8000  
**API docs:** http://localhost:8000/docs  
**Email config:** `backend/.env`
