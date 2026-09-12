# SMTP Email Notifications for Quiz Assignment

## Overview
Implemented automated email notifications sent via SMTP when trainers assign quizzes to learners.

## Implementation Details

### 1. Email Service Module (`app/core/email.py`)
- **EmailService class**: Handles SMTP email sending with TLS encryption
- **send_email()**: Generic email sending method supporting both plain text and HTML
- **send_quiz_assignment_notification()**: Specialized method for quiz assignment emails
- **Singleton pattern**: `get_email_service()` function for efficient reuse

### 2. Configuration Updates (`app/core/config.py`)
Added SMTP configuration fields to Settings:
- `EMAIL_HOST`: SMTP server hostname (e.g., smtp.gmail.com)
- `EMAIL_PORT`: SMTP port (default: 587 for TLS)
- `EMAIL_USER`: SMTP authentication username
- `EMAIL_PASSWORD`: SMTP authentication password
- `EMAIL_FROM`: Sender email address

### 3. Quiz Assignment Service (`app/trainer/service.py`)
Updated `assign_quiz()` method to:
- Fetch trainer and learner details from database
- Send personalized email to each assigned learner
- Track email sending success/failure
- Include email notification count in response message
- Handle failures gracefully (quiz assignment succeeds even if emails fail)

### 4. Email Content
Each notification email includes:
- **Subject**: "New Quiz Assigned: {Quiz Title}"
- **Learner name**: Personalized greeting
- **Quiz title**: Name of the assigned quiz
- **Quiz description**: Context about the assessment
- **Trainer name**: Who assigned the quiz
- **Call to action**: Login prompt to access the quiz
- **Dual format**: Plain text + HTML for email client compatibility

### 5. Error Handling
- SMTP connection failures are logged but don't block quiz assignment
- Individual email failures are caught and logged per learner
- Service disabled gracefully if SMTP settings are incomplete
- Quiz assignment always succeeds regardless of email delivery status

## Configuration

Add the following to your `.env` file:

```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-specific-password
EMAIL_FROM="ShikshaSetu <noreply@shikshasetu.com>"
```

### Gmail App Password Setup
1. Enable 2-Factor Authentication on your Google Account
2. Go to: https://myaccount.google.com/apppasswords
3. Generate an "App Password" for "Mail"
4. Use the generated 16-character password in `EMAIL_PASSWORD`

## Testing

### Unit Tests (`tests/test_email_notifications.py`)
- ✅ Email service initialization with valid/invalid config
- ✅ Successful email sending with SMTP mock
- ✅ Multiple recipient email handling
- ✅ Email failure handling
- ✅ Disabled service behavior
- ✅ Quiz assignment notification format
- ✅ Singleton pattern verification

**Result**: 8/8 tests passing

### Integration Tests (`tests/test_trainer.py`)
- ✅ Email notifications sent when assigning quiz to multiple learners
- ✅ Graceful handling when email service fails
- ✅ Correct email content (learner email, quiz title, description, trainer name)
- ✅ Email service called once per learner
- ✅ Assignment succeeds even if all emails fail

**Result**: 2/2 email notification tests passing

## Usage Example

```python
# Quiz assignment automatically triggers email notifications
resp = client.post(
    f"/api/v1/trainer/quizzes/{quiz_id}/assign",
    headers=headers,
    json={"learner_ids": ["user1_id", "user2_id"]}
)

# Response includes email notification status
# {
#     "quiz_id": "...",
#     "assigned_learners_count": 2,
#     "status": "ASSIGNED",
#     "message": "Quiz successfully assigned to 2 learner(s). Email notifications sent: 2"
# }
```

## Security Considerations

1. **App-specific passwords**: Never use your main Gmail password
2. **TLS encryption**: Emails sent over encrypted connection (STARTTLS)
3. **Email privacy**: Learner emails are fetched from database, not exposed in API
4. **Failure isolation**: Email failures don't expose sensitive error details to API clients
5. **Credential storage**: SMTP credentials stored in environment variables, not code

## Future Enhancements

Potential improvements for future iterations:
- [ ] Email templates stored in database for trainer customization
- [ ] Batch email sending for large learner groups
- [ ] Email delivery status tracking and retry mechanism
- [ ] Support for attachments (e.g., quiz instructions PDF)
- [ ] HTML email templates with branding/logos
- [ ] Unsubscribe management for learners
- [ ] Email bounce handling
- [ ] Multi-language email support based on learner preferences

## Files Modified

1. **Created**: `backend/app/core/email.py` - Email service module
2. **Modified**: `backend/app/core/config.py` - Added SMTP configuration
3. **Modified**: `backend/app/trainer/service.py` - Integrated email notifications
4. **Created**: `backend/tests/test_email_notifications.py` - Email service tests
5. **Modified**: `backend/tests/test_trainer.py` - Added integration tests
6. **Updated**: `backend/.env` - SMTP credentials (already configured)

## Verification Steps

To verify the implementation:

```bash
# Run email service tests
python -m pytest tests/test_email_notifications.py -v

# Run trainer integration tests
python -m pytest tests/test_trainer.py::test_quiz_assignment_sends_email_notifications -v

# Test with real SMTP (optional, requires valid credentials)
# 1. Set up .env with real SMTP credentials
# 2. Run the backend server
# 3. Assign a quiz to a learner via API
# 4. Check learner's inbox for notification email
```

---

**Status**: ✅ **COMPLETE** - All tests passing. Email notifications operational.
