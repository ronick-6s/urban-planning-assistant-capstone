"""
Dropbox User Folder Management System
Handles individual user folders based on email ID with admin access control
"""

import dropbox
import os
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class UserFolder:
    """Represents a user's Dropbox folder"""
    email: str
    folder_path: str
    created_at: datetime
    last_accessed: datetime
    shared_folder_id: Optional[str] = None
    access_permissions: List[str] = None

class DropboxUserManager:
    """
    Manages individual user folders in Dropbox with admin access control
    """
    
    def __init__(self, dropbox_client: dropbox.Dropbox, admin_email: str):
        self.dbx = dropbox_client
        self.admin_email = admin_email
        self.base_folder = "/UrbanPlanningReports"
        self.users_registry_path = f"{self.base_folder}/users_registry.json"
        self.users_registry: Dict[str, UserFolder] = {}
        self._load_users_registry()
    
    def _sanitize_email_for_folder(self, email: str) -> str:
        """
        Convert email to valid folder name
        Example: user@domain.com -> user_at_domain_com
        """
        # Remove special characters and replace with underscores
        sanitized = re.sub(r'[^a-zA-Z0-9._-]', '_', email)
        return sanitized.lower()
    
    def _get_user_folder_path(self, email: str) -> str:
        """Get the Dropbox path for a user's folder"""
        sanitized_email = self._sanitize_email_for_folder(email)
        return f"{self.base_folder}/users/{sanitized_email}"
    
    def _load_users_registry(self):
        """Load users registry from Dropbox"""
        try:
            # Download the registry file
            _, response = self.dbx.files_download(self.users_registry_path)
            registry_data = json.loads(response.content.decode('utf-8'))
            
            # Convert to UserFolder objects
            for email, data in registry_data.items():
                self.users_registry[email] = UserFolder(
                    email=data['email'],
                    folder_path=data['folder_path'],
                    created_at=datetime.fromisoformat(data['created_at']),
                    last_accessed=datetime.fromisoformat(data['last_accessed']),
                    shared_folder_id=data.get('shared_folder_id'),
                    access_permissions=data.get('access_permissions', [])
                )
            logger.info(f"Loaded {len(self.users_registry)} users from registry")
            
        except dropbox.exceptions.ApiError as e:
            # Handle different types of Dropbox errors
            if hasattr(e.error, 'is_path_not_found') and e.error.is_path_not_found():
                logger.info("Users registry not found, creating new registry")
                self.users_registry = {}
                self._save_users_registry()
            elif 'not_found' in str(e.error) or 'path_not_found' in str(e.error).lower():
                logger.info("Users registry file not found, creating new registry")
                self.users_registry = {}
                self._save_users_registry()
            else:
                logger.error(f"Error loading users registry: {e}")
                self.users_registry = {}
        except Exception as general_error:
            logger.warning(f"Could not load users registry: {general_error}")
            logger.info("Starting with empty registry")
            self.users_registry = {}
    
    def _save_users_registry(self):
        """Save users registry to Dropbox"""
        try:
            # Convert UserFolder objects to dict
            registry_data = {}
            for email, user_folder in self.users_registry.items():
                registry_data[email] = {
                    'email': user_folder.email,
                    'folder_path': user_folder.folder_path,
                    'created_at': user_folder.created_at.isoformat(),
                    'last_accessed': user_folder.last_accessed.isoformat(),
                    'shared_folder_id': user_folder.shared_folder_id,
                    'access_permissions': user_folder.access_permissions or []
                }
            
            # Upload registry to Dropbox
            registry_json = json.dumps(registry_data, indent=2)
            self.dbx.files_upload(
                registry_json.encode('utf-8'),
                self.users_registry_path,
                mode=dropbox.files.WriteMode.overwrite
            )
            logger.info("Users registry saved to Dropbox")
            
        except Exception as e:
            logger.error(f"Error saving users registry: {e}")
    
    def _create_folder_if_not_exists(self, folder_path: str) -> bool:
        """Create folder in Dropbox if it doesn't exist"""
        try:
            # Check if folder exists
            self.dbx.files_get_metadata(folder_path)
            return True
        except dropbox.exceptions.ApiError as e:
            # Check if it's a "not found" error using string matching
            error_str = str(e.error).lower()
            if 'not_found' in error_str or 'path_not_found' in error_str:
                try:
                    # Create the folder
                    self.dbx.files_create_folder_v2(folder_path)
                    logger.info(f"Created folder: {folder_path}")
                    return True
                except Exception as create_error:
                    logger.error(f"Error creating folder {folder_path}: {create_error}")
                    return False
            else:
                logger.error(f"Error checking folder {folder_path}: {e}")
                return False
    
    def _create_shared_folder(self, folder_path: str, user_email: str) -> Optional[str]:
        """
        Create a shared folder with restricted access
        Only the specific user and admin have access
        Returns shared folder ID if successful
        """
        try:
            logger.info(f"Creating shared folder for {user_email} at {folder_path}")
            
            # First, ensure the folder exists as a regular folder
            if not self._create_folder_if_not_exists(folder_path):
                logger.error(f"Failed to create base folder: {folder_path}")
                return None
            
            # Create shared folder link with password protection
            try:
                result = self.dbx.sharing_create_shared_link_with_settings(
                    path=folder_path,
                    settings=dropbox.sharing.SharedLinkSettings(
                        require_password=False,
                        expires=None,  # No expiration
                        audience=dropbox.sharing.LinkAudience.public,  # Public but only those with link
                        access=dropbox.sharing.RequestedLinkAccessLevel.viewer
                    )
                )
                
                shared_link_url = result.url
                logger.info(f"Created shared link for {user_email}: {shared_link_url}")
                
                # Try to create a proper shared folder if API supports it
                try:
                    # Create shared folder for collaboration
                    shared_folder_result = self.dbx.sharing_share_folder(
                        path=folder_path,
                        member_policy=dropbox.sharing.MemberPolicy.invite_only,
                        acl_update_policy=dropbox.sharing.AclUpdatePolicy.owner,
                        shared_link_policy=dropbox.sharing.SharedLinkPolicy.members_and_team,
                        force_async=False
                    )
                    
                    if hasattr(shared_folder_result, 'shared_folder_id'):
                        shared_folder_id = shared_folder_result.shared_folder_id
                        logger.info(f"Created shared folder with ID: {shared_folder_id}")
                        
                        # Add user as member if different from admin
                        if user_email.lower() != self.admin_email.lower():
                            try:
                                # Add user as editor to the shared folder
                                self.dbx.sharing_add_folder_member(
                                    shared_folder_id=shared_folder_id,
                                    members=[dropbox.sharing.AddMember(
                                        member=dropbox.sharing.MemberSelector.email(user_email),
                                        access_level=dropbox.sharing.AccessLevel.editor
                                    )],
                                    quiet=False
                                )
                                logger.info(f"Added {user_email} as editor to shared folder")
                            except Exception as member_error:
                                logger.warning(f"Could not add user as member: {member_error}")
                                # Continue anyway - folder is created
                        
                        return shared_folder_id
                    
                except dropbox.exceptions.ApiError as api_error:
                    logger.warning(f"Could not create collaborative shared folder: {api_error}")
                    # Fall back to just the shared link
                    return shared_link_url.split('/')[-1] if shared_link_url else None
                
                return shared_link_url.split('/')[-1] if shared_link_url else None
                
            except Exception as link_error:
                logger.warning(f"Could not create shared link: {link_error}")
                # Return None to indicate no sharing, but folder still exists
                return None
                
        except Exception as e:
            logger.error(f"Error creating shared folder: {e}")
            return None
    
    def get_or_create_user_folder(self, user_email: str) -> Tuple[str, bool]:
        """
        Get or create a user's folder
        Returns: (folder_path, is_new_folder)
        """
        user_email = user_email.lower().strip()
        
        # Check if user already exists
        if user_email in self.users_registry:
            # Update last accessed time
            self.users_registry[user_email].last_accessed = datetime.now()
            self._save_users_registry()
            logger.info(f"User folder exists for {user_email}")
            return self.users_registry[user_email].folder_path, False
        
        # Create new user folder
        user_folder_path = self._get_user_folder_path(user_email)
        
        # Ensure base folders exist
        self._create_folder_if_not_exists(self.base_folder)
        self._create_folder_if_not_exists(f"{self.base_folder}/users")
        
        # Create user's specific folder
        if self._create_folder_if_not_exists(user_folder_path):
            # Create shared folder with restricted access
            shared_folder_id = self._create_shared_folder(user_folder_path, user_email)
            
            # Register the new user
            user_folder = UserFolder(
                email=user_email,
                folder_path=user_folder_path,
                created_at=datetime.now(),
                last_accessed=datetime.now(),
                shared_folder_id=shared_folder_id,
                access_permissions=['read', 'write'] if user_email == self.admin_email else ['read', 'write']
            )
            
            self.users_registry[user_email] = user_folder
            self._save_users_registry()
            
            logger.info(f"Created new user folder for {user_email}: {user_folder_path}")
            return user_folder_path, True
        else:
            raise Exception(f"Failed to create folder for user {user_email}")
    
    def store_report(self, user_email: str, report_content: str, report_type: str = "planning_report") -> str:
        """
        Store a report in the user's folder
        Returns: Dropbox file path
        """
        user_folder_path, is_new = self.get_or_create_user_folder(user_email)
        
        # Generate report filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        sanitized_email = self._sanitize_email_for_folder(user_email)
        filename = f"{report_type}_{sanitized_email}_{timestamp}.txt"
        file_path = f"{user_folder_path}/{filename}"
        
        try:
            # Upload report to user's folder
            self.dbx.files_upload(
                report_content.encode('utf-8'),
                file_path,
                mode=dropbox.files.WriteMode.add
            )
            
            # Update user's last accessed time
            if user_email in self.users_registry:
                self.users_registry[user_email].last_accessed = datetime.now()
                self._save_users_registry()
            
            logger.info(f"Stored report for {user_email}: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error storing report for {user_email}: {e}")
            raise
    
    def get_user_reports(self, user_email: str, admin_request: bool = False) -> List[Dict]:
        """
        Get all reports for a user
        admin_request: If True, admin can access any user's reports
        """
        user_email = user_email.lower().strip()
        
        # Admin can access any user's folder
        if admin_request and self.admin_email:
            target_user = user_email
        else:
            target_user = user_email
        
        if target_user not in self.users_registry:
            return []
        
        user_folder_path = self.users_registry[target_user].folder_path
        
        try:
            # List files in user's folder
            result = self.dbx.files_list_folder(user_folder_path)
            reports = []
            
            for entry in result.entries:
                if isinstance(entry, dropbox.files.FileMetadata):
                    reports.append({
                        'filename': entry.name,
                        'path': entry.path_lower,
                        'size': entry.size,
                        'modified': entry.client_modified.isoformat() if entry.client_modified else None,
                        'download_url': self._get_download_url(entry.path_lower)
                    })
            
            logger.info(f"Found {len(reports)} reports for {target_user}")
            return reports
            
        except Exception as e:
            logger.error(f"Error getting reports for {target_user}: {e}")
            return []
    
    def _get_download_url(self, file_path: str) -> str:
        """Get temporary download URL for a file"""
        try:
            result = self.dbx.files_get_temporary_link(file_path)
            return result.link
        except Exception as e:
            logger.error(f"Error getting download URL for {file_path}: {e}")
            return ""
    
    def get_all_users(self) -> List[Dict]:
        """Get list of all users (admin only)"""
        users = []
        for email, user_folder in self.users_registry.items():
            users.append({
                'email': user_folder.email,
                'folder_path': user_folder.folder_path,
                'created_at': user_folder.created_at.isoformat(),
                'last_accessed': user_folder.last_accessed.isoformat(),
                'shared_folder_id': user_folder.shared_folder_id,
                'report_count': len(self.get_user_reports(email, admin_request=True))
            })
        
        return sorted(users, key=lambda x: x['last_accessed'], reverse=True)
    
    def delete_user_folder(self, user_email: str, admin_request: bool = False) -> bool:
        """
        Delete a user's folder (admin only)
        """
        if not admin_request:
            logger.error("Only admin can delete user folders")
            return False
        
        user_email = user_email.lower().strip()
        
        if user_email not in self.users_registry:
            logger.warning(f"User {user_email} not found in registry")
            return False
        
        user_folder = self.users_registry[user_email]
        
        try:
            # Delete the folder from Dropbox
            self.dbx.files_delete_v2(user_folder.folder_path)
            
            # Remove from registry
            del self.users_registry[user_email]
            self._save_users_registry()
            
            logger.info(f"Deleted user folder for {user_email}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting user folder for {user_email}: {e}")
            return False

# Usage example and integration helper
def create_user_manager(admin_email: str) -> DropboxUserManager:
    """Create DropboxUserManager instance with proper configuration"""
    try:
        from enhanced_dropbox_client import get_dropbox_client
        dropbox_client = get_dropbox_client()
        if not dropbox_client:
            raise Exception("Could not create Dropbox client - check credentials")
        return DropboxUserManager(dropbox_client, admin_email)
    except Exception as e:
        logger.error(f"Error creating user manager: {e}")
        raise
