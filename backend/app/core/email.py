"""Email notification utility using SMTP."""
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending email notifications via SMTP."""

    def __init__(self):
        self.settings = get_settings()
        self.enabled = all([
            self.settings.EMAIL_HOST,
            self.settings.EMAIL_PORT,
            self.settings.EMAIL_USER,
            self.settings.EMAIL_PASSWORD,
        ])
        if not self.enabled:
            logger.warning("Email service disabled: SMTP settings not configured")

    def send_email(
        self,
        to_email: str | List[str],
        subject: str,
        body_text: str,
        body_html: str | None = None,
    ) -> bool:
        """
        Send an email via SMTP.

        Args:
            to_email: Recipient email address or list of addresses
            subject: Email subject line
            body_text: Plain text body
            body_html: Optional HTML body

        Returns:
            True if email sent successfully, False otherwise
        """
        if not self.enabled:
            logger.warning(f"Email not sent (SMTP not configured): {subject} to {to_email}")
            return False

        try:
            # Convert single email to list
            recipients = [to_email] if isinstance(to_email, str) else to_email

            # Create message
            msg = MIMEMultipart("alternative")
            msg["From"] = self.settings.EMAIL_FROM
            msg["To"] = ", ".join(recipients)
            msg["Subject"] = subject

            # Attach text and HTML parts
            msg.attach(MIMEText(body_text, "plain"))
            if body_html:
                msg.attach(MIMEText(body_html, "html"))

            # Send via SMTP
            with smtplib.SMTP(self.settings.EMAIL_HOST, self.settings.EMAIL_PORT) as server:
                server.starttls()
                server.login(self.settings.EMAIL_USER, self.settings.EMAIL_PASSWORD)
                server.send_message(msg)

            logger.info(f"Email sent successfully: {subject} to {recipients}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email: {subject} to {to_email}. Error: {e}")
            return False

    def send_quiz_assignment_notification(
        self,
        learner_email: str,
        learner_name: str,
        quiz_title: str,
        quiz_description: str,
        trainer_name: str,
        competency_code: str = "",
        question_count: int = 0,
        quiz_id: str = "",
        assigned_at: str | None = None,
    ) -> bool:
        """
        Send quiz assignment notification to a learner.

        Args:
            learner_email: Learner's email address
            learner_name: Learner's full name
            quiz_title: Title of the assigned quiz
            quiz_description: Description of the quiz
            trainer_name: Name of the trainer who assigned the quiz
            competency_code: Competency code for the quiz (optional)
            question_count: Number of questions in the quiz (optional)
            quiz_id: Quiz identifier for deep link (optional)
            assigned_at: Assignment timestamp (optional)

        Returns:
            True if email sent successfully, False otherwise
        """
        import html
        
        # Escape HTML for security (prevent XSS)
        learner_name_html = html.escape(learner_name)
        quiz_title_html = html.escape(quiz_title)
        quiz_description_html = html.escape(quiz_description)
        trainer_name_html = html.escape(trainer_name)
        competency_code_html = html.escape(competency_code) if competency_code else ""
        
        # Enhanced subject line with platform branding
        subject = f"New Assessment Assigned — {quiz_title[:60]}{'...' if len(quiz_title) > 60 else ''} | ShikshaSetu"

        # Assessment URL
        assessment_url = f"http://localhost:3000/assessment/{quiz_id}" if quiz_id else "http://localhost:3000"

        # Enhanced plain text version
        body_text = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SHIKSHASETU — National Competency & Learning Platform
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

NEW ASSESSMENT ASSIGNED

Hello {learner_name},

{trainer_name} has assigned a new competency assessment to you.

ASSESSMENT DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{quiz_title}

{quiz_description}
{f'''
COMPETENCY FOCUS
{competency_code}
''' if competency_code else ''}{f'''
QUESTIONS
{question_count} assessment items
''' if question_count > 0 else ''}
ASSIGNED BY
{trainer_name}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Open ShikshaSetu to review and begin your assessment:

{assessment_url}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ShikshaSetu
National Competency & Learning Platform
Building measurable, role-based workforce capability

This email was sent automatically by ShikshaSetu.
Please do not reply to this email.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""".strip()

        # Premium HTML email template
        body_html = f"""
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="color-scheme" content="light dark">
    <meta name="supported-color-schemes" content="light dark">
    <title>New Assessment Assigned | ShikshaSetu</title>
    <!--[if mso]>
    <style type="text/css">
        table {{mso-table-lspace: 0pt; mso-table-rspace: 0pt;}}
        td {{mso-line-height-rule: exactly;}}
    </style>
    <![endif]-->
    <style type="text/css">
        @media only screen and (max-width: 600px) {{
            .container {{ width: 100% !important; }}
            .content {{ padding: 20px !important; }}
            .header {{ padding: 24px 20px !important; }}
            .quiz-card {{ padding: 20px !important; }}
            .cta-button {{ width: 100% !important; display: block !important; }}
        }}
        @media (prefers-color-scheme: dark) {{
            .dark-mode-bg {{ background-color: #1a1a1a !important; }}
            .dark-mode-text {{ color: #e5e5e5 !important; }}
            .dark-mode-card {{ background-color: #2d2d2d !important; border-color: #404040 !important; }}
        }}
    </style>
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #fafafa; -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale;">
    <!-- Outer wrapper table for email client compatibility -->
    <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #fafafa;">
        <tr>
            <td align="center" style="padding: 40px 20px;">
                <!-- Main container -->
                <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="600" class="container" style="background-color: #ffffff; border-radius: 12px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08); overflow: hidden; max-width: 600px;">
                    
                    <!-- Header -->
                    <tr>
                        <td class="header" style="background: linear-gradient(135deg, #ef7e37 0%, #d96a27 100%); padding: 32px 40px; text-align: center;">
                            <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%">
                                <tr>
                                    <td style="text-align: center;">
                                        <h1 style="margin: 0; font-size: 28px; font-weight: 700; color: #ffffff; letter-spacing: -0.5px;">ShikshaSetu</h1>
                                        <p style="margin: 6px 0 0 0; font-size: 13px; font-weight: 500; color: rgba(255, 255, 255, 0.9); text-transform: uppercase; letter-spacing: 1.2px;">National Competency & Learning Platform</p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- Status Banner -->
                    <tr>
                        <td style="padding: 0;">
                            <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%">
                                <tr>
                                    <td style="background-color: #fef3e7; border-bottom: 2px solid #f0ddd0; padding: 16px 40px; text-align: center;">
                                        <p style="margin: 0; font-size: 12px; font-weight: 700; color: #d96a27; text-transform: uppercase; letter-spacing: 1.5px;">● New Assessment Assigned</p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- Content -->
                    <tr>
                        <td class="content" style="padding: 40px;">
                            
                            <!-- Greeting -->
                            <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%">
                                <tr>
                                    <td style="padding-bottom: 24px;">
                                        <h2 style="margin: 0 0 8px 0; font-size: 20px; font-weight: 600; color: #1a1a1a; line-height: 1.4;">Hello {learner_name_html},</h2>
                                        <p style="margin: 0; font-size: 15px; color: #6b7280; line-height: 1.6;"><strong style="color: #1a1a1a;">{trainer_name_html}</strong> has assigned a new competency assessment to you.</p>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- Quiz Card -->
                            <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" class="quiz-card dark-mode-card" style="background-color: #fafafa; border: 2px solid #f0ddd0; border-radius: 10px; padding: 28px; margin-bottom: 28px;">
                                <tr>
                                    <td>
                                        <p style="margin: 0 0 12px 0; font-size: 11px; font-weight: 700; color: #9ca3af; text-transform: uppercase; letter-spacing: 1.2px;">Assigned Assessment</p>
                                        <h3 style="margin: 0 0 12px 0; font-size: 18px; font-weight: 700; color: #1a1a1a; line-height: 1.4;">{quiz_title_html}</h3>
                                        <p style="margin: 0 0 20px 0; font-size: 14px; color: #6b7280; line-height: 1.6;">{quiz_description_html}</p>
                                        
                                        <!-- Metadata -->
                                        <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%">
                                            {f'''<tr>
                                                <td style="padding: 10px 0; border-top: 1px solid #e5e7eb;">
                                                    <p style="margin: 0 0 4px 0; font-size: 11px; font-weight: 600; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.8px;">Competency Focus</p>
                                                    <p style="margin: 0; font-size: 13px; font-weight: 600; color: #1a1a1a; font-family: 'Courier New', monospace;">{competency_code_html}</p>
                                                </td>
                                            </tr>''' if competency_code_html else ''}
                                            {f'''<tr>
                                                <td style="padding: 10px 0; border-top: 1px solid #e5e7eb;">
                                                    <p style="margin: 0 0 4px 0; font-size: 11px; font-weight: 600; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.8px;">Questions</p>
                                                    <p style="margin: 0; font-size: 13px; font-weight: 600; color: #1a1a1a;">{question_count} assessment items</p>
                                                </td>
                                            </tr>''' if question_count > 0 else ''}
                                            <tr>
                                                <td style="padding: 10px 0; border-top: 1px solid #e5e7eb;">
                                                    <p style="margin: 0 0 4px 0; font-size: 11px; font-weight: 600; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.8px;">Assigned By</p>
                                                    <p style="margin: 0; font-size: 13px; font-weight: 600; color: #1a1a1a;">{trainer_name_html}</p>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- CTA Button -->
                            <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%">
                                <tr>
                                    <td align="center" style="padding-bottom: 24px;">
                                        <a href="{assessment_url}" class="cta-button" style="display: inline-block; background: linear-gradient(135deg, #ef7e37 0%, #d96a27 100%); color: #ffffff; text-decoration: none; font-size: 15px; font-weight: 700; padding: 16px 40px; border-radius: 8px; box-shadow: 0 4px 12px rgba(239, 126, 55, 0.25); text-align: center; min-width: 200px;">Open Assessment →</a>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- Supporting Text -->
                            <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%">
                                <tr>
                                    <td style="text-align: center; padding-bottom: 20px;">
                                        <p style="margin: 0; font-size: 13px; color: #9ca3af; line-height: 1.5;">Open ShikshaSetu to review the assessment and begin when you're ready.</p>
                                    </td>
                                </tr>
                            </table>
                            
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #fafafa; padding: 32px 40px; border-top: 1px solid #e5e7eb;">
                            <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%">
                                <tr>
                                    <td style="text-align: center; padding-bottom: 12px;">
                                        <p style="margin: 0 0 4px 0; font-size: 15px; font-weight: 700; color: #1a1a1a;">ShikshaSetu</p>
                                        <p style="margin: 0; font-size: 12px; color: #6b7280;">National Competency & Learning Platform</p>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="text-align: center; padding-top: 12px; border-top: 1px solid #e5e7eb;">
                                        <p style="margin: 0 0 8px 0; font-size: 11px; color: #9ca3af; line-height: 1.6;">Building measurable, role-based workforce capability</p>
                                        <p style="margin: 0; font-size: 10px; color: #9ca3af; line-height: 1.5;">This email was sent automatically by ShikshaSetu.<br>Please do not reply to this email.</p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
""".strip()

        return self.send_email(learner_email, subject, body_text, body_html)


# Singleton instance
_email_service = None


def get_email_service() -> EmailService:
    """Get or create the EmailService singleton."""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service
