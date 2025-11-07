"""
Cloud Integration Configuration for Urban Planning Assistant
Handles Dropbox API and iCloud Mail SMTP settings
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Dropbox Configuration
DROPBOX_CONFIG = {
    "app_key": os.getenv("DROPBOX_CLIENT_ID", "your_dropbox_app_key_here"),
    "app_secret": os.getenv("DROPBOX_CLIENT_SECRET", "your_dropbox_app_secret_here"),
    "access_token": os.getenv("DROPBOX_ACCESS_TOKEN", "your_dropbox_access_token_here"),
    "refresh_token": os.getenv("DROPBOX_REFRESH_TOKEN", "your_dropbox_refresh_token_here"),
    "reports_folder": "/urban_planning_reports",
    "user_folders_base": "/UrbanPlanningReports/users",  # Base path for user folders
    "admin_email": os.getenv("ADMIN_EMAIL", "admin@urbanplanning.studio"),
    "file_retention_days": 30
}

# iCloud Mail SMTP Configuration
ICLOUD_SMTP_CONFIG = {
    "smtp_server": "smtp.mail.me.com",
    "smtp_port": 587,
    "email": os.getenv("ICLOUD_EMAIL", "your_icloud_email@icloud.com"),
    "password": os.getenv("ICLOUD_APP_PASSWORD", "your_app_specific_password"),
    "sender_name": "Urban Planning Assistant",
    "use_tls": True
}

# Email Templates
EMAIL_TEMPLATES = {
    "subject": "Urban Planning Assistant - Chat History Report",
    "greeting": "Hello,",
    "body_intro": "Please find your Urban Planning Assistant chat history report attached.",
    "body_footer": """
Best regards,
Urban Planning Assistant System

This report contains your conversation history with the Chennai Urban Planning Assistant.
If you have any questions, please contact your system administrator.
    """,
    "signature": """
---
Urban Planning Assistant
Chennai Smart City Initiative
Generated on: {timestamp}
    """
}

# Report Configuration
REPORT_CONFIG = {
    "formats": ["pdf", "html", "txt"],
    "default_format": "pdf",
    "include_metadata": True,
    "include_timestamp": True,
    "max_history_days": 30
}

def get_dropbox_config() -> Dict[str, Any]:
    """Get Dropbox configuration with validation."""
    config = DROPBOX_CONFIG.copy()
    
    # Validate required fields
    required_fields = ["app_key", "app_secret", "access_token"]
    missing_fields = [field for field in required_fields 
                     if not config.get(field) or config[field].startswith("your_")]
    
    if missing_fields:
        raise ValueError(f"Missing Dropbox configuration: {', '.join(missing_fields)}")
    
    return config

def get_icloud_config() -> Dict[str, Any]:
    """Get iCloud SMTP configuration with validation."""
    config = ICLOUD_SMTP_CONFIG.copy()
    
    # Validate required fields
    required_fields = ["email", "password"]
    missing_fields = [field for field in required_fields 
                     if not config.get(field) or config[field].startswith("your_")]
    
    if missing_fields:
        raise ValueError(f"Missing iCloud configuration: {', '.join(missing_fields)}")
    
    return config

def get_email_template(template_type: str = "default") -> Dict[str, str]:
    """Get email template configuration."""
    return EMAIL_TEMPLATES.copy()

def get_report_config() -> Dict[str, Any]:
    """Get report generation configuration."""
    return REPORT_CONFIG.copy()

def get_dropbox_client():
    """Create and return a Dropbox client instance."""
    try:
        import dropbox
        config = get_dropbox_config()
        
        # Create Dropbox client with access token
        dbx = dropbox.Dropbox(
            oauth2_access_token=config["access_token"],
            app_key=config["app_key"],
            app_secret=config["app_secret"]
        )
        
        # Test the connection
        dbx.users_get_current_account()
        return dbx
        
    except Exception as e:
        print(f"Failed to create Dropbox client: {e}")
        return None

def get_user_folder_config() -> Dict[str, str]:
    """Get user folder management configuration."""
    return {
        "base_folder": DROPBOX_CONFIG["user_folders_base"],
        "admin_email": DROPBOX_CONFIG["admin_email"],
        "registry_file": f"{DROPBOX_CONFIG['user_folders_base']}/users_registry.json"
    }
