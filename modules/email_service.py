import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
import socket

# Load .env file from the workspace root
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(env_path)

# Email Configuration
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "your-email@gmail.com").strip()
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "your-app-password").strip()
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_TIMEOUT = 30  # 30 second timeout

# Debug: Check if credentials are loaded
if SENDER_EMAIL == "your-email@gmail.com":
    print("⚠️ WARNING: Gmail credentials not configured in .env file")
else:
    print(f"✅ Email service configured for: {SENDER_EMAIL}")

def send_interview_results_email(recipient_email, user_name, overall_score, feedback, interview_data):
    """Send interview results to user's email"""
    try:
        # Create email message
        message = MIMEMultipart("alternative")
        message["Subject"] = "🎉 Your AI Interview Results"
        message["From"] = SENDER_EMAIL
        message["To"] = recipient_email
        
        # Create HTML email body
        html_body = f"""
        <html>
            <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; background: linear-gradient(135deg, #e0f7fa 0%, #b2ebf2 100%); border-radius: 10px; padding: 30px;">
                    
                    <!-- Header -->
                    <div style="text-align: center; margin-bottom: 30px; border-bottom: 2px solid #00bcd4; padding-bottom: 20px;">
                        <h1 style="color: #0097a7; margin: 0; font-size: 28px;">🎉 Interview Complete!</h1>
                        <p style="color: #00838f; margin: 10px 0 0 0; font-size: 14px;">Thank you for taking the AI Interview</p>
                    </div>
                    
                    <!-- Greeting -->
                    <div style="margin-bottom: 25px;">
                        <p style="font-size: 16px; color: #333;">Hello <strong>{user_name}</strong>,</p>
                        <p style="color: #666;">Your interview has been completed and evaluated. Here are your results:</p>
                    </div>
                    
                    <!-- Score Banner -->
                    <div style="background: white; border-radius: 12px; padding: 25px; text-align: center; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,188,212,0.1);">
                        <div style="font-size: 50px; font-weight: 900; color: #00bcd4; margin-bottom: 10px;">{overall_score:.1f}/10</div>
                        <div style="font-size: 14px; color: #00838f; font-weight: 600; letter-spacing: 1px;">OVERALL SCORE</div>
                        
                        <!-- Score Interpretation -->
                        <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #e0f7fa;">
                            <p style="margin: 0; color: #666; font-size: 14px;">
        """
        
        # Add score interpretation
        if overall_score >= 8:
            html_body += "<strong style='color: #00bcd4;'>Excellent Performance!</strong> 🌟<br>You demonstrated strong skills and knowledge."
        elif overall_score >= 6:
            html_body += "<strong style='color: #0097a7;'>Good Performance</strong> 👍<br>There are opportunities to improve further."
        else:
            html_body += "<strong style='color: #ff9800;'>Keep Practicing</strong> 💪<br>Focus on weak areas and practice regularly."
        
        html_body += f"""
                            </p>
                        </div>
                    </div>
                    
                    <!-- Feedback Section -->
                    <div style="background: white; border-radius: 12px; padding: 20px; margin-bottom: 25px; border-left: 4px solid #00bcd4;">
                        <h3 style="color: #00bcd4; margin-top: 0;">📝 Feedback</h3>
                        <p style="color: #555; font-size: 14px; line-height: 1.8;">{feedback}</p>
                    </div>
                    
                    <!-- Interview Stats -->
                    <div style="background: white; border-radius: 12px; padding: 20px; margin-bottom: 25px;">
                        <h3 style="color: #00bcd4; margin-top: 0;">📊 Interview Details</h3>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                            <div style="background: #f4fbfc; padding: 12px; border-radius: 8px;">
                                <div style="color: #00838f; font-size: 12px; font-weight: 600;">Total Questions</div>
                                <div style="color: #0097a7; font-size: 20px; font-weight: 800;">{interview_data.get('questions_count', 'N/A')}</div>
                            </div>
                            <div style="background: #f4fbfc; padding: 12px; border-radius: 8px;">
                                <div style="color: #00838f; font-size: 12px; font-weight: 600;">Interview Date</div>
                                <div style="color: #0097a7; font-size: 14px; font-weight: 700;">{interview_data.get('date', 'N/A')}</div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- CTA Section -->
                    <div style="background: linear-gradient(90deg, #00bcd4, #0097a7); border-radius: 12px; padding: 20px; text-align: center; color: white; margin-bottom: 25px;">
                        <h3 style="margin-top: 0; color: white;">Ready to improve further?</h3>
                        <p style="font-size: 14px; margin: 10px 0;">Log back into the AI Interview Simulator to practice more interviews and track your progress.</p>
                        <a href="http://localhost:8501" style="display: inline-block; background: white; color: #00bcd4; padding: 10px 25px; border-radius: 6px; text-decoration: none; font-weight: 700; margin-top: 10px;">Start Another Interview</a>
                    </div>
                    
                    <!-- Footer -->
                    <div style="text-align: center; border-top: 1px solid #e0f7fa; padding-top: 20px; color: #999; font-size: 12px;">
                        <p style="margin: 5px 0;">© 2026 AI Interview Simulator</p>
                        <p style="margin: 5px 0;">Built to help you succeed in interviews</p>
                    </div>
                    
                </div>
            </body>
        </html>
        """
        
        # Attach HTML to email
        part = MIMEText(html_body, "html")
        message.attach(part)
        
        # Send email with timeout
        try:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=SMTP_TIMEOUT)
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, recipient_email, message.as_string())
            server.quit()
        except socket.timeout:
            return False, "Email service timeout - please try again"
        except smtplib.SMTPAuthenticationError:
            return False, "Email authentication failed - check credentials"
        except smtplib.SMTPException as e:
            return False, f"SMTP error: {str(e)}"
        
        return True, "Email sent successfully!"
        
    except Exception as e:
        error_msg = str(e)
        print(f"Error sending email: {error_msg}")
        return False, f"Failed to send email: {error_msg}"

