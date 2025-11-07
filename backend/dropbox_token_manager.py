#!/usr/bin/env python3
"""
Dropbox Token Manager - Complete OAuth Flow
Handles Dropbox token generation, refresh, and management
"""

import os
import requests
import json
import webbrowser
from urllib.parse import urlencode, parse_qs, urlparse
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/Users/ronick/Documents/curriculum/urban_planning_assistant/.env')

class DropboxTokenManager:
    def __init__(self):
        self.client_id = os.getenv('DROPBOX_CLIENT_ID', 'y8ng4pgs7j1niv2')
        self.client_secret = os.getenv('DROPBOX_CLIENT_SECRET', 'hzpppjnvrv32csf')
        self.redirect_uri = 'http://localhost:3000/callback/dropbox'
        self.authorization_code = None
        self.server = None
        
    def generate_auth_url(self):
        """Generate the authorization URL for Dropbox OAuth"""
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': self.redirect_uri,
            'token_access_type': 'offline'  # This enables refresh tokens
        }
        
        auth_url = f"https://www.dropbox.com/oauth2/authorize?{urlencode(params)}"
        return auth_url
    
    def exchange_code_for_tokens(self, authorization_code):
        """Exchange authorization code for access and refresh tokens"""
        token_url = 'https://api.dropboxapi.com/oauth2/token'
        
        data = {
            'code': authorization_code,
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri
        }
        
        try:
            response = requests.post(token_url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            return {
                'access_token': token_data.get('access_token'),
                'refresh_token': token_data.get('refresh_token'),
                'expires_in': token_data.get('expires_in'),
                'token_type': token_data.get('token_type', 'Bearer'),
                'scope': token_data.get('scope')
            }
        except requests.exceptions.RequestException as e:
            print(f"❌ Error exchanging code for tokens: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"Response: {e.response.text}")
            return None
    
    def refresh_access_token(self, refresh_token):
        """Refresh the access token using refresh token"""
        token_url = 'https://api.dropboxapi.com/oauth2/token'
        
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        
        try:
            response = requests.post(token_url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            return {
                'access_token': token_data.get('access_token'),
                'expires_in': token_data.get('expires_in'),
                'token_type': token_data.get('token_type', 'Bearer')
            }
        except requests.exceptions.RequestException as e:
            print(f"❌ Error refreshing token: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"Response: {e.response.text}")
            return None
    
    def update_env_file(self, access_token, refresh_token=None):
        """Update the .env file with new tokens"""
        env_path = '/Users/ronick/Documents/curriculum/urban_planning_assistant/.env'
        
        try:
            # Read the current .env file
            with open(env_path, 'r') as f:
                lines = f.readlines()
            
            # Update the tokens
            updated_lines = []
            access_token_updated = False
            refresh_token_updated = False
            
            for line in lines:
                if line.startswith('DROPBOX_ACCESS_TOKEN='):
                    updated_lines.append(f'DROPBOX_ACCESS_TOKEN={access_token}\n')
                    access_token_updated = True
                elif line.startswith('DROPBOX_REFRESH_TOKEN=') and refresh_token:
                    updated_lines.append(f'DROPBOX_REFRESH_TOKEN={refresh_token}\n')
                    refresh_token_updated = True
                else:
                    updated_lines.append(line)
            
            # Add tokens if they weren't found in the file
            if not access_token_updated:
                updated_lines.append(f'DROPBOX_ACCESS_TOKEN={access_token}\n')
            
            if refresh_token and not refresh_token_updated:
                updated_lines.append(f'DROPBOX_REFRESH_TOKEN={refresh_token}\n')
            
            # Write back to the file
            with open(env_path, 'w') as f:
                f.writelines(updated_lines)
            
            print(f"✅ Updated .env file with new tokens")
            return True
            
        except Exception as e:
            print(f"❌ Error updating .env file: {e}")
            return False

class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle the OAuth callback"""
        if self.path.startswith('/callback/dropbox'):
            # Parse the authorization code from the URL
            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)
            
            if 'code' in query_params:
                self.server.authorization_code = query_params['code'][0]
                
                # Send success response
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                success_html = """
                <html>
                <head><title>Dropbox Authorization Success</title></head>
                <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                    <h1 style="color: green;">✅ Authorization Successful!</h1>
                    <p>You can now close this tab and return to the terminal.</p>
                    <p>The Dropbox tokens are being processed...</p>
                </body>
                </html>
                """
                self.wfile.write(success_html.encode())
            else:
                # Handle error
                error = query_params.get('error', ['Unknown error'])[0]
                self.server.authorization_code = None
                
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                error_html = f"""
                <html>
                <head><title>Dropbox Authorization Error</title></head>
                <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                    <h1 style="color: red;">❌ Authorization Failed</h1>
                    <p>Error: {error}</p>
                    <p>Please try again.</p>
                </body>
                </html>
                """
                self.wfile.write(error_html.encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass

def start_callback_server():
    """Start the callback server to handle OAuth response"""
    server = HTTPServer(('localhost', 3000), CallbackHandler)
    server.authorization_code = None
    
    print("🌐 Starting callback server on http://localhost:3000")
    
    # Start server in a separate thread
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    return server

def main():
    print("🔑 Dropbox Token Manager")
    print("=" * 50)
    print()
    
    token_manager = DropboxTokenManager()
    
    print("Choose an option:")
    print("1. Get new tokens (full OAuth flow)")
    print("2. Refresh existing token")
    print("3. Test current token")
    print()
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == '1':
        # Full OAuth flow
        print("\n🚀 Starting OAuth flow...")
        print("This will:")
        print("1. Start a local callback server")
        print("2. Open Dropbox authorization in your browser")
        print("3. Wait for you to authorize the app")
        print("4. Exchange the code for tokens")
        print("5. Update your .env file")
        print()
        
        input("Press Enter to continue...")
        
        # Start callback server
        server = start_callback_server()
        
        # Generate and open authorization URL
        auth_url = token_manager.generate_auth_url()
        print(f"\n📱 Opening authorization URL: {auth_url}")
        
        try:
            webbrowser.open(auth_url)
            print("✅ Opened in browser")
        except:
            print("❌ Could not open browser. Please visit the URL manually:")
            print(auth_url)
        
        # Wait for callback
        print("\n⏳ Waiting for authorization...")
        print("Please complete the authorization in your browser...")
        
        timeout = 300  # 5 minutes
        start_time = time.time()
        
        while server.authorization_code is None and (time.time() - start_time) < timeout:
            time.sleep(1)
        
        if server.authorization_code:
            print("✅ Authorization code received!")
            
            # Exchange code for tokens
            print("🔄 Exchanging code for tokens...")
            tokens = token_manager.exchange_code_for_tokens(server.authorization_code)
            
            if tokens:
                print("✅ Tokens obtained successfully!")
                print(f"Access Token: ***{tokens['access_token'][-10:]}")
                if tokens.get('refresh_token'):
                    print(f"Refresh Token: ***{tokens['refresh_token'][-10:]}")
                
                # Update .env file
                token_manager.update_env_file(
                    tokens['access_token'], 
                    tokens.get('refresh_token')
                )
                
                print("\n🎉 Success! Your Dropbox integration is now ready.")
            else:
                print("❌ Failed to obtain tokens")
        else:
            print("⏰ Timeout waiting for authorization")
        
        server.shutdown()
    
    elif choice == '2':
        # Refresh token
        refresh_token = os.getenv('DROPBOX_REFRESH_TOKEN')
        if not refresh_token:
            print("❌ No refresh token found in .env file")
            print("Please run option 1 to get initial tokens")
            return
        
        print("🔄 Refreshing access token...")
        new_tokens = token_manager.refresh_access_token(refresh_token)
        
        if new_tokens:
            print("✅ Token refreshed successfully!")
            print(f"New Access Token: ***{new_tokens['access_token'][-10:]}")
            
            # Update .env file
            token_manager.update_env_file(new_tokens['access_token'])
            
            print("🎉 Access token updated in .env file")
        else:
            print("❌ Failed to refresh token")
    
    elif choice == '3':
        # Test current token
        access_token = os.getenv('DROPBOX_ACCESS_TOKEN')
        if not access_token:
            print("❌ No access token found in .env file")
            return
        
        print("🧪 Testing current access token...")
        
        # Test with a simple API call
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(
                'https://api.dropboxapi.com/2/users/get_current_account',
                headers=headers
            )
            
            if response.status_code == 200:
                user_info = response.json()
                print("✅ Token is valid!")
                print(f"Account: {user_info.get('name', {}).get('display_name', 'Unknown')}")
                print(f"Email: {user_info.get('email', 'Unknown')}")
            else:
                print(f"❌ Token test failed: {response.status_code}")
                print("Token may be expired or invalid")
                
        except Exception as e:
            print(f"❌ Error testing token: {e}")
    
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()
