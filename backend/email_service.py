import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from pathlib import Path
from typing import Optional, List, Dict, Any
import logging
from dotenv import load_dotenv
from datetime import datetime, timedelta
import hashlib
import json

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env', override=True)

logger = logging.getLogger(__name__)

# Track sent emails to prevent duplicates (in-memory cache)
_sent_emails_cache: Dict[str, datetime] = {}
DUPLICATE_WINDOW_MINUTES = 5  # Prevent same email within 5 minutes

class EmailService:
    def __init__(self):
        # Reload environment variables to ensure they're loaded
        load_dotenv(ROOT_DIR / '.env', override=True)
        self._load_credentials()
    
    def _load_credentials(self):
        """Load or reload SMTP credentials from environment"""
        load_dotenv(ROOT_DIR / '.env', override=True)
        
        self.smtp_host = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.environ.get('SMTP_PORT', '587'))
        self.smtp_user = os.environ.get('SMTP_USER', '')
        self.smtp_password = os.environ.get('SMTP_PASSWORD', '')
        self.from_email = os.environ.get('FROM_EMAIL', self.smtp_user)
        self.admin_email = os.environ.get('ADMIN_EMAIL', 'sotubodammy@gmail.com')
        self.site_url = os.environ.get('SITE_URL', 'https://afro-market.co.uk')
        
        # Log configuration status
        if self.smtp_user and self.smtp_password:
            logger.info(f"Email service initialized with SMTP user: {self.smtp_user}")
        else:
            logger.warning("Email service: SMTP credentials not configured")
    
    def _generate_email_hash(self, to_email: str, subject: str, key_data: str = "") -> str:
        """Generate a hash to identify duplicate emails"""
        content = f"{to_email}:{subject}:{key_data}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _is_duplicate_email(self, email_hash: str) -> bool:
        """Check if email was recently sent (prevent duplicates)"""
        global _sent_emails_cache
        
        # Clean old entries
        now = datetime.utcnow()
        cutoff = now - timedelta(minutes=DUPLICATE_WINDOW_MINUTES)
        _sent_emails_cache = {k: v for k, v in _sent_emails_cache.items() if v > cutoff}
        
        if email_hash in _sent_emails_cache:
            logger.warning(f"Duplicate email prevented (hash: {email_hash[:8]}...)")
            return True
        
        return False
    
    def _mark_email_sent(self, email_hash: str):
        """Mark email as sent to prevent duplicates"""
        _sent_emails_cache[email_hash] = datetime.utcnow()
    
    def send_email(self, to_email: str, subject: str, html_content: str, text_content: Optional[str] = None, prevent_duplicate: bool = True, duplicate_key: str = ""):
        """Send an email with duplicate prevention"""
        # Reload credentials in case they were updated
        self._load_credentials()
        
        # Check for duplicates
        if prevent_duplicate:
            email_hash = self._generate_email_hash(to_email, subject, duplicate_key)
            if self._is_duplicate_email(email_hash):
                return False
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add text and HTML parts
            if text_content:
                part1 = MIMEText(text_content, 'plain')
                msg.attach(part1)
            
            part2 = MIMEText(html_content, 'html')
            msg.attach(part2)
            
            # Send email
            if self.smtp_user and self.smtp_password:
                with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                    server.starttls()
                    server.login(self.smtp_user, self.smtp_password)
                    server.send_message(msg)
                logger.info(f"Email sent successfully to {to_email}")
                
                # Mark as sent for duplicate prevention
                if prevent_duplicate:
                    self._mark_email_sent(email_hash)
                
                return True
            else:
                logger.warning("SMTP credentials not configured. Email not sent.")
                # In development, just log the email content
                logger.info(f"\n{'='*50}\nEMAIL PREVIEW\nTo: {to_email}\nSubject: {subject}\n{'-'*50}\n{html_content[:500]}...\n{'='*50}")
                return False
        except Exception as e:
            logger.error(f"Error sending email to {to_email}: {str(e)}")
            return False
            return False
    
    def send_vendor_registration_notification(self, vendor_data: dict):
        """Send vendor registration notification to admin"""
        subject = f"🎉 New Vendor Registration: {vendor_data.get('business_name', 'Unknown')}" 
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f9f9f9;
                }}
                .header {{
                    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                }}
                .content {{
                    background: white;
                    padding: 30px;
                    border-radius: 0 0 10px 10px;
                }}
                .info-row {{
                    margin: 15px 0;
                    padding: 10px;
                    background: #f3f4f6;
                    border-left: 4px solid #10b981;
                }}
                .label {{
                    font-weight: bold;
                    color: #059669;
                }}
                .status-badge {{
                    display: inline-block;
                    padding: 5px 15px;
                    background: #fbbf24;
                    color: #78350f;
                    border-radius: 20px;
                    font-weight: bold;
                    margin: 10px 0;
                }}
                .footer {{
                    text-align: center;
                    padding: 20px;
                    color: #666;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🏪 New Vendor Registration</h1>
                    <p>AfroMarket UK</p>
                </div>
                <div class="content">
                    <p>A new vendor has registered on the AfroMarket UK platform!</p>
                    <span class="status-badge">⏳ Pending Approval</span>
                    
                    <div class="info-row">
                        <span class="label">Business Name:</span><br>
                        {vendor_data.get('business_name', 'N/A')}
                    </div>
                    
                    <div class="info-row">
                        <span class="label">Email:</span><br>
                        {vendor_data.get('email', 'N/A')}
                    </div>
                    
                    <div class="info-row">
                        <span class="label">Phone:</span><br>
                        {vendor_data.get('phone', 'N/A')}
                    </div>
                    
                    <div class="info-row">
                        <span class="label">Location:</span><br>
                        {vendor_data.get('address', 'N/A')}<br>
                        {vendor_data.get('city', 'N/A')}, {vendor_data.get('postcode', 'N/A')}
                    </div>
                    
                    <div class="info-row">
                        <span class="label">Description:</span><br>
                        {vendor_data.get('description', 'N/A')}
                    </div>
                    
                    <div class="info-row">
                        <span class="label">Registered At:</span><br>
                        {vendor_data.get('created_at', 'N/A')}
                    </div>
                    
                    <div style="margin-top: 30px; padding: 20px; background: #dcfce7; border-radius: 10px;">
                        <h3 style="color: #059669; margin-top: 0;">📋 Next Steps:</h3>
                        <ol>
                            <li>Review vendor details</li>
                            <li>Verify business credentials</li>
                            <li>Approve or reject the application</li>
                            <li>Notify the vendor of the decision</li>
                        </ol>
                    </div>
                </div>
                <div class="footer">
                    <p>This is an automated notification from AfroMarket UK</p>
                    <p>&copy; 2025 AfroMarket UK. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        New Vendor Registration - AfroMarket UK
        
        Business Name: {vendor_data.get('business_name', 'N/A')}
        Email: {vendor_data.get('email', 'N/A')}
        Phone: {vendor_data.get('phone', 'N/A')}
        Location: {vendor_data.get('city', 'N/A')}, {vendor_data.get('postcode', 'N/A')}
        Address: {vendor_data.get('address', 'N/A')}
        Description: {vendor_data.get('description', 'N/A')}
        Registered At: {vendor_data.get('created_at', 'N/A')}
        
        Status: Pending Approval
        
        Please review and approve/reject this vendor application.
        """
        
        return self.send_email(
            to_email=self.admin_email,
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )
    
    def send_vendor_approval_email(self, vendor_email: str, vendor_name: str, approved: bool):
        """Send approval/rejection email to vendor"""
        if approved:
            subject = "✅ Your AfroMarket UK Vendor Application has been Approved!"
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        color: #333;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                        background-color: #f9f9f9;
                    }}
                    .header {{
                        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                        color: white;
                        padding: 30px;
                        text-align: center;
                        border-radius: 10px 10px 0 0;
                    }}
                    .content {{
                        background: white;
                        padding: 30px;
                        border-radius: 0 0 10px 10px;
                    }}
                    .button {{
                        display: inline-block;
                        padding: 15px 30px;
                        background: #10b981;
                        color: white;
                        text-decoration: none;
                        border-radius: 5px;
                        margin: 20px 0;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🎉 Congratulations!</h1>
                    </div>
                    <div class="content">
                        <h2>Welcome to AfroMarket UK, {vendor_name}!</h2>
                        <p>We're excited to inform you that your vendor application has been approved!</p>
                        <p>You can now start adding products and reaching customers across the UK.</p>
                        <p style="text-align: center;">
                            <a href="https://afromarket-staging.preview.emergentagent.com/vendor/dashboard" class="button">Go to Dashboard</a>
                        </p>
                        <p>If you have any questions, feel free to contact us.</p>
                        <p>Best regards,<br>The AfroMarket UK Team</p>
                    </div>
                </div>
            </body>
            </html>
            """
        else:
            subject = "AfroMarket UK Vendor Application Update"
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <body>
                <div class="container">
                    <h2>Hello {vendor_name},</h2>
                    <p>Thank you for your interest in AfroMarket UK.</p>
                    <p>Unfortunately, we are unable to approve your vendor application at this time.</p>
                    <p>If you have any questions, please contact us.</p>
                    <p>Best regards,<br>The AfroMarket UK Team</p>
                </div>
            </body>
            </html>
            """
        
        return self.send_email(
            to_email=vendor_email,
            subject=subject,
            html_content=html_content
        )

    def send_password_reset_email(self, to_email: str, user_name: str, reset_link: str):
        """Send password reset email to user"""
        subject = "🔐 Reset Your AfroMarket UK Password"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    margin: 0;
                    padding: 0;
                    background-color: #f4f4f4;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                    color: white;
                    padding: 40px 30px;
                    text-align: center;
                    border-radius: 16px 16px 0 0;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 28px;
                    font-weight: 700;
                }}
                .header p {{
                    margin: 10px 0 0;
                    opacity: 0.9;
                }}
                .content {{
                    background: white;
                    padding: 40px 30px;
                    border-radius: 0 0 16px 16px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }}
                .greeting {{
                    font-size: 18px;
                    color: #333;
                    margin-bottom: 20px;
                }}
                .message {{
                    color: #666;
                    margin-bottom: 30px;
                }}
                .button {{
                    display: inline-block;
                    padding: 16px 40px;
                    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                    color: white !important;
                    text-decoration: none;
                    border-radius: 8px;
                    font-weight: 600;
                    font-size: 16px;
                    text-align: center;
                    box-shadow: 0 4px 14px rgba(16, 185, 129, 0.4);
                }}
                .button:hover {{
                    background: linear-gradient(135deg, #059669 0%, #047857 100%);
                }}
                .button-container {{
                    text-align: center;
                    margin: 30px 0;
                }}
                .warning {{
                    background: #fef3c7;
                    border-left: 4px solid #f59e0b;
                    padding: 15px 20px;
                    border-radius: 0 8px 8px 0;
                    margin: 25px 0;
                }}
                .warning-title {{
                    font-weight: 600;
                    color: #92400e;
                    margin-bottom: 5px;
                }}
                .warning-text {{
                    color: #a16207;
                    font-size: 14px;
                    margin: 0;
                }}
                .link-box {{
                    background: #f3f4f6;
                    padding: 15px;
                    border-radius: 8px;
                    margin: 20px 0;
                    word-break: break-all;
                    font-size: 12px;
                    color: #6b7280;
                }}
                .footer {{
                    text-align: center;
                    padding: 30px 20px;
                    color: #9ca3af;
                    font-size: 12px;
                }}
                .footer a {{
                    color: #10b981;
                    text-decoration: none;
                }}
                .security-note {{
                    background: #ecfdf5;
                    border-radius: 8px;
                    padding: 15px 20px;
                    margin-top: 25px;
                }}
                .security-note h4 {{
                    color: #059669;
                    margin: 0 0 10px;
                    font-size: 14px;
                }}
                .security-note ul {{
                    margin: 0;
                    padding-left: 20px;
                    color: #047857;
                    font-size: 13px;
                }}
                .security-note li {{
                    margin: 5px 0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔐 Password Reset</h1>
                    <p>AfroMarket UK</p>
                </div>
                <div class="content">
                    <p class="greeting">Hello {user_name},</p>
                    
                    <p class="message">
                        We received a request to reset your password for your AfroMarket UK account. 
                        Click the button below to create a new password.
                    </p>
                    
                    <div class="button-container">
                        <a href="{reset_link}" class="button">Reset My Password</a>
                    </div>
                    
                    <div class="warning">
                        <p class="warning-title">⏰ This link expires in 30 minutes</p>
                        <p class="warning-text">For security reasons, this password reset link will expire soon. If you don't reset your password within this time, you'll need to request a new link.</p>
                    </div>
                    
                    <p style="font-size: 14px; color: #6b7280;">
                        If the button doesn't work, copy and paste this link into your browser:
                    </p>
                    <div class="link-box">
                        {reset_link}
                    </div>
                    
                    <div class="security-note">
                        <h4>🛡️ Security Tips:</h4>
                        <ul>
                            <li>Never share your password with anyone</li>
                            <li>Use a strong, unique password</li>
                            <li>If you didn't request this reset, please ignore this email</li>
                        </ul>
                    </div>
                    
                    <p style="margin-top: 30px; color: #666;">
                        Best regards,<br>
                        <strong>The AfroMarket UK Team</strong>
                    </p>
                </div>
                <div class="footer">
                    <p>This is an automated message from AfroMarket UK</p>
                    <p>If you didn't request a password reset, you can safely ignore this email.</p>
                    <p>&copy; 2025 AfroMarket UK. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Password Reset Request - AfroMarket UK
        
        Hello {user_name},
        
        We received a request to reset your password for your AfroMarket UK account.
        
        Click this link to reset your password:
        {reset_link}
        
        This link will expire in 30 minutes.
        
        If you didn't request this password reset, please ignore this email.
        
        Best regards,
        The AfroMarket UK Team
        """
        
        return self.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )
    
    def send_password_changed_confirmation(self, to_email: str, user_name: str):
        """Send confirmation email after password has been changed"""
        subject = "✅ Your AfroMarket UK Password Has Been Changed"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    margin: 0;
                    padding: 0;
                    background-color: #f4f4f4;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                    color: white;
                    padding: 40px 30px;
                    text-align: center;
                    border-radius: 16px 16px 0 0;
                }}
                .content {{
                    background: white;
                    padding: 40px 30px;
                    border-radius: 0 0 16px 16px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }}
                .success-icon {{
                    width: 80px;
                    height: 80px;
                    background: #ecfdf5;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin: 0 auto 20px;
                    font-size: 40px;
                }}
                .alert {{
                    background: #fef2f2;
                    border-left: 4px solid #ef4444;
                    padding: 15px 20px;
                    border-radius: 0 8px 8px 0;
                    margin: 25px 0;
                }}
                .button {{
                    display: inline-block;
                    padding: 14px 30px;
                    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                    color: white !important;
                    text-decoration: none;
                    border-radius: 8px;
                    font-weight: 600;
                }}
                .footer {{
                    text-align: center;
                    padding: 30px 20px;
                    color: #9ca3af;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>✅ Password Changed</h1>
                    <p>AfroMarket UK</p>
                </div>
                <div class="content">
                    <div class="success-icon">✓</div>
                    
                    <h2 style="text-align: center; color: #059669;">Password Successfully Changed</h2>
                    
                    <p>Hello {user_name},</p>
                    
                    <p>Your AfroMarket UK account password has been successfully changed.</p>
                    
                    <div class="alert">
                        <p style="margin: 0; color: #991b1b;">
                            <strong>⚠️ Didn't make this change?</strong><br>
                            If you didn't change your password, please contact us immediately or reset your password again to secure your account.
                        </p>
                    </div>
                    
                    <p style="text-align: center; margin-top: 30px;">
                        <a href="https://afromarket-staging.preview.emergentagent.com/login" class="button">Login to Your Account</a>
                    </p>
                    
                    <p style="margin-top: 30px; color: #666;">
                        Best regards,<br>
                        <strong>The AfroMarket UK Team</strong>
                    </p>
                </div>
                <div class="footer">
                    <p>This is an automated security notification from AfroMarket UK</p>
                    <p>&copy; 2025 AfroMarket UK. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Password Changed - AfroMarket UK
        
        Hello {user_name},
        
        Your AfroMarket UK account password has been successfully changed.
        
        If you didn't make this change, please contact us immediately or reset your password again to secure your account.
        
        Best regards,
        The AfroMarket UK Team
        """
        
        return self.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )

    def send_order_confirmation(self, to_email: str, customer_name: str, order_data: dict):
        """Send order confirmation email to customer after successful payment"""
        order_id = order_data.get('orderId', 'N/A')
        total = order_data.get('total', 0)
        items = order_data.get('items', [])
        shipping_info = order_data.get('shippingInfo', {})
        
        # Build items HTML
        items_html = ""
        for item in items:
            items_html += f"""
            <tr>
                <td style="padding: 12px; border-bottom: 1px solid #e5e7eb;">
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <img src="{item.get('image', '')}" alt="{item.get('name', '')}" style="width: 60px; height: 60px; border-radius: 8px; object-fit: cover;">
                        <div>
                            <p style="margin: 0; font-weight: 600; color: #1f2937;">{item.get('name', 'Product')}</p>
                            <p style="margin: 4px 0 0; color: #6b7280; font-size: 14px;">Qty: {item.get('quantity', 1)}</p>
                        </div>
                    </div>
                </td>
                <td style="padding: 12px; border-bottom: 1px solid #e5e7eb; text-align: right; font-weight: 600;">
                    £{item.get('price', 0):.2f}
                </td>
            </tr>
            """
        
        subject = f"🎉 Order Confirmed - #{order_id}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    margin: 0;
                    padding: 0;
                    background-color: #f4f4f4;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                    color: white;
                    padding: 40px 30px;
                    text-align: center;
                    border-radius: 16px 16px 0 0;
                }}
                .content {{
                    background: white;
                    padding: 40px 30px;
                    border-radius: 0 0 16px 16px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }}
                .order-box {{
                    background: #f0fdf4;
                    border: 2px solid #10b981;
                    border-radius: 12px;
                    padding: 20px;
                    text-align: center;
                    margin: 20px 0;
                }}
                .order-id {{
                    font-size: 24px;
                    font-weight: 700;
                    color: #059669;
                    margin: 0;
                }}
                .section {{
                    margin: 30px 0;
                }}
                .section-title {{
                    font-size: 18px;
                    font-weight: 600;
                    color: #1f2937;
                    margin-bottom: 15px;
                    padding-bottom: 10px;
                    border-bottom: 2px solid #e5e7eb;
                }}
                .address-box {{
                    background: #f9fafb;
                    border-radius: 8px;
                    padding: 15px;
                }}
                .total-row {{
                    display: flex;
                    justify-content: space-between;
                    padding: 10px 0;
                    border-bottom: 1px solid #e5e7eb;
                }}
                .total-row.final {{
                    border-bottom: none;
                    font-size: 20px;
                    font-weight: 700;
                    color: #059669;
                    padding-top: 15px;
                    margin-top: 10px;
                    border-top: 2px solid #10b981;
                }}
                .button {{
                    display: inline-block;
                    padding: 14px 30px;
                    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                    color: white !important;
                    text-decoration: none;
                    border-radius: 8px;
                    font-weight: 600;
                }}
                .footer {{
                    text-align: center;
                    padding: 30px 20px;
                    color: #9ca3af;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Order Confirmed!</h1>
                    <p>Thank you for shopping with AfroMarket UK</p>
                </div>
                <div class="content">
                    <p>Hello {customer_name},</p>
                    <p>Great news! Your order has been confirmed and is being processed. Here are your order details:</p>
                    
                    <div class="order-box">
                        <p style="margin: 0 0 5px; color: #6b7280;">Order Number</p>
                        <p class="order-id">#{order_id}</p>
                    </div>
                    
                    <div class="section">
                        <h3 class="section-title">📦 Order Items</h3>
                        <table style="width: 100%; border-collapse: collapse;">
                            {items_html}
                        </table>
                    </div>
                    
                    <div class="section">
                        <h3 class="section-title">💰 Order Summary</h3>
                        <div class="total-row">
                            <span>Subtotal</span>
                            <span>£{order_data.get('subtotal', 0):.2f}</span>
                        </div>
                        <div class="total-row">
                            <span>Delivery Fee</span>
                            <span>£{order_data.get('deliveryFee', 0):.2f}</span>
                        </div>
                        <div class="total-row final">
                            <span>Total Paid</span>
                            <span>£{total:.2f}</span>
                        </div>
                    </div>
                    
                    <div class="section">
                        <h3 class="section-title">📍 Delivery Address</h3>
                        <div class="address-box">
                            <p style="margin: 0; font-weight: 600;">{shipping_info.get('fullName', customer_name)}</p>
                            <p style="margin: 5px 0 0; color: #6b7280;">
                                {shipping_info.get('address', '')}<br>
                                {shipping_info.get('city', '')}, {shipping_info.get('postcode', '')}<br>
                                {shipping_info.get('phone', '')}
                            </p>
                        </div>
                    </div>
                    
                    <div style="background: #fef3c7; border-radius: 8px; padding: 15px; margin: 20px 0;">
                        <p style="margin: 0; color: #92400e;">
                            <strong>📧 What's Next?</strong><br>
                            You'll receive another email when your order is shipped with tracking information.
                        </p>
                    </div>
                    
                    <p style="text-align: center; margin-top: 30px;">
                        <a href="https://afromarket-staging.preview.emergentagent.com/profile" class="button">Track Your Order</a>
                    </p>
                    
                    <p style="margin-top: 30px; color: #666;">
                        Thank you for choosing AfroMarket UK!<br>
                        <strong>The AfroMarket UK Team</strong>
                    </p>
                </div>
                <div class="footer">
                    <p>Questions? Contact us at support@afromarket.co.uk</p>
                    <p>&copy; 2025 AfroMarket UK. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Order Confirmed - AfroMarket UK
        
        Hello {customer_name},
        
        Your order #{order_id} has been confirmed!
        
        Order Total: £{total:.2f}
        
        Delivery Address:
        {shipping_info.get('fullName', customer_name)}
        {shipping_info.get('address', '')}
        {shipping_info.get('city', '')}, {shipping_info.get('postcode', '')}
        
        You'll receive tracking information once your order ships.
        
        Thank you for shopping with AfroMarket UK!
        """
        
        return self.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )

    def send_vendor_order_notification(self, to_email: str, vendor_name: str, order_data: dict, customer_info: dict):
        """Send order notification to vendor with customer details"""
        order_id = order_data.get('orderId', 'N/A')
        items = order_data.get('items', [])
        
        # Build items HTML
        items_html = ""
        total_vendor_amount = 0
        for item in items:
            item_total = item.get('price', 0) * item.get('quantity', 1)
            total_vendor_amount += item_total
            items_html += f"""
            <tr>
                <td style="padding: 12px; border-bottom: 1px solid #e5e7eb;">{item.get('name', 'Product')}</td>
                <td style="padding: 12px; border-bottom: 1px solid #e5e7eb; text-align: center;">{item.get('quantity', 1)}</td>
                <td style="padding: 12px; border-bottom: 1px solid #e5e7eb; text-align: right;">£{item.get('price', 0):.2f}</td>
                <td style="padding: 12px; border-bottom: 1px solid #e5e7eb; text-align: right; font-weight: 600;">£{item_total:.2f}</td>
            </tr>
            """
        
        commission = total_vendor_amount * 0.10
        vendor_earning = total_vendor_amount - commission
        
        subject = f"🛒 New Order Received - #{order_id}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    margin: 0;
                    padding: 0;
                    background-color: #f4f4f4;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
                    color: white;
                    padding: 40px 30px;
                    text-align: center;
                    border-radius: 16px 16px 0 0;
                }}
                .content {{
                    background: white;
                    padding: 40px 30px;
                    border-radius: 0 0 16px 16px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }}
                .customer-box {{
                    background: #f0f9ff;
                    border: 2px solid #0ea5e9;
                    border-radius: 12px;
                    padding: 20px;
                    margin: 20px 0;
                }}
                .customer-title {{
                    font-size: 16px;
                    font-weight: 600;
                    color: #0369a1;
                    margin: 0 0 15px;
                }}
                .customer-info {{
                    display: grid;
                    gap: 10px;
                }}
                .info-row {{
                    display: flex;
                    gap: 10px;
                }}
                .info-label {{
                    font-weight: 600;
                    color: #64748b;
                    min-width: 80px;
                }}
                .earnings-box {{
                    background: #f0fdf4;
                    border: 2px solid #10b981;
                    border-radius: 12px;
                    padding: 20px;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    padding: 30px 20px;
                    color: #9ca3af;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🛒 New Order Received!</h1>
                    <p>Order #{order_id}</p>
                </div>
                <div class="content">
                    <p>Hello {vendor_name},</p>
                    <p>Great news! You have received a new order. Please prepare the items for delivery.</p>
                    
                    <div class="customer-box">
                        <p class="customer-title">👤 Customer Information</p>
                        <div class="customer-info">
                            <div class="info-row">
                                <span class="info-label">Name:</span>
                                <span>{customer_info.get('name', 'N/A')}</span>
                            </div>
                            <div class="info-row">
                                <span class="info-label">Email:</span>
                                <span>{customer_info.get('email', 'N/A')}</span>
                            </div>
                            <div class="info-row">
                                <span class="info-label">Phone:</span>
                                <span>{customer_info.get('phone', 'N/A')}</span>
                            </div>
                            <div class="info-row">
                                <span class="info-label">Address:</span>
                                <span>{customer_info.get('address', 'N/A')}</span>
                            </div>
                            <div class="info-row">
                                <span class="info-label">City:</span>
                                <span>{customer_info.get('city', 'N/A')}, {customer_info.get('postcode', 'N/A')}</span>
                            </div>
                        </div>
                    </div>
                    
                    <h3 style="color: #1f2937; margin-top: 30px;">📦 Order Items</h3>
                    <table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
                        <thead>
                            <tr style="background: #f3f4f6;">
                                <th style="padding: 12px; text-align: left;">Product</th>
                                <th style="padding: 12px; text-align: center;">Qty</th>
                                <th style="padding: 12px; text-align: right;">Price</th>
                                <th style="padding: 12px; text-align: right;">Total</th>
                            </tr>
                        </thead>
                        <tbody>
                            {items_html}
                        </tbody>
                    </table>
                    
                    <div class="earnings-box">
                        <h3 style="color: #059669; margin: 0 0 15px;">💰 Your Earnings</h3>
                        <div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #d1fae5;">
                            <span>Order Total</span>
                            <span>£{total_vendor_amount:.2f}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #d1fae5;">
                            <span>Platform Fee (10%)</span>
                            <span style="color: #ef4444;">-£{commission:.2f}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; padding: 12px 0; font-size: 18px; font-weight: 700; color: #059669;">
                            <span>Your Earning</span>
                            <span>£{vendor_earning:.2f}</span>
                        </div>
                    </div>
                    
                    <p style="margin-top: 30px; color: #666;">
                        Please prepare the order for delivery as soon as possible.<br>
                        <strong>The AfroMarket UK Team</strong>
                    </p>
                </div>
                <div class="footer">
                    <p>&copy; 2025 AfroMarket UK. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content
        )

    def send_vendor_notification_email(self, to_email: str, vendor_name: str, 
                                       notification_type: str, title: str, 
                                       message: str, link: str = None):
        """Send a generic notification email to vendor"""
        
        # Choose icon and color based on type
        type_config = {
            'order': {'icon': '🛒', 'color': '#2563eb', 'bg': '#eff6ff'},
            'message': {'icon': '💬', 'color': '#7c3aed', 'bg': '#f5f3ff'},
            'review': {'icon': '⭐', 'color': '#f59e0b', 'bg': '#fffbeb'},
            'approval': {'icon': '✅', 'color': '#10b981', 'bg': '#f0fdf4'},
            'rejection': {'icon': '⚠️', 'color': '#ef4444', 'bg': '#fef2f2'},
            'system': {'icon': '📢', 'color': '#6b7280', 'bg': '#f9fafb'},
        }
        
        config = type_config.get(notification_type, type_config['system'])
        
        button_html = ""
        if link:
            full_link = f"https://afromarket-staging.preview.emergentagent.com{link}"
            button_html = f'''
            <div style="text-align: center; margin: 30px 0;">
                <a href="{full_link}" style="display: inline-block; padding: 14px 32px; 
                   background: linear-gradient(135deg, {config['color']}, {config['color']}dd); 
                   color: white; text-decoration: none; border-radius: 8px; font-weight: 600;">
                    View Details
                </a>
            </div>
            '''
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    margin: 0;
                    padding: 0;
                    background-color: #f4f4f4;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 12px 12px 0 0;
                }}
                .content {{
                    background: white;
                    padding: 30px;
                    border-radius: 0 0 12px 12px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }}
                .notification-box {{
                    background: {config['bg']};
                    border-left: 4px solid {config['color']};
                    border-radius: 8px;
                    padding: 20px;
                    margin: 20px 0;
                }}
                .notification-title {{
                    font-size: 18px;
                    font-weight: 600;
                    color: {config['color']};
                    margin: 0 0 10px;
                }}
                .notification-message {{
                    color: #4b5563;
                    margin: 0;
                }}
                .footer {{
                    text-align: center;
                    padding: 20px;
                    color: #9ca3af;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{config['icon']} Notification</h1>
                    <p>AfroMarket UK</p>
                </div>
                <div class="content">
                    <p>Hello <strong>{vendor_name}</strong>,</p>
                    
                    <div class="notification-box">
                        <p class="notification-title">{title}</p>
                        <p class="notification-message">{message}</p>
                    </div>
                    
                    {button_html}
                    
                    <p style="color: #6b7280; font-size: 14px;">
                        This is an automated notification from AfroMarket UK. 
                        You can manage your notification preferences in your vendor dashboard.
                    </p>
                    
                    <p style="margin-top: 20px;">
                        Best regards,<br>
                        <strong>The AfroMarket UK Team</strong>
                    </p>
                </div>
                <div class="footer">
                    <p>&copy; 2025 AfroMarket UK. All rights reserved.</p>
                    <p>
                        <a href="https://afromarket-staging.preview.emergentagent.com/vendor/notifications/settings" 
                           style="color: #10b981; text-decoration: none;">
                            Manage notification preferences
                        </a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(
            to_email=to_email,
            subject=f"{config['icon']} {title}",
            html_content=html_content
        )

    # ============ COMPREHENSIVE PAYMENT NOTIFICATION SYSTEM ============
    
    def send_payment_confirmation_to_customer(
        self, 
        customer_email: str, 
        customer_name: str, 
        order_data: Dict[str, Any]
    ) -> bool:
        """
        Send comprehensive payment confirmation email to customer
        
        Args:
            customer_email: Customer's email address
            customer_name: Customer's name
            order_data: Order details including items, shipping, delivery info
        """
        order_id = order_data.get('order_id', order_data.get('orderId', 'N/A'))
        items = order_data.get('items', [])
        shipping_info = order_data.get('shipping_info', order_data.get('shippingInfo', {}))
        delivery_info = order_data.get('delivery_info', {})
        subtotal = order_data.get('subtotal', 0)
        delivery_fee = order_data.get('delivery_fee', order_data.get('deliveryFee', 0))
        total = order_data.get('total', subtotal + delivery_fee)
        payment_method = order_data.get('payment_method', 'Card')
        
        # Calculate estimated arrival
        estimated_days = delivery_info.get('estimated_days', '3-5 days')
        now = datetime.utcnow()
        
        # Parse estimated days to calculate arrival date
        try:
            if 'Same day' in estimated_days:
                arrival_date = now
            elif 'Next day' in estimated_days:
                arrival_date = now + timedelta(days=1)
            else:
                # Extract first number from string like "2-3 days"
                import re
                match = re.search(r'(\d+)', estimated_days)
                days = int(match.group(1)) if match else 3
                arrival_date = now + timedelta(days=days + 1)  # Add buffer
            
            estimated_arrival = arrival_date.strftime('%A, %d %B %Y')
        except:
            estimated_arrival = f"Within {estimated_days}"
        
        # Build items HTML
        items_html = ""
        for item in items:
            price = float(item.get('price', 0))
            qty = int(item.get('quantity', 1))
            item_total = price * qty
            items_html += f"""
            <tr>
                <td style="padding: 15px; border-bottom: 1px solid #e5e7eb;">
                    <div style="display: flex; align-items: center; gap: 15px;">
                        <img src="{item.get('image', '')}" alt="" style="width: 60px; height: 60px; border-radius: 8px; object-fit: cover; background: #f3f4f6;">
                        <div>
                            <p style="margin: 0; font-weight: 600; color: #1f2937;">{item.get('name', 'Product')}</p>
                            <p style="margin: 4px 0 0; color: #6b7280; font-size: 14px;">Qty: {qty}</p>
                            {f'<p style="margin: 4px 0 0; color: #9ca3af; font-size: 12px;">Vendor: {item.get("vendor_name", "")}</p>' if item.get('vendor_name') else ''}
                        </div>
                    </div>
                </td>
                <td style="padding: 15px; border-bottom: 1px solid #e5e7eb; text-align: right;">
                    <p style="margin: 0; font-weight: 600;">£{item_total:.2f}</p>
                    <p style="margin: 2px 0 0; color: #9ca3af; font-size: 12px;">£{price:.2f} each</p>
                </td>
            </tr>
            """
        
        subject = f"✅ Payment Confirmed - Order #{order_id}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f4f4;">
            <table role="presentation" style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td align="center" style="padding: 20px;">
                        <table role="presentation" style="width: 100%; max-width: 600px; border-collapse: collapse;">
                            <!-- Header -->
                            <tr>
                                <td style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); padding: 40px 30px; text-align: center; border-radius: 16px 16px 0 0;">
                                    <h1 style="margin: 0; color: white; font-size: 28px;">✅ Payment Successful!</h1>
                                    <p style="margin: 10px 0 0; color: rgba(255,255,255,0.9); font-size: 16px;">Thank you for your order</p>
                                </td>
                            </tr>
                            
                            <!-- Content -->
                            <tr>
                                <td style="background: white; padding: 40px 30px; border-radius: 0 0 16px 16px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                                    <p style="margin: 0 0 20px; font-size: 16px;">Hello <strong>{customer_name}</strong>,</p>
                                    
                                    <p style="margin: 0 0 25px; color: #4b5563;">
                                        Great news! Your payment has been successfully processed and your order is confirmed. 
                                        Here are your complete order details:
                                    </p>
                                    
                                    <!-- Order Reference Box -->
                                    <table role="presentation" style="width: 100%; background: #f0fdf4; border: 2px solid #10b981; border-radius: 12px; margin-bottom: 25px;">
                                        <tr>
                                            <td style="padding: 20px; text-align: center;">
                                                <p style="margin: 0 0 5px; color: #6b7280; font-size: 14px;">Order Reference</p>
                                                <p style="margin: 0; font-size: 24px; font-weight: 700; color: #059669;">#{order_id}</p>
                                                <p style="margin: 10px 0 0; color: #6b7280; font-size: 13px;">
                                                    Payment Method: {payment_method} | Date: {now.strftime('%d %B %Y, %H:%M')}
                                                </p>
                                            </td>
                                        </tr>
                                    </table>
                                    
                                    <!-- Order Items -->
                                    <h3 style="margin: 30px 0 15px; font-size: 18px; color: #1f2937; border-bottom: 2px solid #e5e7eb; padding-bottom: 10px;">
                                        📦 Order Items
                                    </h3>
                                    <table role="presentation" style="width: 100%; border-collapse: collapse;">
                                        {items_html}
                                    </table>
                                    
                                    <!-- Order Summary -->
                                    <h3 style="margin: 30px 0 15px; font-size: 18px; color: #1f2937; border-bottom: 2px solid #e5e7eb; padding-bottom: 10px;">
                                        💰 Payment Summary
                                    </h3>
                                    <table role="presentation" style="width: 100%;">
                                        <tr>
                                            <td style="padding: 10px 0; color: #4b5563;">Subtotal</td>
                                            <td style="padding: 10px 0; text-align: right; font-weight: 500;">£{subtotal:.2f}</td>
                                        </tr>
                                        <tr>
                                            <td style="padding: 10px 0; color: #4b5563;">Delivery Fee</td>
                                            <td style="padding: 10px 0; text-align: right; font-weight: 500;">
                                                {'<span style="color: #10b981;">FREE</span>' if delivery_fee == 0 else f'£{delivery_fee:.2f}'}
                                            </td>
                                        </tr>
                                        <tr style="border-top: 2px solid #10b981;">
                                            <td style="padding: 15px 0 10px; font-size: 18px; font-weight: 700; color: #059669;">Total Paid</td>
                                            <td style="padding: 15px 0 10px; text-align: right; font-size: 20px; font-weight: 700; color: #059669;">£{total:.2f}</td>
                                        </tr>
                                    </table>
                                    
                                    <!-- Delivery Information -->
                                    <h3 style="margin: 30px 0 15px; font-size: 18px; color: #1f2937; border-bottom: 2px solid #e5e7eb; padding-bottom: 10px;">
                                        🚚 Delivery Information
                                    </h3>
                                    <table role="presentation" style="width: 100%; background: #f9fafb; border-radius: 12px;">
                                        <tr>
                                            <td style="padding: 20px;">
                                                <table role="presentation" style="width: 100%;">
                                                    <tr>
                                                        <td style="width: 50%; vertical-align: top; padding-right: 15px;">
                                                            <p style="margin: 0 0 5px; color: #6b7280; font-size: 13px; font-weight: 600;">DELIVERY ADDRESS</p>
                                                            <p style="margin: 0; font-weight: 600; color: #1f2937;">{shipping_info.get('fullName', customer_name)}</p>
                                                            <p style="margin: 5px 0 0; color: #4b5563;">
                                                                {shipping_info.get('address', 'N/A')}<br>
                                                                {shipping_info.get('city', '')}, {shipping_info.get('postcode', '')}<br>
                                                                {shipping_info.get('phone', '')}
                                                            </p>
                                                        </td>
                                                        <td style="width: 50%; vertical-align: top; padding-left: 15px; border-left: 1px solid #e5e7eb;">
                                                            <p style="margin: 0 0 5px; color: #6b7280; font-size: 13px; font-weight: 600;">ESTIMATED ARRIVAL</p>
                                                            <p style="margin: 0; font-size: 18px; font-weight: 700; color: #059669;">{estimated_arrival}</p>
                                                            <p style="margin: 8px 0 0; color: #4b5563; font-size: 14px;">
                                                                Delivery: {delivery_info.get('zone_name', 'Standard')}<br>
                                                                {delivery_info.get('delivery_option', '')}
                                                            </p>
                                                        </td>
                                                    </tr>
                                                </table>
                                            </td>
                                        </tr>
                                    </table>
                                    
                                    <!-- What's Next -->
                                    <table role="presentation" style="width: 100%; background: #fef3c7; border-radius: 12px; margin-top: 25px;">
                                        <tr>
                                            <td style="padding: 20px;">
                                                <p style="margin: 0 0 10px; color: #92400e; font-weight: 600;">📧 What's Next?</p>
                                                <ul style="margin: 0; padding-left: 20px; color: #a16207;">
                                                    <li>You'll receive shipping confirmation with tracking details</li>
                                                    <li>Track your order anytime in your account</li>
                                                    <li>Contact us if you have any questions</li>
                                                </ul>
                                            </td>
                                        </tr>
                                    </table>
                                    
                                    <!-- CTA Button -->
                                    <table role="presentation" style="width: 100%; margin-top: 30px;">
                                        <tr>
                                            <td align="center">
                                                <a href="{self.site_url}/profile" style="display: inline-block; padding: 16px 40px; background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 16px;">
                                                    Track Your Order
                                                </a>
                                            </td>
                                        </tr>
                                    </table>
                                    
                                    <p style="margin: 30px 0 0; color: #6b7280;">
                                        Thank you for shopping with us!<br>
                                        <strong style="color: #1f2937;">The AfroMarket UK Team</strong>
                                    </p>
                                </td>
                            </tr>
                            
                            <!-- Footer -->
                            <tr>
                                <td style="padding: 30px; text-align: center; color: #9ca3af; font-size: 12px;">
                                    <p style="margin: 0;">Questions? Contact us at {self.admin_email}</p>
                                    <p style="margin: 10px 0 0;">&copy; 2025 AfroMarket UK. All rights reserved.</p>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """
        
        text_content = f"""
        Payment Confirmed - Order #{order_id}
        
        Hello {customer_name},
        
        Your payment has been successfully processed!
        
        Order Reference: #{order_id}
        Total Paid: £{total:.2f}
        Payment Method: {payment_method}
        
        Delivery Address:
        {shipping_info.get('fullName', customer_name)}
        {shipping_info.get('address', '')}
        {shipping_info.get('city', '')}, {shipping_info.get('postcode', '')}
        
        Estimated Arrival: {estimated_arrival}
        Delivery Fee: {'FREE' if delivery_fee == 0 else f'£{delivery_fee:.2f}'}
        
        You'll receive tracking information once your order ships.
        
        Thank you for shopping with AfroMarket UK!
        """
        
        return self.send_email(
            to_email=customer_email,
            subject=subject,
            html_content=html_content,
            text_content=text_content,
            duplicate_key=f"customer_payment_{order_id}"
        )

    def send_payment_notification_to_vendor(
        self,
        vendor_email: str,
        vendor_name: str,
        order_data: Dict[str, Any],
        vendor_items: List[Dict[str, Any]],
        customer_info: Dict[str, Any]
    ) -> bool:
        """
        Send comprehensive order notification to vendor after payment success
        
        Args:
            vendor_email: Vendor's email address
            vendor_name: Vendor's business name
            order_data: Full order data
            vendor_items: Only items belonging to this vendor
            customer_info: Customer details for this order
        """
        order_id = order_data.get('order_id', order_data.get('orderId', 'N/A'))
        shipping_info = order_data.get('shipping_info', order_data.get('shippingInfo', {}))
        delivery_info = order_data.get('delivery_info', {})
        
        # Calculate estimated arrival
        estimated_days = delivery_info.get('estimated_days', '3-5 days')
        now = datetime.utcnow()
        
        try:
            if 'Same day' in estimated_days:
                arrival_date = now
            elif 'Next day' in estimated_days:
                arrival_date = now + timedelta(days=1)
            else:
                import re
                match = re.search(r'(\d+)', estimated_days)
                days = int(match.group(1)) if match else 3
                arrival_date = now + timedelta(days=days + 1)
            
            estimated_arrival = arrival_date.strftime('%A, %d %B %Y')
        except:
            estimated_arrival = f"Within {estimated_days}"
        
        # Build items HTML and calculate totals
        items_html = ""
        vendor_total = 0
        
        for item in vendor_items:
            price = float(item.get('price', 0))
            qty = int(item.get('quantity', 1))
            item_total = price * qty
            vendor_total += item_total
            
            items_html += f"""
            <tr>
                <td style="padding: 12px; border-bottom: 1px solid #e5e7eb;">
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <img src="{item.get('image', '')}" alt="" style="width: 50px; height: 50px; border-radius: 6px; object-fit: cover; background: #f3f4f6;">
                        <span style="font-weight: 500; color: #1f2937;">{item.get('name', 'Product')}</span>
                    </div>
                </td>
                <td style="padding: 12px; border-bottom: 1px solid #e5e7eb; text-align: center;">{qty}</td>
                <td style="padding: 12px; border-bottom: 1px solid #e5e7eb; text-align: right;">£{price:.2f}</td>
                <td style="padding: 12px; border-bottom: 1px solid #e5e7eb; text-align: right; font-weight: 600;">£{item_total:.2f}</td>
            </tr>
            """
        
        # Calculate commission and earnings
        commission_rate = 0.10  # 10% platform fee
        commission = vendor_total * commission_rate
        vendor_earning = vendor_total - commission
        
        subject = f"🎉 New Order Received - #{order_id}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
        </head>
        <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f4f4;">
            <table role="presentation" style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td align="center" style="padding: 20px;">
                        <table role="presentation" style="width: 100%; max-width: 600px; border-collapse: collapse;">
                            <!-- Header -->
                            <tr>
                                <td style="background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%); padding: 35px 30px; text-align: center; border-radius: 16px 16px 0 0;">
                                    <h1 style="margin: 0; color: white; font-size: 26px;">🎉 New Order Received!</h1>
                                    <p style="margin: 10px 0 0; color: rgba(255,255,255,0.9);">Order #{order_id}</p>
                                </td>
                            </tr>
                            
                            <!-- Content -->
                            <tr>
                                <td style="background: white; padding: 35px 30px; border-radius: 0 0 16px 16px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                                    <p style="margin: 0 0 20px; font-size: 16px;">Hello <strong>{vendor_name}</strong>,</p>
                                    
                                    <p style="margin: 0 0 25px; color: #4b5563;">
                                        Great news! You have received a new order. Payment has been confirmed - please prepare the items for shipment.
                                    </p>
                                    
                                    <!-- Customer Info Box -->
                                    <table role="presentation" style="width: 100%; background: #f0f9ff; border: 2px solid #0ea5e9; border-radius: 12px; margin-bottom: 25px;">
                                        <tr>
                                            <td style="padding: 20px;">
                                                <p style="margin: 0 0 15px; font-weight: 600; color: #0369a1; font-size: 15px;">👤 Customer Information</p>
                                                <table role="presentation" style="width: 100%;">
                                                    <tr>
                                                        <td style="padding: 5px 0; color: #64748b; width: 100px;">Name:</td>
                                                        <td style="padding: 5px 0; font-weight: 500;">{customer_info.get('name', shipping_info.get('fullName', 'N/A'))}</td>
                                                    </tr>
                                                    <tr>
                                                        <td style="padding: 5px 0; color: #64748b;">Email:</td>
                                                        <td style="padding: 5px 0;">{customer_info.get('email', 'N/A')}</td>
                                                    </tr>
                                                    <tr>
                                                        <td style="padding: 5px 0; color: #64748b;">Phone:</td>
                                                        <td style="padding: 5px 0;">{shipping_info.get('phone', 'N/A')}</td>
                                                    </tr>
                                                </table>
                                            </td>
                                        </tr>
                                    </table>
                                    
                                    <!-- Delivery Address -->
                                    <table role="presentation" style="width: 100%; background: #f9fafb; border-radius: 12px; margin-bottom: 25px;">
                                        <tr>
                                            <td style="padding: 20px;">
                                                <p style="margin: 0 0 10px; font-weight: 600; color: #1f2937; font-size: 15px;">📍 Delivery Address</p>
                                                <p style="margin: 0; color: #4b5563;">
                                                    {shipping_info.get('fullName', customer_info.get('name', 'N/A'))}<br>
                                                    {shipping_info.get('address', 'N/A')}<br>
                                                    {shipping_info.get('city', '')}, {shipping_info.get('postcode', '')}<br>
                                                    Phone: {shipping_info.get('phone', 'N/A')}
                                                </p>
                                                <p style="margin: 15px 0 0; padding-top: 15px; border-top: 1px solid #e5e7eb;">
                                                    <strong style="color: #059669;">Estimated Arrival: {estimated_arrival}</strong><br>
                                                    <span style="color: #6b7280; font-size: 14px;">Delivery: {delivery_info.get('delivery_option', 'Standard')} - {delivery_info.get('zone_name', '')}</span>
                                                </p>
                                            </td>
                                        </tr>
                                    </table>
                                    
                                    <!-- Order Items -->
                                    <h3 style="margin: 25px 0 15px; font-size: 16px; color: #1f2937; border-bottom: 2px solid #e5e7eb; padding-bottom: 10px;">
                                        📦 Items to Ship
                                    </h3>
                                    <table role="presentation" style="width: 100%; border-collapse: collapse;">
                                        <thead>
                                            <tr style="background: #f3f4f6;">
                                                <th style="padding: 12px; text-align: left; font-weight: 600; color: #4b5563;">Product</th>
                                                <th style="padding: 12px; text-align: center; font-weight: 600; color: #4b5563;">Qty</th>
                                                <th style="padding: 12px; text-align: right; font-weight: 600; color: #4b5563;">Price</th>
                                                <th style="padding: 12px; text-align: right; font-weight: 600; color: #4b5563;">Total</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {items_html}
                                        </tbody>
                                    </table>
                                    
                                    <!-- Earnings Box -->
                                    <table role="presentation" style="width: 100%; background: #f0fdf4; border: 2px solid #10b981; border-radius: 12px; margin-top: 25px;">
                                        <tr>
                                            <td style="padding: 20px;">
                                                <p style="margin: 0 0 15px; font-weight: 600; color: #059669; font-size: 16px;">💰 Your Earnings</p>
                                                <table role="presentation" style="width: 100%;">
                                                    <tr>
                                                        <td style="padding: 8px 0; color: #4b5563;">Order Total</td>
                                                        <td style="padding: 8px 0; text-align: right;">£{vendor_total:.2f}</td>
                                                    </tr>
                                                    <tr>
                                                        <td style="padding: 8px 0; color: #4b5563;">Platform Fee (10%)</td>
                                                        <td style="padding: 8px 0; text-align: right; color: #ef4444;">-£{commission:.2f}</td>
                                                    </tr>
                                                    <tr style="border-top: 2px solid #10b981;">
                                                        <td style="padding: 12px 0 0; font-size: 18px; font-weight: 700; color: #059669;">Your Earning</td>
                                                        <td style="padding: 12px 0 0; text-align: right; font-size: 20px; font-weight: 700; color: #059669;">£{vendor_earning:.2f}</td>
                                                    </tr>
                                                </table>
                                            </td>
                                        </tr>
                                    </table>
                                    
                                    <!-- Action Required -->
                                    <table role="presentation" style="width: 100%; background: #fef3c7; border-radius: 12px; margin-top: 25px;">
                                        <tr>
                                            <td style="padding: 20px;">
                                                <p style="margin: 0 0 10px; color: #92400e; font-weight: 600;">⚡ Action Required</p>
                                                <p style="margin: 0; color: #a16207;">
                                                    Please prepare and ship this order as soon as possible. 
                                                    Update the tracking information in your vendor dashboard once shipped.
                                                </p>
                                            </td>
                                        </tr>
                                    </table>
                                    
                                    <!-- CTA -->
                                    <table role="presentation" style="width: 100%; margin-top: 30px;">
                                        <tr>
                                            <td align="center">
                                                <a href="{self.site_url}/vendor/orders" style="display: inline-block; padding: 14px 35px; background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%); color: white; text-decoration: none; border-radius: 8px; font-weight: 600;">
                                                    View Order Details
                                                </a>
                                            </td>
                                        </tr>
                                    </table>
                                    
                                    <p style="margin: 30px 0 0; color: #6b7280;">
                                        Thank you for selling on AfroMarket UK!<br>
                                        <strong style="color: #1f2937;">The AfroMarket UK Team</strong>
                                    </p>
                                </td>
                            </tr>
                            
                            <!-- Footer -->
                            <tr>
                                <td style="padding: 25px; text-align: center; color: #9ca3af; font-size: 12px;">
                                    <p style="margin: 0;">&copy; 2025 AfroMarket UK. All rights reserved.</p>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """
        
        return self.send_email(
            to_email=vendor_email,
            subject=subject,
            html_content=html_content,
            duplicate_key=f"vendor_payment_{order_id}_{vendor_email}"
        )

    def send_payment_notification_to_admin(
        self,
        order_data: Dict[str, Any],
        customer_info: Dict[str, Any],
        vendors_info: List[Dict[str, Any]]
    ) -> bool:
        """
        Send comprehensive payment notification to platform admin/owner
        
        Args:
            order_data: Full order data
            customer_info: Customer details
            vendors_info: List of vendors and their items in this order
        """
        order_id = order_data.get('order_id', order_data.get('orderId', 'N/A'))
        shipping_info = order_data.get('shipping_info', order_data.get('shippingInfo', {}))
        delivery_info = order_data.get('delivery_info', {})
        items = order_data.get('items', [])
        subtotal = order_data.get('subtotal', 0)
        delivery_fee = order_data.get('delivery_fee', order_data.get('deliveryFee', 0))
        total = order_data.get('total', subtotal + delivery_fee)
        payment_method = order_data.get('payment_method', 'Card')
        
        now = datetime.utcnow()
        
        # Build items HTML
        items_html = ""
        for item in items:
            price = float(item.get('price', 0))
            qty = int(item.get('quantity', 1))
            item_total = price * qty
            items_html += f"""
            <tr>
                <td style="padding: 10px; border-bottom: 1px solid #e5e7eb;">{item.get('name', 'Product')}</td>
                <td style="padding: 10px; border-bottom: 1px solid #e5e7eb;">{item.get('vendor_name', 'N/A')}</td>
                <td style="padding: 10px; border-bottom: 1px solid #e5e7eb; text-align: center;">{qty}</td>
                <td style="padding: 10px; border-bottom: 1px solid #e5e7eb; text-align: right;">£{item_total:.2f}</td>
            </tr>
            """
        
        # Build vendors summary
        vendors_html = ""
        total_commission = 0
        for vendor in vendors_info:
            vendor_total = sum(float(i.get('price', 0)) * int(i.get('quantity', 1)) for i in vendor.get('items', []))
            commission = vendor_total * 0.10
            total_commission += commission
            vendors_html += f"""
            <tr>
                <td style="padding: 10px; border-bottom: 1px solid #e5e7eb;">{vendor.get('name', 'Unknown')}</td>
                <td style="padding: 10px; border-bottom: 1px solid #e5e7eb;">{vendor.get('email', 'N/A')}</td>
                <td style="padding: 10px; border-bottom: 1px solid #e5e7eb; text-align: right;">£{vendor_total:.2f}</td>
                <td style="padding: 10px; border-bottom: 1px solid #e5e7eb; text-align: right; color: #10b981;">£{commission:.2f}</td>
            </tr>
            """
        
        subject = f"💰 New Payment Received - Order #{order_id} (£{total:.2f})"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
        </head>
        <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f4f4;">
            <table role="presentation" style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td align="center" style="padding: 20px;">
                        <table role="presentation" style="width: 100%; max-width: 650px; border-collapse: collapse;">
                            <!-- Header -->
                            <tr>
                                <td style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); padding: 35px 30px; text-align: center; border-radius: 16px 16px 0 0;">
                                    <h1 style="margin: 0; color: white; font-size: 26px;">💰 New Payment Received!</h1>
                                    <p style="margin: 10px 0 0; color: rgba(255,255,255,0.9);">Order #{order_id}</p>
                                </td>
                            </tr>
                            
                            <!-- Content -->
                            <tr>
                                <td style="background: white; padding: 35px 30px; border-radius: 0 0 16px 16px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                                    
                                    <!-- Summary Box -->
                                    <table role="presentation" style="width: 100%; margin-bottom: 25px;">
                                        <tr>
                                            <td style="background: #f0fdf4; padding: 20px; border-radius: 12px; text-align: center; width: 33%;">
                                                <p style="margin: 0 0 5px; color: #6b7280; font-size: 13px;">Order Total</p>
                                                <p style="margin: 0; font-size: 24px; font-weight: 700; color: #059669;">£{total:.2f}</p>
                                            </td>
                                            <td style="width: 10px;"></td>
                                            <td style="background: #fef3c7; padding: 20px; border-radius: 12px; text-align: center; width: 33%;">
                                                <p style="margin: 0 0 5px; color: #6b7280; font-size: 13px;">Platform Commission</p>
                                                <p style="margin: 0; font-size: 24px; font-weight: 700; color: #d97706;">£{total_commission:.2f}</p>
                                            </td>
                                            <td style="width: 10px;"></td>
                                            <td style="background: #f0f9ff; padding: 20px; border-radius: 12px; text-align: center; width: 33%;">
                                                <p style="margin: 0 0 5px; color: #6b7280; font-size: 13px;">Vendors</p>
                                                <p style="margin: 0; font-size: 24px; font-weight: 700; color: #0ea5e9;">{len(vendors_info)}</p>
                                            </td>
                                        </tr>
                                    </table>
                                    
                                    <!-- Order Details -->
                                    <table role="presentation" style="width: 100%; background: #f9fafb; border-radius: 12px; margin-bottom: 25px;">
                                        <tr>
                                            <td style="padding: 20px;">
                                                <table role="presentation" style="width: 100%;">
                                                    <tr>
                                                        <td style="width: 50%;">
                                                            <p style="margin: 0 0 5px; color: #6b7280; font-size: 13px; font-weight: 600;">CUSTOMER</p>
                                                            <p style="margin: 0; font-weight: 600; color: #1f2937;">{customer_info.get('name', 'N/A')}</p>
                                                            <p style="margin: 3px 0 0; color: #4b5563; font-size: 14px;">{customer_info.get('email', 'N/A')}</p>
                                                        </td>
                                                        <td style="width: 50%;">
                                                            <p style="margin: 0 0 5px; color: #6b7280; font-size: 13px; font-weight: 600;">PAYMENT</p>
                                                            <p style="margin: 0; font-weight: 600; color: #1f2937;">{payment_method}</p>
                                                            <p style="margin: 3px 0 0; color: #4b5563; font-size: 14px;">{now.strftime('%d %B %Y, %H:%M')}</p>
                                                        </td>
                                                    </tr>
                                                    <tr>
                                                        <td colspan="2" style="padding-top: 15px;">
                                                            <p style="margin: 0 0 5px; color: #6b7280; font-size: 13px; font-weight: 600;">DELIVERY ADDRESS</p>
                                                            <p style="margin: 0; color: #4b5563;">
                                                                {shipping_info.get('address', 'N/A')}, {shipping_info.get('city', '')}, {shipping_info.get('postcode', '')}
                                                            </p>
                                                        </td>
                                                    </tr>
                                                </table>
                                            </td>
                                        </tr>
                                    </table>
                                    
                                    <!-- Items -->
                                    <h3 style="margin: 25px 0 15px; font-size: 15px; color: #1f2937;">📦 Order Items</h3>
                                    <table role="presentation" style="width: 100%; border-collapse: collapse; font-size: 14px;">
                                        <thead>
                                            <tr style="background: #f3f4f6;">
                                                <th style="padding: 10px; text-align: left;">Product</th>
                                                <th style="padding: 10px; text-align: left;">Vendor</th>
                                                <th style="padding: 10px; text-align: center;">Qty</th>
                                                <th style="padding: 10px; text-align: right;">Total</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {items_html}
                                        </tbody>
                                    </table>
                                    
                                    <!-- Vendors Breakdown -->
                                    <h3 style="margin: 25px 0 15px; font-size: 15px; color: #1f2937;">🏪 Vendor Breakdown</h3>
                                    <table role="presentation" style="width: 100%; border-collapse: collapse; font-size: 14px;">
                                        <thead>
                                            <tr style="background: #f3f4f6;">
                                                <th style="padding: 10px; text-align: left;">Vendor</th>
                                                <th style="padding: 10px; text-align: left;">Email</th>
                                                <th style="padding: 10px; text-align: right;">Sales</th>
                                                <th style="padding: 10px; text-align: right;">Commission</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {vendors_html}
                                        </tbody>
                                        <tfoot>
                                            <tr style="background: #f0fdf4; font-weight: 600;">
                                                <td colspan="2" style="padding: 12px;">Total</td>
                                                <td style="padding: 12px; text-align: right;">£{subtotal:.2f}</td>
                                                <td style="padding: 12px; text-align: right; color: #059669;">£{total_commission:.2f}</td>
                                            </tr>
                                        </tfoot>
                                    </table>
                                    
                                    <!-- CTA -->
                                    <table role="presentation" style="width: 100%; margin-top: 30px;">
                                        <tr>
                                            <td align="center">
                                                <a href="{self.site_url}/owner" style="display: inline-block; padding: 14px 35px; background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: white; text-decoration: none; border-radius: 8px; font-weight: 600;">
                                                    View in Dashboard
                                                </a>
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                            
                            <!-- Footer -->
                            <tr>
                                <td style="padding: 25px; text-align: center; color: #9ca3af; font-size: 12px;">
                                    <p style="margin: 0;">This is an automated admin notification from AfroMarket UK</p>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """
        
        return self.send_email(
            to_email=self.admin_email,
            subject=subject,
            html_content=html_content,
            duplicate_key=f"admin_payment_{order_id}"
        )

    async def send_all_payment_notifications(
        self,
        order_data: Dict[str, Any],
        customer_info: Dict[str, Any],
        vendors_data: List[Dict[str, Any]],
        db_service: Any = None
    ) -> Dict[str, bool]:
        """
        Send all payment notifications (customer, vendors, admin) after successful payment
        
        Args:
            order_data: Full order data including items, shipping, delivery info
            customer_info: Customer name and email
            vendors_data: List of vendor info with their items
            db_service: Database service to fetch vendor emails if needed
            
        Returns:
            Dict with status for each notification type
        """
        results = {
            'customer': False,
            'vendors': {},
            'admin': False
        }
        
        order_id = order_data.get('order_id', order_data.get('orderId', 'N/A'))
        logger.info(f"Sending payment notifications for order #{order_id}")
        
        # 1. Send to customer
        try:
            results['customer'] = self.send_payment_confirmation_to_customer(
                customer_email=customer_info.get('email'),
                customer_name=customer_info.get('name'),
                order_data=order_data
            )
            logger.info(f"Customer notification sent: {results['customer']}")
        except Exception as e:
            logger.error(f"Failed to send customer notification: {str(e)}")
        
        # 2. Send to each vendor
        for vendor in vendors_data:
            vendor_id = vendor.get('id', vendor.get('vendor_id', 'unknown'))
            try:
                success = self.send_payment_notification_to_vendor(
                    vendor_email=vendor.get('email'),
                    vendor_name=vendor.get('name', vendor.get('business_name', 'Vendor')),
                    order_data=order_data,
                    vendor_items=vendor.get('items', []),
                    customer_info=customer_info
                )
                results['vendors'][vendor_id] = success
                logger.info(f"Vendor {vendor_id} notification sent: {success}")
            except Exception as e:
                logger.error(f"Failed to send vendor {vendor_id} notification: {str(e)}")
                results['vendors'][vendor_id] = False
        
        # 3. Send to admin
        try:
            results['admin'] = self.send_payment_notification_to_admin(
                order_data=order_data,
                customer_info=customer_info,
                vendors_info=vendors_data
            )
            logger.info(f"Admin notification sent: {results['admin']}")
        except Exception as e:
            logger.error(f"Failed to send admin notification: {str(e)}")
        
        return results

    def send_vendor_approval_notification(
        self,
        vendor_email: str,
        vendor_name: str,
        approved: bool,
        admin_notes: str = ""
    ) -> bool:
        """
        Send vendor approval/rejection notification after admin decision
        
        Args:
            vendor_email: Vendor's email
            vendor_name: Vendor's business name
            approved: True if approved, False if rejected
            admin_notes: Optional notes from admin
        """
        if approved:
            subject = "🎉 Congratulations! Your AfroMarket UK Vendor Account is Approved!"
            
            notes_html = ""
            if admin_notes:
                notes_html = f"""
                <table role="presentation" style="width: 100%; background: #f0f9ff; border-radius: 12px; margin: 25px 0;">
                    <tr>
                        <td style="padding: 20px;">
                            <p style="margin: 0 0 10px; font-weight: 600; color: #0369a1;">📝 Note from Admin</p>
                            <p style="margin: 0; color: #0ea5e9;">{admin_notes}</p>
                        </td>
                    </tr>
                </table>
                """
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f4f4;">
                <table role="presentation" style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td align="center" style="padding: 20px;">
                            <table role="presentation" style="width: 100%; max-width: 600px;">
                                <!-- Header -->
                                <tr>
                                    <td style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); padding: 50px 30px; text-align: center; border-radius: 16px 16px 0 0;">
                                        <div style="width: 80px; height: 80px; background: rgba(255,255,255,0.2); border-radius: 50%; margin: 0 auto 20px; line-height: 80px; font-size: 40px;">✓</div>
                                        <h1 style="margin: 0; color: white; font-size: 28px;">You're Approved!</h1>
                                        <p style="margin: 15px 0 0; color: rgba(255,255,255,0.9); font-size: 16px;">Welcome to AfroMarket UK</p>
                                    </td>
                                </tr>
                                
                                <!-- Content -->
                                <tr>
                                    <td style="background: white; padding: 40px 30px; border-radius: 0 0 16px 16px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                                        <p style="margin: 0 0 20px; font-size: 17px;">Hello <strong>{vendor_name}</strong>,</p>
                                        
                                        <p style="margin: 0 0 25px; color: #4b5563; font-size: 16px; line-height: 1.6;">
                                            Great news! Your vendor application has been <strong style="color: #059669;">approved</strong>. 
                                            You can now start adding products and reaching thousands of customers across the UK!
                                        </p>
                                        
                                        {notes_html}
                                        
                                        <!-- What you can do -->
                                        <table role="presentation" style="width: 100%; background: #f0fdf4; border-radius: 12px; margin: 25px 0;">
                                            <tr>
                                                <td style="padding: 25px;">
                                                    <p style="margin: 0 0 15px; font-weight: 600; color: #059669; font-size: 16px;">🚀 Get Started Now</p>
                                                    <table role="presentation" style="width: 100%;">
                                                        <tr>
                                                            <td style="padding: 8px 0; color: #047857;">✅ Add your products to the marketplace</td>
                                                        </tr>
                                                        <tr>
                                                            <td style="padding: 8px 0; color: #047857;">✅ Set up your store profile</td>
                                                        </tr>
                                                        <tr>
                                                            <td style="padding: 8px 0; color: #047857;">✅ Start receiving orders from customers</td>
                                                        </tr>
                                                        <tr>
                                                            <td style="padding: 8px 0; color: #047857;">✅ Track your sales and earnings</td>
                                                        </tr>
                                                    </table>
                                                </td>
                                            </tr>
                                        </table>
                                        
                                        <!-- CTA -->
                                        <table role="presentation" style="width: 100%; margin: 30px 0;">
                                            <tr>
                                                <td align="center">
                                                    <a href="{self.site_url}/vendor/dashboard" style="display: inline-block; padding: 18px 50px; background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; text-decoration: none; border-radius: 10px; font-weight: 600; font-size: 16px; box-shadow: 0 4px 14px rgba(16, 185, 129, 0.4);">
                                                        Go to Your Dashboard →
                                                    </a>
                                                </td>
                                            </tr>
                                        </table>
                                        
                                        <p style="margin: 25px 0 0; color: #6b7280; font-size: 14px;">
                                            If you have any questions, don't hesitate to contact us at {self.admin_email}
                                        </p>
                                        
                                        <p style="margin: 25px 0 0;">
                                            Welcome aboard!<br>
                                            <strong style="color: #1f2937;">The AfroMarket UK Team</strong>
                                        </p>
                                    </td>
                                </tr>
                                
                                <!-- Footer -->
                                <tr>
                                    <td style="padding: 30px; text-align: center; color: #9ca3af; font-size: 12px;">
                                        <p style="margin: 0;">&copy; 2025 AfroMarket UK. All rights reserved.</p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
            </body>
            </html>
            """
        else:
            # Rejection email
            subject = "Update on Your AfroMarket UK Vendor Application"
            
            notes_html = ""
            if admin_notes:
                notes_html = f"""
                <table role="presentation" style="width: 100%; background: #fef2f2; border-left: 4px solid #ef4444; border-radius: 0 8px 8px 0; margin: 25px 0;">
                    <tr>
                        <td style="padding: 20px;">
                            <p style="margin: 0 0 10px; font-weight: 600; color: #991b1b;">Reason:</p>
                            <p style="margin: 0; color: #dc2626;">{admin_notes}</p>
                        </td>
                    </tr>
                </table>
                """
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f4f4;">
                <table role="presentation" style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td align="center" style="padding: 20px;">
                            <table role="presentation" style="width: 100%; max-width: 600px;">
                                <!-- Header -->
                                <tr>
                                    <td style="background: #6b7280; padding: 40px 30px; text-align: center; border-radius: 16px 16px 0 0;">
                                        <h1 style="margin: 0; color: white; font-size: 24px;">Application Update</h1>
                                        <p style="margin: 10px 0 0; color: rgba(255,255,255,0.8);">AfroMarket UK</p>
                                    </td>
                                </tr>
                                
                                <!-- Content -->
                                <tr>
                                    <td style="background: white; padding: 40px 30px; border-radius: 0 0 16px 16px;">
                                        <p style="margin: 0 0 20px; font-size: 17px;">Hello <strong>{vendor_name}</strong>,</p>
                                        
                                        <p style="margin: 0 0 25px; color: #4b5563; line-height: 1.6;">
                                            Thank you for your interest in becoming a vendor on AfroMarket UK. 
                                            After careful review, we regret to inform you that we are unable to approve your application at this time.
                                        </p>
                                        
                                        {notes_html}
                                        
                                        <p style="margin: 25px 0; color: #4b5563; line-height: 1.6;">
                                            This decision is not final. You're welcome to address the concerns mentioned above and reapply in the future. 
                                            If you believe this decision was made in error, please contact us.
                                        </p>
                                        
                                        <p style="margin: 25px 0 0; color: #6b7280;">
                                            Best regards,<br>
                                            <strong>The AfroMarket UK Team</strong>
                                        </p>
                                    </td>
                                </tr>
                                
                                <!-- Footer -->
                                <tr>
                                    <td style="padding: 30px; text-align: center; color: #9ca3af; font-size: 12px;">
                                        <p style="margin: 0;">Contact us: {self.admin_email}</p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
            </body>
            </html>
            """
        
        return self.send_email(
            to_email=vendor_email,
            subject=subject,
            html_content=html_content,
            duplicate_key=f"vendor_approval_{vendor_email}_{approved}"
        )

    def send_order_status_update(self, to_email: str, customer_name: str, order_data: dict, new_status: str, tracking_info: dict = None):
        """Send email notification when order status changes"""
        order_id = order_data.get('order_id', order_data.get('orderId', 'N/A'))
        
        status_config = {
            'processing': {'emoji': '⚙️', 'title': 'Order Processing', 'color': '#3b82f6', 'message': 'We are preparing your order for shipment.'},
            'shipped': {'emoji': '📦', 'title': 'Order Shipped', 'color': '#8b5cf6', 'message': 'Great news! Your order is on its way.'},
            'in_transit': {'emoji': '🚚', 'title': 'In Transit', 'color': '#6366f1', 'message': 'Your package is currently in transit.'},
            'out_for_delivery': {'emoji': '🏃', 'title': 'Out for Delivery', 'color': '#f59e0b', 'message': 'Your package is out for delivery today!'},
            'delivered': {'emoji': '✅', 'title': 'Delivered', 'color': '#10b981', 'message': 'Your order has been delivered successfully.'},
            'cancelled': {'emoji': '❌', 'title': 'Order Cancelled', 'color': '#ef4444', 'message': 'Your order has been cancelled.'},
        }
        
        config = status_config.get(new_status, {'emoji': '📋', 'title': 'Status Update', 'color': '#6b7280', 'message': f'Your order status has been updated to: {new_status}'})
        
        tracking_html = ""
        if tracking_info and tracking_info.get('tracking_number'):
            tracking_html = f"""
            <div style="background: #f0f9ff; border-left: 4px solid #0284c7; padding: 15px 20px; margin: 20px 0; border-radius: 0 8px 8px 0;">
                <p style="font-weight: 600; color: #0369a1; margin: 0 0 10px;">📍 Tracking Information</p>
                <p style="margin: 5px 0; color: #0c4a6e;">
                    <strong>Tracking Number:</strong> {tracking_info.get('tracking_number', 'N/A')}
                </p>
                <p style="margin: 5px 0; color: #0c4a6e;">
                    <strong>Carrier:</strong> {tracking_info.get('carrier', 'N/A')}
                </p>
                {f"<p style='margin: 5px 0; color: #0c4a6e;'><strong>Estimated Delivery:</strong> {tracking_info.get('estimated_delivery')}</p>" if tracking_info.get('estimated_delivery') else ""}
            </div>
            """
        
        subject = f"{config['emoji']} Order #{order_id} - {config['title']}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f4f4f4; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, {config['color']} 0%, {config['color']}dd 100%); color: white; padding: 40px 30px; text-align: center; border-radius: 16px 16px 0 0; }}
                .content {{ background: white; padding: 40px 30px; border-radius: 0 0 16px 16px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); }}
                .status-badge {{ display: inline-block; padding: 10px 25px; background: {config['color']}22; color: {config['color']}; border-radius: 25px; font-weight: 600; font-size: 14px; margin: 20px 0; }}
                .footer {{ text-align: center; padding: 30px 20px; color: #9ca3af; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 style="font-size: 48px; margin: 0;">{config['emoji']}</h1>
                    <h2 style="margin: 10px 0 0;">{config['title']}</h2>
                    <p style="margin: 5px 0 0; opacity: 0.9;">Order #{order_id}</p>
                </div>
                <div class="content">
                    <p style="font-size: 18px; color: #1f2937;">Hello {customer_name},</p>
                    <p style="color: #4b5563;">{config['message']}</p>
                    
                    <div style="text-align: center;">
                        <span class="status-badge">{new_status.upper().replace('_', ' ')}</span>
                    </div>
                    
                    {tracking_html}
                    
                    <div style="text-align: center; margin-top: 30px;">
                        <a href="{self.site_url}/track-order/{order_id}" style="display: inline-block; padding: 14px 35px; background: {config['color']}; color: white; text-decoration: none; border-radius: 8px; font-weight: 600;">Track Your Order</a>
                    </div>
                </div>
                <div class="footer">
                    <p>Thank you for shopping with AfroMarket UK!</p>
                    <p>&copy; 2025 AfroMarket UK. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        {config['title']} - Order #{order_id}
        
        Hello {customer_name},
        
        {config['message']}
        
        Status: {new_status.upper().replace('_', ' ')}
        
        {f"Tracking Number: {tracking_info.get('tracking_number', 'N/A')}" if tracking_info else ""}
        {f"Carrier: {tracking_info.get('carrier', 'N/A')}" if tracking_info else ""}
        
        Track your order at: {self.site_url}/track-order/{order_id}
        
        Thank you for shopping with AfroMarket UK!
        """
        
        return self.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            text_content=text_content,
            duplicate_key=f"order_status_{order_id}_{new_status}"
        )


# Singleton instance
email_service = EmailService()