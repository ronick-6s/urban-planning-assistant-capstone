"""
iCloud Mail SMTP Integration for Urban Planning Assistant
Handles sending email reports and notifications
"""

import smtplib
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import datetime
from typing import Optional, List, Dict, Any
from cloud_config import get_icloud_config, get_email_template
import logging

logger = logging.getLogger(__name__)

class EmailManager:
    """Manages email operations using iCloud SMTP."""
    
    def __init__(self):
        """Initialize email client with iCloud configuration."""
        try:
            self.config = get_icloud_config()
            self.template_config = get_email_template()
            self.smtp_server = None
        except ValueError as e:
            logger.warning(f"iCloud email configuration incomplete: {e}")
            self.config = None
    
    def _connect_smtp(self) -> bool:
        """
        Establish SMTP connection to iCloud mail server.
        
        Returns:
            True if connection successful, False otherwise
        """
        if not self.config:
            return False
        
        try:
            self.smtp_server = smtplib.SMTP(
                self.config["smtp_server"], 
                self.config["smtp_port"]
            )
            
            if self.config["use_tls"]:
                self.smtp_server.starttls()
            
            self.smtp_server.login(
                self.config["email"],
                self.config["password"]
            )
            
            logger.info("Successfully connected to iCloud SMTP server")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to iCloud SMTP: {e}")
            if self.smtp_server:
                try:
                    self.smtp_server.quit()
                except:
                    pass
                self.smtp_server = None
            return False
    
    def _disconnect_smtp(self):
        """Disconnect from SMTP server."""
        if self.smtp_server:
            try:
                self.smtp_server.quit()
            except:
                pass
            self.smtp_server = None
    
    def send_report_email(self, recipient_email: str, user_id: str, 
                         report_content: str, attachments: Optional[List[Dict[str, Any]]] = None,
                         dropbox_links: Optional[List[str]] = None) -> bool:
        """
        Send a chat history report via email.
        
        Args:
            recipient_email: Email address to send to
            user_id: ID of the user
            report_content: Text content of the report
            attachments: List of attachment dictionaries with 'content', 'filename', 'content_type'
            dropbox_links: List of Dropbox share URLs
            
        Returns:
            True if email sent successfully, False otherwise
        """
        if not self.config:
            logger.error("Email configuration not available")
            return False
        
        try:
            # Connect to SMTP server
            if not self._connect_smtp():
                return False
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.config['sender_name']} <{self.config['email']}>"
            msg['To'] = recipient_email
            msg['Subject'] = self.template_config['subject']
            
            # Create email body
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Text version
            text_body = self._create_text_email_body(user_id, report_content, dropbox_links, timestamp)
            text_part = MIMEText(text_body, 'plain')
            msg.attach(text_part)
            
            # HTML version
            html_body = self._create_html_email_body(user_id, report_content, dropbox_links, timestamp)
            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)
            
            # Add attachments if provided
            if attachments:
                for attachment in attachments:
                    try:
                        part = MIMEApplication(
                            attachment['content'],
                            attachment.get('content_type', 'application/octet-stream')
                        )
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename="{attachment["filename"]}"'
                        )
                        msg.attach(part)
                    except Exception as attach_error:
                        logger.error(f"Failed to attach file {attachment.get('filename', 'unknown')}: {attach_error}")
            
            # Send email
            self.smtp_server.send_message(msg)
            logger.info(f"Successfully sent report email to {recipient_email}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
        
        finally:
            self._disconnect_smtp()
    
    def _create_text_email_body(self, user_id: str, report_content: str, 
                               dropbox_links: Optional[List[str]], timestamp: str) -> str:
        """Create plain text email body with README-style formatting."""
        body_parts = [
            "📧 Urban Planning Studio - Consultation Report Delivery",
            "=" * 60,
            "",
            self.template_config['greeting'],
            "",
            f"**User ID**: {user_id}",
            f"**Report Generated**: {timestamp}",
            f"**Format**: Professional README Documentation",
            "",
            "🎯 **What's Included:**",
            "- Comprehensive consultation summary",
            "- Structured conversation analysis", 
            "- Actionable recommendations",
            "- Key metrics and KPIs",
            "- Professional README formatting",
            "",
            self.template_config['body_intro'],
            "",
            "📋 **CONSULTATION REPORT:**",
            "=" * 60,
            "",
            report_content,
            "",
            "=" * 60,
            ""
        ]
        
        if dropbox_links:
            body_parts.extend([
                "☁️ **CLOUD STORAGE LINKS:**",
                "-" * 30,
                "Your report is also available in the cloud:",
                ""
            ])
            for i, link in enumerate(dropbox_links, 1):
                body_parts.append(f"🔗 **Link {i}**: {link}")
            body_parts.extend(["", "💡 These links provide direct access to your report files.", ""])
        
        body_parts.extend([
            "📞 **Next Steps:**",
            "- Review the detailed consultation summary",
            "- Consider the recommended action items",
            "- Contact us for follow-up consultations",
            "- Implement suggested strategies as appropriate",
            "",
            self.template_config['body_footer'],
            "",
            "🏙️ Urban Planning Studio",
            "Intelligent Urban Solutions for Sustainable Communities",
            "",
            self.template_config['signature'].format(timestamp=timestamp)
        ])
        
        return "\n".join(body_parts)
    
    def _create_html_email_body(self, user_id: str, report_content: str,
                               dropbox_links: Optional[List[str]], timestamp: str) -> str:
        """Create compact HTML email body with README-style formatting."""
        
        # Convert markdown-style content to HTML (condensed version)
        html_report = self._convert_readme_to_html_compact(report_content)
        
        html_body = f"""
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; line-height: 1.4; color: #333; background-color: #f8f9fa; margin: 0; padding: 0; font-size: 14px; }}
                .container {{ max-width: 700px; margin: 0 auto; background-color: white; }}
                .header {{ background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%); color: white; padding: 20px; text-align: center; }}
                .header h1 {{ margin: 0; font-size: 22px; font-weight: 600; }}
                .header .subtitle {{ margin: 8px 0 0 0; opacity: 0.9; font-size: 14px; }}
                .content {{ padding: 20px; }}
                .intro-section {{ background-color: #e8f4fd; padding: 15px; border-radius: 6px; border-left: 3px solid #0066cc; margin-bottom: 15px; }}
                .intro-section h3 {{ margin: 0 0 10px 0; font-size: 16px; }}
                .intro-section p {{ margin: 8px 0; }}
                .report-section {{ background-color: #f8f9fa; padding: 15px; border-radius: 6px; border: 1px solid #e1e4e8; margin: 15px 0; max-height: 400px; overflow-y: auto; }}
                .report-section h3 {{ margin: 0 0 10px 0; font-size: 16px; }}
                .report-content {{ font-family: 'SFMono-Regular', Monaco, Consolas, monospace; font-size: 12px; line-height: 1.3; }}
                .links-section {{ background-color: #fff3cd; padding: 15px; border-radius: 6px; border-left: 3px solid #ffc107; margin: 15px 0; }}
                .links-section h3 {{ margin: 0 0 10px 0; color: #856404; font-size: 16px; }}
                .links-section a {{ color: #0066cc; text-decoration: none; font-weight: 500; display: block; margin: 5px 0; }}
                .links-section a:hover {{ text-decoration: underline; }}
                .footer {{ background-color: #f8f9fa; padding: 15px; text-align: center; border-top: 1px solid #e1e4e8; }}
                .footer p {{ margin: 3px 0; color: #666; font-size: 12px; }}
                .badge {{ display: inline-block; padding: 3px 6px; background-color: #28a745; color: white; border-radius: 10px; font-size: 11px; font-weight: 600; }}
                .timestamp {{ color: #666; font-size: 12px; font-style: italic; }}
                .features {{ display: flex; flex-wrap: wrap; gap: 8px; margin: 10px 0; }}
                .feature {{ background-color: #e1f5fe; color: #01579b; padding: 4px 8px; border-radius: 12px; font-size: 11px; }}
                .summary-box {{ background-color: #f0f9ff; padding: 12px; border-radius: 6px; border-left: 3px solid #0ea5e9; margin: 10px 0; }}
                .summary-box h4 {{ margin: 0 0 8px 0; color: #0c4a6e; font-size: 14px; }}
                .summary-box ul {{ margin: 8px 0; padding-left: 20px; }}
                .summary-box li {{ margin: 3px 0; color: #164e63; font-size: 13px; }}
                @media (max-width: 600px) {{
                    .content {{ padding: 15px; }}
                    .features {{ justify-content: center; }}
                    .report-section {{ max-height: 300px; }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📋 Urban Planning Studio</h1>
                    <p class="subtitle">Consultation Report</p>
                    <p class="timestamp">{timestamp}</p>
                </div>
                
                <div class="content">
                    <div class="intro-section">
                        <h3>🎯 Report Summary</h3>
                        <p><strong>User:</strong> <code>{user_id}</code> | <strong>Format:</strong> <span class="badge">README Style</span></p>
                        
                        <div class="features">
                            <span class="feature">📊 Analysis</span>
                            <span class="feature">🎯 Recommendations</span>
                            <span class="feature">📋 Professional Format</span>
                        </div>
                        
                        <p style="margin: 10px 0 0 0;">{self.template_config['body_intro']}</p>
                    </div>
                    
                    <div class="report-section">
                        <h3>📝 Consultation Report (Scrollable)</h3>
                        <div class="report-content">
                            {html_report}
                        </div>
                    </div>
        """
        
        if dropbox_links:
            html_body += """
                    <div class="links-section">
                        <h3>☁️ Download Links</h3>
                        <p style="margin: 5px 0;">Access your complete reports:</p>
            """
            for i, link in enumerate(dropbox_links, 1):
                html_body += f'<a href="{link}" target="_blank">📎 Report {i} (PDF/HTML/TXT)</a>'
            html_body += """
                        <p style="font-size: 11px; color: #666; margin-top: 8px;">💡 Links provide permanent access to full reports.</p>
                    </div>
            """
        
        html_body += f"""
                    <div class="summary-box">
                        <h4>📞 Next Steps</h4>
                        <ul>
                            <li>Review consultation summary above</li>
                            <li>Download complete reports via links</li>
                            <li>Contact for follow-up consultations</li>
                            <li>Implement recommended strategies</li>
                        </ul>
                    </div>
                </div>
                
                <div class="footer">
                    <p><strong>🏙️ Urban Planning Studio</strong></p>
                    <p><em>Intelligent Urban Solutions for Sustainable Communities</em></p>
                    <p style="font-size: 11px; margin-top: 8px;">{self.template_config['signature'].format(timestamp=timestamp).replace(chr(10), '<br>')}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_body
    
    def _convert_readme_to_html(self, readme_content: str) -> str:
        """Convert README-style markdown content to HTML."""
        # Simple markdown to HTML conversion for email
        html_content = readme_content
        
        # Convert headers
        html_content = html_content.replace('# ', '<h1>').replace('\n# ', '</h1>\n<h1>')
        html_content = html_content.replace('## ', '<h2>').replace('\n## ', '</h2>\n<h2>')
        html_content = html_content.replace('### ', '<h3>').replace('\n### ', '</h3>\n<h3>')
        
        # Convert bold text
        html_content = html_content.replace('**', '<strong>').replace('**', '</strong>')
        
        # Convert italic text
        html_content = html_content.replace('*', '<em>').replace('*', '</em>')
        
        # Convert code blocks
        html_content = html_content.replace('`', '<code>').replace('`', '</code>')
        
        # Convert line breaks
        html_content = html_content.replace('\n', '<br>')
        
        # Convert tables (basic support)
        lines = html_content.split('<br>')
        processed_lines = []
        in_table = False
        
        for line in lines:
            if '|' in line and '---' not in line:
                if not in_table:
                    processed_lines.append('<table style="border-collapse: collapse; margin: 15px 0;">')
                    in_table = True
                
                cells = [cell.strip() for cell in line.split('|') if cell.strip()]
                row_html = '<tr>'
                for cell in cells:
                    row_html += f'<td style="border: 1px solid #ddd; padding: 8px;">{cell}</td>'
                row_html += '</tr>'
                processed_lines.append(row_html)
            else:
                if in_table:
                    processed_lines.append('</table>')
                    in_table = False
                processed_lines.append(line)
        
        if in_table:
            processed_lines.append('</table>')
        
        return '<br>'.join(processed_lines)
    
    def _convert_readme_to_html_compact(self, readme_content: str) -> str:
        """Convert README-style content to compact HTML for email."""
        # Truncate very long content
        if len(readme_content) > 3000:
            readme_content = readme_content[:3000] + "\n\n... (content truncated for email - see attached files for complete report)"
        
        html_content = readme_content
        
        # Convert headers (smaller sizes for email)
        html_content = html_content.replace('# ', '<h4 style="margin: 10px 0 5px 0; color: #2c3e50;">').replace('\n# ', '</h4>\n<h4 style="margin: 10px 0 5px 0; color: #2c3e50;">')
        html_content = html_content.replace('## ', '<h5 style="margin: 8px 0 4px 0; color: #34495e;">').replace('\n## ', '</h5>\n<h5 style="margin: 8px 0 4px 0; color: #34495e;">')
        html_content = html_content.replace('### ', '<h6 style="margin: 6px 0 3px 0; color: #5d6d7e;">').replace('\n### ', '</h6>\n<h6 style="margin: 6px 0 3px 0; color: #5d6d7e;">')
        
        # Convert bold text
        html_content = html_content.replace('**', '<strong>').replace('**', '</strong>')
        
        # Convert italic text  
        html_content = html_content.replace('*', '<em>').replace('*', '</em>')
        
        # Convert code blocks
        html_content = html_content.replace('`', '<code style="background-color: #f6f8fa; padding: 2px 4px; border-radius: 3px; font-size: 11px;">').replace('`', '</code>')
        
        # Convert line breaks
        html_content = html_content.replace('\n', '<br>')
        
        # Convert tables (compact version)
        lines = html_content.split('<br>')
        processed_lines = []
        in_table = False
        
        for line in lines:
            if '|' in line and '---' not in line and line.strip():
                if not in_table:
                    processed_lines.append('<table style="border-collapse: collapse; margin: 8px 0; font-size: 11px; width: 100%;">')
                    in_table = True
                
                cells = [cell.strip() for cell in line.split('|') if cell.strip()]
                row_html = '<tr>'
                for j, cell in enumerate(cells):
                    style = 'border: 1px solid #ddd; padding: 4px 6px; font-size: 11px;'
                    if j == 0:  # First column
                        style += ' background-color: #f8f9fa; font-weight: bold;'
                    row_html += f'<td style="{style}">{cell}</td>'
                row_html += '</tr>'
                processed_lines.append(row_html)
            else:
                if in_table:
                    processed_lines.append('</table>')
                    in_table = False
                processed_lines.append(line)
        
        if in_table:
            processed_lines.append('</table>')
        
        return '<br>'.join(processed_lines)
    
    def send_notification_email(self, recipient_email: str, subject: str, 
                              message: str, user_id: Optional[str] = None) -> bool:
        """
        Send a simple notification email.
        
        Args:
            recipient_email: Email address to send to
            subject: Email subject
            message: Email message content
            user_id: Optional user ID for context
            
        Returns:
            True if email sent successfully, False otherwise
        """
        if not self.config:
            logger.error("Email configuration not available")
            return False
        
        try:
            if not self._connect_smtp():
                return False
            
            msg = MIMEMultipart()
            msg['From'] = f"{self.config['sender_name']} <{self.config['email']}>"
            msg['To'] = recipient_email
            msg['Subject'] = subject
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            body = f"""
{message}

---
Urban Planning Assistant
{f"User: {user_id}" if user_id else ""}
Sent: {timestamp}
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            self.smtp_server.send_message(msg)
            logger.info(f"Successfully sent notification email to {recipient_email}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send notification email: {e}")
            return False
        
        finally:
            self._disconnect_smtp()

# Global instance
email_manager = EmailManager()

def send_report_email(recipient_email: str, user_id: str, report_content: str,
                     attachments: Optional[List[Dict[str, Any]]] = None,
                     dropbox_links: Optional[List[str]] = None) -> bool:
    """
    Convenience function to send a report email.
    
    Args:
        recipient_email: Email address to send to
        user_id: ID of the user
        report_content: Text content of the report
        attachments: List of attachment dictionaries
        dropbox_links: List of Dropbox share URLs
        
    Returns:
        True if email sent successfully, False otherwise
    """
    return email_manager.send_report_email(
        recipient_email, user_id, report_content, attachments, dropbox_links
    )

def send_notification(recipient_email: str, subject: str, message: str,
                     user_id: Optional[str] = None) -> bool:
    """
    Convenience function to send a notification email.
    
    Args:
        recipient_email: Email address to send to
        subject: Email subject
        message: Email message content
        user_id: Optional user ID for context
        
    Returns:
        True if email sent successfully, False otherwise
    """
    return email_manager.send_notification_email(recipient_email, subject, message, user_id)
