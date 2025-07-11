import hashlib
import json
import platform
import subprocess
import sys
import time
import uuid
import requests
try:
    import mysql.connector
    from mysql.connector import Error
    MYSQL_AVAILABLE = True
except ImportError:
    print("MySQL connector not available. Database features will be disabled.")
    MYSQL_AVAILABLE = False
    
    # Create dummy Error class for compatibility
    class Error(Exception):
        pass
import websocket
import threading
from datetime import datetime
import os
import ctypes
from ctypes import wintypes
import psutil

class AuthenticationSystem:
    def __init__(self):
        self.db_config = {
            'host': '139.185.37.15',
            'port': 8212,
            'database': 'damain1611',
            'user': 'damain1611',
            'password': 'SdPFzq6UhZPua3k'
        }
        self.websocket_url = "ws://139.185.37.15:6551/ws"
        self.discord_webhook_url = "https://discord.com/api/webhooks/1296626853012045864/ZIfJZmPMckaTOwLg_TfAEO0TQyLaFXPrUwlwARvvtGQJe7YyAcUJFYUuiBYuLGqoV_s8"
        self.loader_version = "2.0"
        self.offsets_url = "http://139.185.37.15:6553/offsets.json"
        self.steam_api_url = "https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/?appid=730"
        self.connection = None
        self.ws_connection = None
        self.authenticated = False
        self.user_key = None
        self.hwid = None

    def get_hwid(self):
        """Generate Hardware ID based on BIOS UUID and MAC address"""
        try:
            # Get BIOS UUID
            if platform.system() == "Windows":
                result = subprocess.run(
                    ["wmic", "csproduct", "get", "UUID"],
                    capture_output=True,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                bios_uuid = result.stdout.strip()
            else:
                # Fallback for non-Windows systems
                bios_uuid = str(uuid.uuid4())

            # Get MAC address
            mac_addresses = []
            for interface, addrs in psutil.net_if_addrs().items():
                for addr in addrs:
                    if addr.family == psutil.AF_LINK:  # MAC address
                        mac_addresses.append(addr.address)
            
            mac_addr = mac_addresses[0] if mac_addresses else "00:00:00:00:00:00"
            
            # Create HWID hash
            hwid_source = bios_uuid + mac_addr
            hwid_hash = hashlib.sha256(hwid_source.encode()).hexdigest()
            
            return hwid_hash
            
        except Exception as e:
            print(f"Error generating HWID: {e}")
            return None

    def connect_to_database(self):
        """Establish database connection"""
        if not MYSQL_AVAILABLE:
            print("MySQL connector not available")
            return False
            
        try:
            self.connection = mysql.connector.connect(**self.db_config)
            if self.connection.is_connected():
                return True
        except Error as e:
            print(f"Database connection error: {e}")
            return False

    def get_public_ip(self):
        """Get user's public IP address"""
        try:
            response = requests.get("https://api.ipify.org", timeout=10)
            return response.text.strip()
        except:
            return "Unknown"

    def fetch_game_version_gid(self):
        """Fetch latest game version GID from Steam API"""
        try:
            response = requests.get(self.steam_api_url, timeout=10)
            data = response.json()
            
            if 'appnews' in data and 'newsitems' in data['appnews']:
                if len(data['appnews']['newsitems']) > 0:
                    return data['appnews']['newsitems'][0]['gid']
            
            return None
        except Exception as e:
            print(f"Error fetching game version: {e}")
            return None

    def check_versions(self):
        """Check loader and game versions against database"""
        if not MYSQL_AVAILABLE or not self.connection:
            print("Database connection not available")
            return False
            
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT LoaderVersion, GameVersion FROM version_control WHERE id = 1")
            result = cursor.fetchone()
            
            if not result:
                print("Version control data not found in database")
                return False
            
            db_loader_version, db_game_version = result
            
            # Check loader version
            if self.loader_version != db_loader_version:
                print(f"Loader update required. Current: {self.loader_version}, Required: {db_loader_version}")
                return False
            
            # Check game version
            steam_gid = self.fetch_game_version_gid()
            if steam_gid and steam_gid != db_game_version:
                print(f"Game update detected. Please wait for client updates.")
                return False
            
            return True
            
        except Error as e:
            print(f"Version check error: {e}")
            return False

    def validate_key_and_hwid(self, key, hwid):
        """Validate authentication key and HWID"""
        result = self.validate_key_and_hwid_detailed(key, hwid)
        return result['success']
    
    def validate_key_and_hwid_detailed(self, key, hwid):
        """Validate authentication key and HWID with detailed response"""
        if not MYSQL_AVAILABLE or not self.connection:
            print("Database connection not available")
            return {'success': False, 'error': 'Database connection not available'}
            
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT hwid, is_valid, expiration_date FROM `keys` WHERE key_value = %s",
                (key,)
            )
            result = cursor.fetchone()
            
            if not result:
                print("Invalid key. Please check your key or contact support.")
                return {'success': False, 'error': 'Invalid key. Please check your key or contact support.'}
            
            db_hwid, is_valid, expiration_date = result
            
            # Check if key has expired
            if expiration_date and datetime.now() > expiration_date:
                print("The key has expired.")
                return {'success': False, 'error': 'The key has expired.', 'expiration_date': expiration_date}
            
            # Check if key is valid
            if not is_valid:
                print("Key is not valid or has been deactivated.")
                return {'success': False, 'error': 'Key is not valid or has been deactivated.'}
            
            # Handle HWID cases
            if not db_hwid:  # No HWID assigned
                print("No HWID assigned. Please contact support for HWID binding.")
                return {'success': False, 'error': 'No HWID assigned. Please contact support for HWID binding.'}
            
            if db_hwid != hwid:  # HWID mismatch
                print("HWID mismatch. You are trying to log in from a different machine.")
                return {'success': False, 'error': 'HWID mismatch. You are trying to log in from a different machine.'}
            
            return {'success': True, 'expiration_date': expiration_date}
            
        except Error as e:
            print(f"Key validation error: {e}")
            return {'success': False, 'error': f'Key validation error: {e}'}

    def send_discord_webhook(self, key, ip):
        """Send login notification to Discord webhook"""
        try:
            message = f"Fury User logged in using key: `{key}`, IP: `{ip}`"
            payload = {"content": message}
            
            response = requests.post(
                self.discord_webhook_url,
                json=payload,
                timeout=10
            )
            
            return response.status_code in [200, 204]
            
        except Exception as e:
            print(f"Discord webhook error: {e}")
            return False

    def on_websocket_message(self, ws, message):
        """Handle WebSocket messages"""
        pass

    def on_websocket_error(self, ws, error):
        """Handle WebSocket errors"""
        print(f"WebSocket error: {error}")

    def on_websocket_close(self, ws, close_status_code, close_msg):
        """Handle WebSocket close"""
        print("WebSocket connection closed")
        # Attempt to reconnect after 5 seconds
        time.sleep(5)
        self.connect_websocket()

    def on_websocket_open(self, ws):
        """Handle WebSocket open"""
        print("WebSocket connected successfully")
        
        # Send periodic pings
        def send_ping():
            while self.ws_connection:
                try:
                    ws.send("ping")
                    time.sleep(60)  # Send ping every 60 seconds
                except:
                    break
        
        ping_thread = threading.Thread(target=send_ping, daemon=True)
        ping_thread.start()

    def connect_websocket(self):
        """Connect to WebSocket server"""
        if not self.user_key:
            return False
        
        try:
            ws_url = f"{self.websocket_url}?key={self.user_key}"
            self.ws_connection = websocket.WebSocketApp(
                ws_url,
                on_open=self.on_websocket_open,
                on_message=self.on_websocket_message,
                on_error=self.on_websocket_error,
                on_close=self.on_websocket_close
            )
            
            # Run WebSocket in a separate thread
            ws_thread = threading.Thread(
                target=self.ws_connection.run_forever,
                daemon=True
            )
            ws_thread.start()
            
            return True
            
        except Exception as e:
            print(f"WebSocket connection error: {e}")
            return False

    def display_ascii_art(self):
        """Display ASCII art banner"""
        ascii_art = """
 ███████╗██╗   ██╗██████╗ ██╗   ██╗
 ██╔════╝██║   ██║██╔══██╗╚██╗ ██╔╝
 █████╗  ██║   ██║██████╔╝ ╚████╔╝ 
 ██╔══╝  ██║   ██║██╔══██╗  ╚██╔╝  
 ██║     ╚██████╔╝██║  ██║   ██║   
 ╚═╝      ╚═════╝ ╚═╝  ╚═╝   ╚═╝   
                                   
        Enhanced Authentication System
        """
        print(ascii_art)

    def clear_screen(self):
        """Clear console screen"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def countdown(self, seconds, message="Starting in"):
        """Display countdown"""
        print(f"{message}:")
        for i in range(seconds, 0, -1):
            print(f"{i}...")
            time.sleep(1)
        self.clear_screen()

    def authenticate(self):
        """Main authentication process"""
        self.clear_screen()
        self.display_ascii_art()
        
        # Get HWID
        self.hwid = self.get_hwid()
        if not self.hwid:
            print("Failed to generate HWID")
            return False
        
        print(f"HWID: {self.hwid}")
        
        # Connect to database
        if not self.connect_to_database():
            print("Failed to connect to authentication server")
            return False
        
        # Check versions
        if not self.check_versions():
            return False
        
        # Get authentication key
        key = input("Enter your authentication key: ").strip()
        if not key:
            print("Invalid key format")
            return False
        
        # Validate key and HWID
        if not self.validate_key_and_hwid(key, self.hwid):
            return False
        
        # Store key for WebSocket connection
        self.user_key = key
        
        print("Authentication successful!")
        
        # Get public IP and send Discord notification
        public_ip = self.get_public_ip()
        self.send_discord_webhook(key, public_ip)
        
        # Connect to WebSocket
        self.connect_websocket()
        
        # Set authenticated flag
        self.authenticated = True
        
        # Countdown before starting
        self.countdown(5, "Initializing Fury")
        
        return True

    def is_authenticated(self):
        """Check if user is authenticated"""
        return self.authenticated

    def get_offsets(self):
        """Fetch game offsets"""
        try:
            response = requests.get(self.offsets_url, timeout=10)
            return response.json()
        except Exception as e:
            print(f"Error fetching offsets: {e}")
            return None

    def cleanup(self):
        """Cleanup resources"""
        if self.ws_connection:
            self.ws_connection.close()
        
        if self.connection and self.connection.is_connected():
            self.connection.close()

    def __del__(self):
        """Destructor"""
        self.cleanup()

# Global authentication instance
auth_system = AuthenticationSystem()

def authenticate_user():
    """Convenience function for authentication"""
    return auth_system.authenticate()

def is_user_authenticated():
    """Check if user is authenticated"""
    return auth_system.is_authenticated()

def get_game_offsets():
    """Get game offsets"""
    return auth_system.get_offsets()

def cleanup_auth():
    """Cleanup authentication system"""
    auth_system.cleanup()