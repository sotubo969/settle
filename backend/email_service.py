import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from pathlib import Path
from typing import Optional
import logging
from dotenv import load_dotenv

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        # Reload environment variables to ensure they're loaded
        load_dotenv(ROOT_DIR / '.env')
        
        self.smtp_host = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.environ.get('SMTP_PORT', '587'))
        self.smtp_user = os.environ.get('SMTP_USER', '')
        self.smtp_password = os.environ.get('SMTP_PASSWORD', '')
        self.from_email = os.environ.get('FROM_EMAIL', self.smtp_user)
        self.admin_email = os.environ.get('ADMIN_EMAIL', 'sotubodammy@gmail.com')
        
        # Log configuration status
        if self.smtp_user and self.smtp_password:
            logger.info(f"Email service initialized with SMTP user: {self.smtp_user}")
        else:
            logger.warning("Email service: SMTP credentials not configured")
    
    def send_email(self, to_email: str, subject: str, html_content: str, text_content: Optional[str] = None):
        """Send an email"""
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
                return True
            else:
                logger.warning("SMTP credentials not configured. Email not sent.")
                # In development, just log the email content
                logger.info(f"\n{'='*50}\nEMAIL PREVIEW\nTo: {to_email}\nSubject: {subject}\n{'-'*50}\n{html_content}\n{'='*50}")
                return False
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
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
                            <a href="https://afrobasket.preview.emergentagent.com/vendor/dashboard" class="button">Go to Dashboard</a>
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
                        <a href="https://afrobasket.preview.emergentagent.com/login" class="button">Login to Your Account</a>
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
                        <a href="https://code-fetcher-23.preview.emergentagent.com/profile" class="button">Track Your Order</a>
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

# Singleton instance
email_service = EmailService()