def send_scheduled_interview_notification(user_email, user_name, admin_name, interview_type, notes=""):
    """Send notification when admin schedules an interview for a user"""
    try:
        # Validate credentials first
        if SENDER_EMAIL == "your-email@gmail.com" or SENDER_PASSWORD == "your-app-password":
            return False, "❌ Email credentials not configured. Please check .env file."
        
        if not user_email:
            return False, "❌ Recipient email address is required"
        
        message = MIMEMultipart("alternative")
        message["Subject"] = "📅 Interview Scheduled for You"
        message["From"] = SENDER_EMAIL
        message["To"] = user_email
        
        # Build notes HTML if notes exist
        notes_html = f"<p><strong>Notes:</strong> {notes}</p>" if notes else ""
        
        html_body = f"""
        <html>
            <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; background: linear-gradient(135deg, #e0f7fa 0%, #b2ebf2 100%); border-radius: 10px; padding: 30px;">
                    
                    <!-- Header -->
                    <div style="text-align: center; margin-bottom: 30px; border-bottom: 2px solid #00bcd4; padding-bottom: 20px;">
                        <h1 style="color: #0097a7; margin: 0; font-size: 28px;">📅 Interview Scheduled</h1>
                    </div>
                    
                    <!-- Greeting -->
                    <div style="margin-bottom: 25px;">
                        <p style="font-size: 16px; color: #333;">Hello <strong>{user_name}</strong>,</p>
                        <p style="color: #666;">An interview has been scheduled for you by <strong>{admin_name}</strong>.</p>
                    </div>
                    
                    <!-- Interview Details -->
                    <div style="background: white; border-radius: 12px; padding: 20px; margin-bottom: 25px; border-left: 4px solid #00bcd4;">
                        <h3 style="color: #00bcd4; margin-top: 0;">📋 Interview Details</h3>
                        <div style="color: #555; font-size: 14px; line-height: 2;">
                            <p><strong>Interview Type:</strong> {interview_type}</p>
                            <p><strong>Scheduled By:</strong> {admin_name}</p>
                            {notes_html}
                        </div>
                    </div>
                    
                    <!-- CTA -->
                    <div style="background: linear-gradient(90deg, #00bcd4, #0097a7); border-radius: 12px; padding: 20px; text-align: center; color: white; margin-bottom: 25px;">
                        <h3 style="margin-top: 0; color: white;">Ready?</h3>
                        <p style="font-size: 14px; margin: 10px 0;">Log in to the AI Interview Simulator to take your scheduled interview.</p>
                        <a href="http://localhost:8501" style="display: inline-block; background: white; color: #00bcd4; padding: 10px 25px; border-radius: 6px; text-decoration: none; font-weight: 700; margin-top: 10px;">Take Interview</a>
                    </div>
                    
                    <!-- Footer -->
                    <div style="text-align: center; border-top: 1px solid #e0f7fa; padding-top: 20px; color: #999; font-size: 12px;">
                        <p style="margin: 5px 0;">© 2026 AI Interview Simulator</p>
                    </div>
                    
                </div>
            </body>
        </html>
        """
        
        part = MIMEText(html_body, "html")
        message.attach(part)
        
        # Send email with timeout
        try:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=SMTP_TIMEOUT)
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, user_email, message.as_string())
            server.quit()
        except socket.timeout:
            return False, "Email service timeout - please try again"
        except smtplib.SMTPAuthenticationError:
            return False, "Email authentication failed - check credentials"
        except smtplib.SMTPException as e:
            return False, f"SMTP error: {str(e)}"
        
        return True, "Notification sent successfully!"
        
    except Exception as e:
        error_msg = str(e)
        print(f"Error sending notification: {error_msg}")
        return False, f"Failed to send notification: {error_msg}"
