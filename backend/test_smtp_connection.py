#!/usr/bin/env python
"""
Quick script to test SMTP email configuration.
Run this to verify your email settings are working before assigning quizzes.

Usage:
    python test_smtp_connection.py recipient@example.com
"""

import sys
from app.core.email import get_email_service


def test_smtp_connection(recipient_email: str):
    """Test SMTP connection and send a test email."""
    print("🔧 Testing SMTP Email Configuration...")
    print("-" * 60)
    
    email_service = get_email_service()
    
    if not email_service.enabled:
        print("❌ Email service is DISABLED")
        print("   Check your .env file for SMTP settings:")
        print("   - EMAIL_HOST")
        print("   - EMAIL_PORT")
        print("   - EMAIL_USER")
        print("   - EMAIL_PASSWORD")
        print("   - EMAIL_FROM")
        return False
    
    print("✅ Email service is ENABLED")
    print(f"   Host: {email_service.settings.EMAIL_HOST}")
    print(f"   Port: {email_service.settings.EMAIL_PORT}")
    print(f"   User: {email_service.settings.EMAIL_USER}")
    print(f"   From: {email_service.settings.EMAIL_FROM}")
    print()
    
    print(f"📧 Sending test email to: {recipient_email}")
    
    success = email_service.send_email(
        to_email=recipient_email,
        subject="[ShikshaSetu] SMTP Test Email",
        body_text="""
Hello!

This is a test email from ShikshaSetu to verify your SMTP configuration is working correctly.

If you received this email, your email notification system is operational and ready to send quiz assignment notifications to learners.

Best regards,
ShikshaSetu Team
        """.strip(),
        body_html="""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <h2 style="color: #FF6B35;">SMTP Test Successful!</h2>
    <p>Hello!</p>
    <p>This is a test email from <strong>ShikshaSetu</strong> to verify your SMTP configuration is working correctly.</p>
    
    <div style="background-color: #f5f5f5; padding: 15px; border-left: 4px solid #28a745; margin: 20px 0;">
        <p style="margin: 0;">✅ <strong>Email notifications are operational!</strong></p>
        <p style="margin: 5px 0 0 0;">Your system is ready to send quiz assignment notifications to learners.</p>
    </div>
    
    <p style="margin-top: 30px; color: #666;">
        Best regards,<br>
        <strong>ShikshaSetu Team</strong>
    </p>
</body>
</html>
        """.strip()
    )
    
    print()
    if success:
        print("✅ Test email sent successfully!")
        print(f"   Check the inbox of {recipient_email}")
        print("   Don't forget to check spam/junk folder if you don't see it")
        return True
    else:
        print("❌ Failed to send test email")
        print("   Check the logs above for error details")
        print("   Common issues:")
        print("   - Incorrect SMTP credentials")
        print("   - Gmail: Need to use App Password (not regular password)")
        print("   - Firewall blocking port 587")
        print("   - 2FA not enabled (required for Gmail App Passwords)")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_smtp_connection.py recipient@example.com")
        sys.exit(1)
    
    recipient = sys.argv[1]
    success = test_smtp_connection(recipient)
    sys.exit(0 if success else 1)
