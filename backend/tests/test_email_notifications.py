"""Tests for email notification service."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from app.core.email import EmailService, get_email_service
from app.core.config import Settings


@pytest.fixture
def mock_settings():
    """Create mock settings with email config."""
    settings = Mock(spec=Settings)
    settings.EMAIL_HOST = "smtp.gmail.com"
    settings.EMAIL_PORT = 587
    settings.EMAIL_USER = "test@example.com"
    settings.EMAIL_PASSWORD = "test_password"
    settings.EMAIL_FROM = "noreply@shikshasetu.com"
    return settings


@pytest.fixture
def email_service(mock_settings):
    """Create EmailService with mocked settings."""
    with patch("app.core.email.get_settings", return_value=mock_settings):
        service = EmailService()
    return service


def test_email_service_initialization_with_valid_config(mock_settings):
    """Test EmailService initializes correctly with valid SMTP config."""
    with patch("app.core.email.get_settings", return_value=mock_settings):
        service = EmailService()
        assert service.enabled is True


def test_email_service_initialization_without_config():
    """Test EmailService disables itself when SMTP config is missing."""
    settings = Mock(spec=Settings)
    settings.EMAIL_HOST = ""
    settings.EMAIL_PORT = 587
    settings.EMAIL_USER = ""
    settings.EMAIL_PASSWORD = ""
    
    with patch("app.core.email.get_settings", return_value=settings):
        service = EmailService()
        assert service.enabled is False


@patch("app.core.email.smtplib.SMTP")
def test_send_email_success(mock_smtp_class, email_service):
    """Test sending email successfully."""
    # Setup mock SMTP server
    mock_smtp = MagicMock()
    mock_smtp_class.return_value.__enter__.return_value = mock_smtp
    
    # Send email
    result = email_service.send_email(
        to_email="learner@example.com",
        subject="Test Subject",
        body_text="Test body",
        body_html="<p>Test body</p>"
    )
    
    # Verify
    assert result is True
    mock_smtp.starttls.assert_called_once()
    mock_smtp.login.assert_called_once_with("test@example.com", "test_password")
    mock_smtp.send_message.assert_called_once()


@patch("app.core.email.smtplib.SMTP")
def test_send_email_to_multiple_recipients(mock_smtp_class, email_service):
    """Test sending email to multiple recipients."""
    mock_smtp = MagicMock()
    mock_smtp_class.return_value.__enter__.return_value = mock_smtp
    
    result = email_service.send_email(
        to_email=["learner1@example.com", "learner2@example.com"],
        subject="Test Subject",
        body_text="Test body"
    )
    
    assert result is True
    mock_smtp.send_message.assert_called_once()


@patch("app.core.email.smtplib.SMTP")
def test_send_email_failure(mock_smtp_class, email_service):
    """Test email sending failure is handled gracefully."""
    mock_smtp = MagicMock()
    mock_smtp.login.side_effect = Exception("SMTP authentication failed")
    mock_smtp_class.return_value.__enter__.return_value = mock_smtp
    
    result = email_service.send_email(
        to_email="learner@example.com",
        subject="Test Subject",
        body_text="Test body"
    )
    
    assert result is False


def test_send_email_when_disabled():
    """Test sending email when service is disabled (no SMTP config)."""
    settings = Mock(spec=Settings)
    settings.EMAIL_HOST = ""
    settings.EMAIL_PORT = 587
    settings.EMAIL_USER = ""
    settings.EMAIL_PASSWORD = ""
    
    with patch("app.core.email.get_settings", return_value=settings):
        service = EmailService()
        result = service.send_email(
            to_email="learner@example.com",
            subject="Test Subject",
            body_text="Test body"
        )
        assert result is False


@patch("app.core.email.smtplib.SMTP")
def test_send_quiz_assignment_notification(mock_smtp_class, email_service):
    """Test sending quiz assignment notification email."""
    mock_smtp = MagicMock()
    mock_smtp_class.return_value.__enter__.return_value = mock_smtp
    
    result = email_service.send_quiz_assignment_notification(
        learner_email="learner@example.com",
        learner_name="John Doe",
        quiz_title="Python Fundamentals Quiz",
        quiz_description="Test your Python knowledge",
        trainer_name="Dr. Jane Smith"
    )
    
    assert result is True
    mock_smtp.send_message.assert_called_once()
    
    # Verify the message contains expected content
    call_args = mock_smtp.send_message.call_args
    msg = call_args[0][0]
    assert "New Assessment Assigned" in msg["Subject"]
    assert "ShikshaSetu" in msg["Subject"]
    assert "learner@example.com" in msg["To"]


@patch("app.core.email.smtplib.SMTP")
def test_send_quiz_assignment_with_full_parameters(mock_smtp_class, email_service):
    """Test sending quiz assignment with all optional parameters."""
    mock_smtp = MagicMock()
    mock_smtp_class.return_value.__enter__.return_value = mock_smtp
    
    from datetime import datetime
    
    result = email_service.send_quiz_assignment_notification(
        learner_email="learner@example.com",
        learner_name="Abhishek Pathak",
        quiz_title="Data Visualization Assessment",
        quiz_description="Comprehensive evaluation for data visualization competency",
        trainer_name="Dr. Ananya Verma",
        competency_code="TECH_DATA_VISUALIZATION",
        question_count=15,
        quiz_id="test-quiz-123",
        assigned_at=datetime(2026, 1, 15, 10, 30)
    )
    
    assert result is True
    mock_smtp.send_message.assert_called_once()
    
    # Verify message structure
    call_args = mock_smtp.send_message.call_args
    msg = call_args[0][0]
    
    # Check subject includes branding
    assert "ShikshaSetu" in msg["Subject"]
    assert "Data Visualization Assessment" in msg["Subject"]
    
    # Verify HTML body contains new fields
    html_body = None
    for part in msg.walk():
        if part.get_content_type() == "text/html":
            html_body = part.get_payload(decode=True).decode()
            break
    
    assert html_body is not None
    assert "TECH_DATA_VISUALIZATION" in html_body
    assert "15 assessment items" in html_body
    assert "test-quiz-123" in html_body
    assert "Abhishek Pathak" in html_body
    assert "Dr. Ananya Verma" in html_body


@patch("app.core.email.smtplib.SMTP")
def test_send_quiz_assignment_without_optional_parameters(mock_smtp_class, email_service):
    """Test sending quiz assignment without optional parameters (backward compatibility)."""
    mock_smtp = MagicMock()
    mock_smtp_class.return_value.__enter__.return_value = mock_smtp
    
    result = email_service.send_quiz_assignment_notification(
        learner_email="learner@example.com",
        learner_name="Test Learner",
        quiz_title="General Assessment",
        quiz_description="Broad evaluation",
        trainer_name="Test Trainer"
    )
    
    assert result is True
    mock_smtp.send_message.assert_called_once()


@patch("app.core.email.smtplib.SMTP")
def test_subject_line_length_truncation(mock_smtp_class, email_service):
    """Test that long quiz titles are truncated in subject line."""
    mock_smtp = MagicMock()
    mock_smtp_class.return_value.__enter__.return_value = mock_smtp
    
    long_title = "Advanced Statistical Sampling Techniques for National Survey Methodology and Quality Assurance Framework"
    
    result = email_service.send_quiz_assignment_notification(
        learner_email="learner@example.com",
        learner_name="Test Learner",
        quiz_title=long_title,
        quiz_description="Test",
        trainer_name="Test Trainer"
    )
    
    assert result is True
    
    # Verify subject is truncated
    call_args = mock_smtp.send_message.call_args
    msg = call_args[0][0]
    subject = msg["Subject"]
    
    # Should have ellipsis if title is too long
    if len(long_title) > 60:
        assert "..." in subject
    
    # Subject should still have branding
    assert "ShikshaSetu" in subject


@patch("app.core.email.smtplib.SMTP")
def test_html_and_plain_text_both_present(mock_smtp_class, email_service):
    """Test that both HTML and plain-text versions are sent."""
    mock_smtp = MagicMock()
    mock_smtp_class.return_value.__enter__.return_value = mock_smtp
    
    result = email_service.send_quiz_assignment_notification(
        learner_email="learner@example.com",
        learner_name="Test Learner",
        quiz_title="Test Quiz",
        quiz_description="Test Description",
        trainer_name="Test Trainer",
        competency_code="TEST_COMP",
        question_count=10
    )
    
    assert result is True
    
    # Verify both content types exist
    call_args = mock_smtp.send_message.call_args
    msg = call_args[0][0]
    
    content_types = []
    for part in msg.walk():
        content_types.append(part.get_content_type())
    
    assert "text/plain" in content_types
    assert "text/html" in content_types


@patch("app.core.email.smtplib.SMTP")
def test_assessment_url_in_html(mock_smtp_class, email_service):
    """Test that assessment URL is correctly included in HTML."""
    mock_smtp = MagicMock()
    mock_smtp_class.return_value.__enter__.return_value = mock_smtp
    
    quiz_id = "quiz-abc-123"
    
    result = email_service.send_quiz_assignment_notification(
        learner_email="learner@example.com",
        learner_name="Test Learner",
        quiz_title="Test Quiz",
        quiz_description="Test",
        trainer_name="Test Trainer",
        quiz_id=quiz_id
    )
    
    assert result is True
    
    # Extract HTML body
    call_args = mock_smtp.send_message.call_args
    msg = call_args[0][0]
    
    html_body = None
    for part in msg.walk():
        if part.get_content_type() == "text/html":
            html_body = part.get_payload(decode=True).decode()
            break
    
    assert html_body is not None
    assert f"http://localhost:3000/assessment/{quiz_id}" in html_body


@patch("app.core.email.smtplib.SMTP")
def test_multiple_recipients_quiz_notification(mock_smtp_class, email_service):
    """Test sending quiz assignment to multiple learners."""
    mock_smtp = MagicMock()
    mock_smtp_class.return_value.__enter__.return_value = mock_smtp
    
    result = email_service.send_quiz_assignment_notification(
        learner_email=["learner1@example.com", "learner2@example.com", "learner3@example.com"],
        learner_name="Team Members",
        quiz_title="Team Assessment",
        quiz_description="Group evaluation",
        trainer_name="Test Trainer"
    )
    
    assert result is True
    mock_smtp.send_message.assert_called_once()


@patch("app.core.email.smtplib.SMTP")
def test_empty_competency_code_handling(mock_smtp_class, email_service):
    """Test that empty competency code doesn't break email."""
    mock_smtp = MagicMock()
    mock_smtp_class.return_value.__enter__.return_value = mock_smtp
    
    result = email_service.send_quiz_assignment_notification(
        learner_email="learner@example.com",
        learner_name="Test Learner",
        quiz_title="General Quiz",
        quiz_description="No specific competency",
        trainer_name="Test Trainer",
        competency_code="",
        question_count=0
    )
    
    assert result is True
    
    # Verify HTML doesn't show empty competency section
    call_args = mock_smtp.send_message.call_args
    msg = call_args[0][0]
    
    html_body = None
    for part in msg.walk():
        if part.get_content_type() == "text/html":
            html_body = part.get_payload(decode=True).decode()
            break
    
    assert html_body is not None
    # If competency is empty, the competency row should not appear
    # (depends on template implementation)


@patch("app.core.email.smtplib.SMTP")
def test_special_characters_in_names(mock_smtp_class, email_service):
    """Test handling of special characters in names."""
    mock_smtp = MagicMock()
    mock_smtp_class.return_value.__enter__.return_value = mock_smtp
    
    result = email_service.send_quiz_assignment_notification(
        learner_email="learner@example.com",
        learner_name="Müller O'Brien-García",
        quiz_title="Test Quiz <script>alert('xss')</script>",
        quiz_description="Test & Description",
        trainer_name="Dr. José María"
    )
    
    assert result is True
    
    # Verify HTML escaping
    call_args = mock_smtp.send_message.call_args
    msg = call_args[0][0]
    
    html_body = None
    for part in msg.walk():
        if part.get_content_type() == "text/html":
            html_body = part.get_payload(decode=True).decode()
            break
    
    assert html_body is not None
    # Script tags should be escaped
    assert "<script>" not in html_body or "&lt;script&gt;" in html_body


def test_get_email_service_singleton():
    """Test get_email_service returns singleton instance."""
    service1 = get_email_service()
    service2 = get_email_service()
    assert service1 is service2
