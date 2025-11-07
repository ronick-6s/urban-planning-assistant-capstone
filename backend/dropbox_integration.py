"""
Dropbox Integration for Urban Planning Assistant
Handles file upload, storage, and management in Dropbox
"""

import os
import json
import dropbox
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from cloud_config import get_dropbox_config, get_report_config
import logging

logger = logging.getLogger(__name__)

class DropboxManager:
    """Manages Dropbox operations for report storage."""
    
    def __init__(self):
        """Initialize Dropbox client with configuration."""
        try:
            self.config = get_dropbox_config()
            self.dbx = dropbox.Dropbox(
                app_key=self.config["app_key"],
                app_secret=self.config["app_secret"],
                oauth2_access_token=self.config["access_token"]
            )
            self.reports_folder = self.config["reports_folder"]
            self._ensure_folder_exists()
        except ValueError as e:
            logger.warning(f"Dropbox configuration incomplete: {e}")
            self.dbx = None
    
    def _refresh_access_token(self):
        """Attempt to refresh the access token if refresh token is available"""
        refresh_token = os.getenv('DROPBOX_REFRESH_TOKEN')
        if not refresh_token:
            logger.warning("No refresh token available for Dropbox")
            return False
        
        try:
            token_url = 'https://api.dropboxapi.com/oauth2/token'
            data = {
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token,
                'client_id': self.config["app_key"],
                'client_secret': self.config["app_secret"]
            }
            
            response = requests.post(token_url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            new_access_token = token_data.get('access_token')
            
            if new_access_token:
                # Update the Dropbox client with new token
                self.dbx = dropbox.Dropbox(
                    app_key=self.config["app_key"],
                    app_secret=self.config["app_secret"],
                    oauth2_access_token=new_access_token
                )
                
                # Update environment variable (note: this only affects current session)
                os.environ['DROPBOX_ACCESS_TOKEN'] = new_access_token
                
                logger.info("Successfully refreshed Dropbox access token")
                return True
                
        except Exception as e:
            logger.error(f"Failed to refresh Dropbox access token: {e}")
        
        return False
    
    def _ensure_folder_exists(self):
        """Ensure the reports folder exists in Dropbox."""
        if not self.dbx:
            return
        
        try:
            self.dbx.files_get_metadata(self.reports_folder)
            logger.info(f"Reports folder exists: {self.reports_folder}")
        except dropbox.exceptions.ApiError as e:
            # Check if it's a path not found error
            if hasattr(e.error, 'get_path_lookup') and e.error.get_path_lookup().is_not_found():
                folder_not_found = True
            elif str(e).find('not_found') != -1 or str(e).find('path_lookup') != -1:
                folder_not_found = True
            else:
                folder_not_found = False
                
            if folder_not_found:
                # Folder doesn't exist, create it
                try:
                    self.dbx.files_create_folder_v2(self.reports_folder)
                    logger.info(f"Created Dropbox folder: {self.reports_folder}")
                except Exception as create_error:
                    logger.error(f"Failed to create Dropbox folder: {create_error}")
            else:
                logger.error(f"Error accessing Dropbox folder: {e}")
        except Exception as e:
            logger.error(f"Unexpected error checking folder: {e}")
    
    def upload_report(self, file_content: bytes, filename: str, 
                     user_id: str, content_type: str = "application/pdf") -> Optional[Dict[str, str]]:
        """
        Upload a report file to Dropbox.
        
        Args:
            file_content: The file content as bytes
            filename: Name of the file
            user_id: ID of the user who generated the report
            content_type: MIME type of the file
            
        Returns:
            Dictionary with upload info or None if failed
        """
        if not self.dbx:
            logger.error("Dropbox client not initialized - check configuration")
            return {"error": "Dropbox not configured", "share_url": None}
        
        try:
            # Create timestamp for unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_filename = f"{user_id}_{timestamp}_{filename}"
            dropbox_path = f"{self.reports_folder}/{unique_filename}"
            
            # Upload file
            result = self.dbx.files_upload(
                file_content,
                dropbox_path,
                mode=dropbox.files.WriteMode.overwrite,
                autorename=True
            )
            
            # Create shareable link
            try:
                link_result = self.dbx.sharing_create_shared_link_with_settings(
                    dropbox_path,
                    settings=dropbox.sharing.SharedLinkSettings(
                        requested_visibility=dropbox.sharing.RequestedVisibility.public
                    )
                )
                share_url = link_result.url
            except Exception as link_error:
                logger.warning(f"Failed to create share link: {link_error}")
                share_url = None
            
            upload_info = {
                "filename": unique_filename,
                "path": dropbox_path,
                "size": len(file_content),
                "uploaded_at": datetime.now().isoformat(),
                "user_id": user_id,
                "share_url": share_url,
                "content_type": content_type
            }
            
            logger.info(f"Successfully uploaded report to Dropbox: {unique_filename}")
            return upload_info
            
        except dropbox.exceptions.AuthError as auth_error:
            logger.warning(f"Dropbox authentication failed, attempting token refresh: {auth_error}")
            
            # Try to refresh the token and retry the upload
            if self._refresh_access_token():
                try:
                    # Retry the upload with refreshed token
                    result = self.dbx.files_upload(
                        file_content,
                        dropbox_path,
                        mode=dropbox.files.WriteMode.overwrite,
                        autorename=True
                    )
                    
                    # Create shareable link
                    try:
                        link_result = self.dbx.sharing_create_shared_link_with_settings(
                            dropbox_path,
                            settings=dropbox.sharing.SharedLinkSettings(
                                requested_visibility=dropbox.sharing.RequestedVisibility.public
                            )
                        )
                        share_url = link_result.url
                    except Exception as link_error:
                        logger.warning(f"Failed to create share link after retry: {link_error}")
                        share_url = None
                    
                    upload_info = {
                        "filename": unique_filename,
                        "path": dropbox_path,
                        "size": len(file_content),
                        "uploaded_at": datetime.now().isoformat(),
                        "user_id": user_id,
                        "share_url": share_url,
                        "content_type": content_type
                    }
                    
                    logger.info(f"Successfully uploaded report to Dropbox after token refresh: {unique_filename}")
                    return upload_info
                    
                except Exception as retry_error:
                    logger.error(f"Upload failed even after token refresh: {retry_error}")
                    return {"error": f"Upload failed after token refresh: {str(retry_error)}", "share_url": None}
            else:
                return {"error": "Dropbox authentication failed - unable to refresh token", "share_url": None}
        except Exception as e:
            logger.error(f"Failed to upload to Dropbox: {e}")
            return {"error": f"Upload failed: {str(e)}", "share_url": None}
    
    def list_user_reports(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        List reports for a specific user.
        
        Args:
            user_id: ID of the user
            limit: Maximum number of reports to return
            
        Returns:
            List of report metadata dictionaries
        """
        if not self.dbx:
            return []
        
        try:
            # List files in the reports folder
            result = self.dbx.files_list_folder(self.reports_folder)
            user_files = []
            
            for entry in result.entries:
                if isinstance(entry, dropbox.files.FileMetadata):
                    # Check if file belongs to user
                    if entry.name.startswith(f"{user_id}_"):
                        file_info = {
                            "name": entry.name,
                            "path": entry.path_display,
                            "size": entry.size,
                            "modified": entry.server_modified.isoformat() if entry.server_modified else None,
                            "id": entry.id
                        }
                        user_files.append(file_info)
            
            # Sort by modification date (newest first)
            user_files.sort(key=lambda x: x.get("modified", ""), reverse=True)
            return user_files[:limit]
            
        except Exception as e:
            logger.error(f"Failed to list user reports: {e}")
            return []
    
    def delete_old_reports(self, days_old: int = 30) -> int:
        """
        Delete reports older than specified days.
        
        Args:
            days_old: Number of days after which to delete reports
            
        Returns:
            Number of reports deleted
        """
        if not self.dbx:
            return 0
        
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)
            result = self.dbx.files_list_folder(self.reports_folder)
            deleted_count = 0
            
            for entry in result.entries:
                if isinstance(entry, dropbox.files.FileMetadata):
                    if entry.server_modified and entry.server_modified < cutoff_date:
                        try:
                            self.dbx.files_delete_v2(entry.path_display)
                            deleted_count += 1
                            logger.info(f"Deleted old report: {entry.name}")
                        except Exception as delete_error:
                            logger.error(f"Failed to delete {entry.name}: {delete_error}")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to delete old reports: {e}")
            return 0
    
    def get_storage_info(self) -> Optional[Dict[str, Any]]:
        """
        Get Dropbox storage usage information.
        
        Returns:
            Dictionary with storage info or None if failed
        """
        if not self.dbx:
            return None
        
        try:
            space_usage = self.dbx.users_get_space_usage()
            
            return {
                "used": space_usage.used,
                "allocated": space_usage.allocation.get_individual().allocated if hasattr(space_usage.allocation, 'get_individual') else None,
                "usage_percentage": (space_usage.used / space_usage.allocation.get_individual().allocated * 100) if hasattr(space_usage.allocation, 'get_individual') else None
            }
            
        except Exception as e:
            logger.error(f"Failed to get storage info: {e}")
            return None

# Global instance
dropbox_manager = DropboxManager()

def upload_report_to_dropbox(file_content: bytes, filename: str, 
                           user_id: str, content_type: str = "application/pdf") -> Optional[Dict[str, str]]:
    """
    Convenience function to upload a report to Dropbox.
    
    Args:
        file_content: The file content as bytes
        filename: Name of the file
        user_id: ID of the user who generated the report
        content_type: MIME type of the file
        
    Returns:
        Dictionary with upload info or None if failed
    """
    return dropbox_manager.upload_report(file_content, filename, user_id, content_type)

def get_user_reports(user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    """
    Get list of reports for a user.
    
    Args:
        user_id: ID of the user
        limit: Maximum number of reports to return
        
    Returns:
        List of report metadata dictionaries
    """
    return dropbox_manager.list_user_reports(user_id, limit)

def cleanup_old_reports(days_old: int = 30) -> int:
    """
    Clean up old reports from Dropbox.
    
    Args:
        days_old: Number of days after which to delete reports
        
    Returns:
        Number of reports deleted
    """
    return dropbox_manager.delete_old_reports(days_old)
