import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.smtp_host = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.environ.get('SMTP_PORT', '587'))
        self.smtp_user = os.environ.get('SMTP_USER', '')
        self.smtp_password = os.environ.get('SMTP_PASSWORD', '')
        self.from_email = os.environ.get('FROM_EMAIL', self.smtp_user)
        self.admin_email = os.environ.get('ADMIN_EMAIL', 'sotubodammy@gmail.com')
    
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
                            <a href="https://sourcecode-fetch.preview.emergentagent.com/vendor/dashboard" class="button">Go to Dashboard</a>
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

# Singleton instance
email_service = EmailService()