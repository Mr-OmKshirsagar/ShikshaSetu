#!/usr/bin/env python
"""
Generate HTML preview files for the quiz assignment email template.

Usage:
    python generate_email_preview.py
"""

import os


def save_preview(filename: str, html_content: str):
    """Save HTML content to preview directory."""
    preview_dir = "email_preview"
    os.makedirs(preview_dir, exist_ok=True)
    
    filepath = os.path.join(preview_dir, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Generated: {filepath}")


def generate_preview_from_service(
    learner_name: str,
    quiz_title: str,
    quiz_description: str,
    trainer_name: str,
    competency_code: str = "",
    question_count: int = 0,
    quiz_id: str = "test-quiz-id-123",
) -> tuple[str, str]:
    """Generate email content preview without EmailService."""
    
    assessment_url = f"http://localhost:3000/assessment/{quiz_id}"
    
    # Subject
    subject = f"New Assessment Assigned — {quiz_title[:60]}{'...' if len(quiz_title) > 60 else ''} | ShikshaSetu"
    
    # HTML (simplified version for preview)
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{subject}</title>
    <style>
        body {{ margin: 0; padding: 20px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif; background: #fafafa; }}
        .preview-note {{ max-width: 600px; margin: 0 auto 20px; padding: 15px; background: #fff3cd; border: 2px dashed #ffc107; border-radius: 8px; }}
        .preview-note h3 {{ margin: 0 0 8px 0; font-size: 14px; color: #856404; }}
        .preview-note p {{ margin: 0; font-size: 12px; color: #856404; line-height: 1.5; }}
    </style>
</head>
<body>
    <div class="preview-note">
        <h3>📧 Email Preview</h3>
        <p><strong>To:</strong> {learner_name}<br>
        <strong>From:</strong> ShikshaSetu<br>
        <strong>Subject:</strong> {subject}</p>
    </div>
"""
    html += f"""
    <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #fafafa;">
        <tr>
            <td align="center" style="padding: 40px 20px;">
                <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="600" style="background-color: #ffffff; border-radius: 12px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08); overflow: hidden; max-width: 600px;">
                    
                    <tr>
                        <td style="background: linear-gradient(135deg, #ef7e37 0%, #d96a27 100%); padding: 32px 40px; text-align: center;">
                            <h1 style="margin: 0; font-size: 28px; font-weight: 700; color: #ffffff; letter-spacing: -0.5px;">ShikshaSetu</h1>
                            <p style="margin: 6px 0 0 0; font-size: 13px; font-weight: 500; color: rgba(255, 255, 255, 0.9); text-transform: uppercase; letter-spacing: 1.2px;">National Competency & Learning Platform</p>
                        </td>
                    </tr>
                    
                    <tr>
                        <td style="background-color: #fef3e7; border-bottom: 2px solid #f0ddd0; padding: 16px 40px; text-align: center;">
                            <p style="margin: 0; font-size: 12px; font-weight: 700; color: #d96a27; text-transform: uppercase; letter-spacing: 1.5px;">● New Assessment Assigned</p>
                        </td>
                    </tr>
                    
                    <tr>
                        <td style="padding: 40px;">
                            <h2 style="margin: 0 0 8px 0; font-size: 20px; font-weight: 600; color: #1a1a1a;">Hello {learner_name},</h2>
                            <p style="margin: 0 0 24px 0; font-size: 15px; color: #6b7280;"><strong style="color: #1a1a1a;">{trainer_name}</strong> has assigned a new competency assessment to you.</p>
                            
                            <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #fafafa; border: 2px solid #f0ddd0; border-radius: 10px; padding: 28px; margin-bottom: 28px;">
                                <tr>
                                    <td>
                                        <p style="margin: 0 0 12px 0; font-size: 11px; font-weight: 700; color: #9ca3af; text-transform: uppercase; letter-spacing: 1.2px;">Assigned Assessment</p>
                                        <h3 style="margin: 0 0 12px 0; font-size: 18px; font-weight: 700; color: #1a1a1a; line-height: 1.4;">{quiz_title}</h3>
                                        <p style="margin: 0 0 20px 0; font-size: 14px; color: #6b7280; line-height: 1.6;">{quiz_description}</p>
                                        
                                        <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%">
                                            {f'''<tr>
                                                <td style="padding: 10px 0; border-top: 1px solid #e5e7eb;">
                                                    <p style="margin: 0 0 4px 0; font-size: 11px; font-weight: 600; color: #9ca3af; text-transform: uppercase;">Competency Focus</p>
                                                    <p style="margin: 0; font-size: 13px; font-weight: 600; color: #1a1a1a; font-family: 'Courier New', monospace;">{competency_code}</p>
                                                </td>
                                            </tr>''' if competency_code else ''}
                                            {f'''<tr>
                                                <td style="padding: 10px 0; border-top: 1px solid #e5e7eb;">
                                                    <p style="margin: 0 0 4px 0; font-size: 11px; font-weight: 600; color: #9ca3af; text-transform: uppercase;">Questions</p>
                                                    <p style="margin: 0; font-size: 13px; font-weight: 600; color: #1a1a1a;">{question_count} assessment items</p>
                                                </td>
                                            </tr>''' if question_count > 0 else ''}
                                            <tr>
                                                <td style="padding: 10px 0; border-top: 1px solid #e5e7eb;">
                                                    <p style="margin: 0 0 4px 0; font-size: 11px; font-weight: 600; color: #9ca3af; text-transform: uppercase;">Assigned By</p>
                                                    <p style="margin: 0; font-size: 13px; font-weight: 600; color: #1a1a1a;">{trainer_name}</p>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>
                            
                            <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%">
                                <tr>
                                    <td align="center" style="padding-bottom: 24px;">
                                        <a href="{assessment_url}" style="display: inline-block; background: linear-gradient(135deg, #ef7e37 0%, #d96a27 100%); color: #ffffff; text-decoration: none; font-size: 15px; font-weight: 700; padding: 16px 40px; border-radius: 8px; box-shadow: 0 4px 12px rgba(239, 126, 55, 0.25);">Open Assessment →</a>
                                    </td>
                                </tr>
                            </table>
                            
                            <p style="margin: 0; text-align: center; font-size: 13px; color: #9ca3af;">Open ShikshaSetu to review the assessment and begin when you're ready.</p>
                        </td>
                    </tr>
                    
                    <tr>
                        <td style="background-color: #fafafa; padding: 32px 40px; border-top: 1px solid #e5e7eb; text-align: center;">
                            <p style="margin: 0 0 4px 0; font-size: 15px; font-weight: 700; color: #1a1a1a;">ShikshaSetu</p>
                            <p style="margin: 0 0 12px 0; font-size: 12px; color: #6b7280;">National Competency & Learning Platform</p>
                            <p style="margin: 0 0 8px 0; font-size: 11px; color: #9ca3af; padding-top: 12px; border-top: 1px solid #e5e7eb;">Building measurable, role-based workforce capability</p>
                            <p style="margin: 0; font-size: 10px; color: #9ca3af;">This email was sent automatically by ShikshaSetu.<br>Please do not reply to this email.</p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>"""
    
    return subject, html


def main():
    """Generate all test case previews."""
    
    print("=" * 70)
    print("📧 SHIKSHASETU EMAIL PREVIEW GENERATOR")
    print("=" * 70)
    print()
    
    # Test Case 1: Normal with full data
    print("Generating test cases...")
    
    subject, html = generate_preview_from_service(
        learner_name="Abhishek Pathak",
        quiz_title="iGOT: Data Visualization, Dashboards & Official Statistics",
        quiz_description="Comprehensive competency evaluation for public sector data visualization, official indicators, and performance dashboards.",
        trainer_name="Dr. Ananya Verma",
        competency_code="TECH_DATA_VISUALIZATION",
        question_count=15,
    )
    save_preview("01_normal_full_data.html", html)
    
    # Test Case 2: Long title
    subject, html = generate_preview_from_service(
        learner_name="Priya Sundaram",
        quiz_title="Advanced Statistical Sampling Techniques for National Survey Methodology and Quality Assurance",
        quiz_description="This comprehensive assessment evaluates understanding of statistical sampling frameworks and field operations.",
        trainer_name="Dr. Ananya Verma",
        competency_code="STAT_SAMPLING",
        question_count=20,
    )
    save_preview("02_long_title.html", html)
    
    # Test Case 3: Missing competency
    subject, html = generate_preview_from_service(
        learner_name="Amit Sen",
        quiz_title="General Knowledge Assessment",
        quiz_description="Broad assessment covering multiple competency areas for baseline evaluation.",
        trainer_name="Dr. Ananya Verma",
        competency_code="",
        question_count=25,
    )
    save_preview("03_no_competency.html", html)
    
    # Test Case 4: Minimal data
    subject, html = generate_preview_from_service(
        learner_name="Rajesh Kumar",
        quiz_title="Quick Check",
        quiz_description="Brief assessment.",
        trainer_name="Trainer",
        competency_code="",
        question_count=0,
    )
    save_preview("04_minimal_data.html", html)
    
    # Test Case 5: Long names
    subject, html = generate_preview_from_service(
        learner_name="Dr. Meenakshi Raghunathan Venkataraman",
        quiz_title="Python Programming Fundamentals",
        quiz_description="Basic Python programming concepts and data structures for public service applications.",
        trainer_name="Professor Dr. Rajesh Kumar Sharma Chowdhury",
        competency_code="TECH_PYTHON",
        question_count=10,
    )
    save_preview("05_long_names.html", html)
    
    print()
    print("=" * 70)
    print("✅ Preview generation complete!")
    print("=" * 70)
    print()
    print("Preview files saved to: backend/email_preview/")
    print()
    print("Open the HTML files in your browser to review:")
    print("  01_normal_full_data.html  - Standard case with all fields")
    print("  02_long_title.html        - Long quiz title test")
    print("  03_no_competency.html     - Missing competency code")
    print("  04_minimal_data.html      - Minimal data scenario")
    print("  05_long_names.html        - Long user names")
    print()


if __name__ == "__main__":
    main()
