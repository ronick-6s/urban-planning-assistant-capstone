"""
Enhanced Dropbox Integration with Token Refresh
Handles token expiration and automatic refresh
"""

import dropbox
import os
import logging
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class DropboxClientManager:
    """
    Manages Dropbox client with automatic token refresh
    """
    
    def __init__(self):
        self.app_key = os.getenv("DROPBOX_CLIENT_ID")
        self.app_secret = os.getenv("DROPBOX_CLIENT_SECRET") 
        self.access_token = os.getenv("DROPBOX_ACCESS_TOKEN")
        self.refresh_token = os.getenv("DROPBOX_REFRESH_TOKEN")
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self) -> bool:
        """Initialize Dropbox client with token refresh capability"""
        try:
            if not all([self.app_key, self.app_secret, self.access_token]):
                logger.error("Missing required Dropbox configuration")
                return False
            
            # Create client with refresh capability
            self.client = dropbox.Dropbox(
                oauth2_access_token=self.access_token,
                oauth2_refresh_token=self.refresh_token,
                app_key=self.app_key,
                app_secret=self.app_secret
            )
            
            # Test the connection
            try:
                account_info = self.client.users_get_current_account()
                logger.info(f"Dropbox connected successfully for: {account_info.email}")
                return True
            except dropbox.exceptions.AuthError as auth_error:
                logger.warning(f"Auth error, attempting token refresh: {auth_error}")
                return self._refresh_access_token()
                
        except Exception as e:
            logger.error(f"Error initializing Dropbox client: {e}")
            return False
    
    def _refresh_access_token(self) -> bool:
        """Refresh the access token using refresh token"""
        try:
            if not self.refresh_token:
                logger.error("No refresh token available")
                return False
            
            # Use the Dropbox client to refresh token
            logger.info("Attempting to refresh access token...")
            
            # Create a new client for token refresh
            refresh_client = dropbox.Dropbox(
                app_key=self.app_key,
                app_secret=self.app_secret
            )
            
            # Refresh the token
            token_result = refresh_client.refresh_access_token(self.refresh_token)
            
            if token_result and hasattr(token_result, 'access_token'):
                new_access_token = token_result.access_token
                
                # Update the environment variable and client
                os.environ['DROPBOX_ACCESS_TOKEN'] = new_access_token
                self.access_token = new_access_token
                
                # Create new client with refreshed token
                self.client = dropbox.Dropbox(
                    oauth2_access_token=new_access_token,
                    oauth2_refresh_token=self.refresh_token,
                    app_key=self.app_key,
                    app_secret=self.app_secret
                )
                
                # Test the new client
                account_info = self.client.users_get_current_account()
                logger.info(f"Token refreshed successfully for: {account_info.email}")
                
                # Update .env file with new token
                self._update_env_file(new_access_token)
                return True
            else:
                logger.error("Token refresh failed - no access token returned")
                return False
                
        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            return False
    
    def _update_env_file(self, new_token: str):
        """Update the .env file with new access token"""
        try:
            env_path = os.path.join(os.path.dirname(__file__), '.env')
            if os.path.exists(env_path):
                with open(env_path, 'r') as f:
                    content = f.read()
                
                # Replace the old token with new one
                if 'DROPBOX_ACCESS_TOKEN=' in content:
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if line.startswith('DROPBOX_ACCESS_TOKEN='):
                            lines[i] = f'DROPBOX_ACCESS_TOKEN={new_token}'
                            break
                    
                    with open(env_path, 'w') as f:
                        f.write('\n'.join(lines))
                    
                    logger.info("Updated .env file with new access token")
        except Exception as e:
            logger.warning(f"Could not update .env file: {e}")
    
    def get_client(self) -> Optional[dropbox.Dropbox]:
        """Get the Dropbox client, refreshing token if needed"""
        if not self.client:
            if not self._initialize_client():
                return None
        
        try:
            # Test the client
            self.client.users_get_current_account()
            return self.client
        except dropbox.exceptions.AuthError:
            # Try to refresh token
            if self._refresh_access_token():
                return self.client
            return None
        except Exception as e:
            logger.error(f"Error testing Dropbox client: {e}")
            return None
    
    def test_connection(self) -> bool:
        """Test the Dropbox connection"""
        client = self.get_client()
        if client:
            try:
                account_info = client.users_get_current_account()
                logger.info(f"Dropbox connection test successful: {account_info.email}")
                return True
            except Exception as e:
                logger.error(f"Dropbox connection test failed: {e}")
                return False
        return False

# Global instance
_dropbox_manager = None

def get_dropbox_client() -> Optional[dropbox.Dropbox]:
    """Get a working Dropbox client with automatic token refresh"""
    global _dropbox_manager
    
    if _dropbox_manager is None:
        _dropbox_manager = DropboxClientManager()
    
    return _dropbox_manager.get_client()

def test_dropbox_connection() -> bool:
    """Test Dropbox connection"""
    global _dropbox_manager
    
    if _dropbox_manager is None:
        _dropbox_manager = DropboxClientManager()
    
    return _dropbox_manager.test_connection()

if __name__ == "__main__":
    # Test the Dropbox connection
    print("🔧 Testing Dropbox Connection...")
    
    if test_dropbox_connection():
        print("✅ Dropbox connection successful!")
        
        client = get_dropbox_client()
        if client:
            try:
                account = client.users_get_current_account()
                print(f"📧 Connected as: {account.email}")
                print(f"👤 Display name: {account.name.display_name}")
                
                # Test file operations
                print("\n📁 Testing file operations...")
                
                # List root folder
                result = client.files_list_folder("")
                print(f"📂 Root folder contains {len(result.entries)} items")
                
                print("✅ All tests passed!")
            except Exception as e:
                print(f"❌ File operations test failed: {e}")
    else:
        print("❌ Dropbox connection failed!")
        print("Please check your Dropbox credentials in the .env file")
