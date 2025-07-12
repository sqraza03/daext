import pyMeow as pm
import ctypes
import os
import sys

try:
    from ui.auth_window import AuthenticationWindow
    from ui.materials.draw import *
    from ui.controllers.control import *
    from ui.resources.fonts import *
    from core.utils import *
    from core.auth import auth_system, is_user_authenticated, cleanup_auth
    from features.esp import *
    from features.aimbot import *
    from features.trigger import *
except ImportError:
    # Try with src prefix
    from src.ui.auth_window import AuthenticationWindow
    from src.ui.materials.draw import *
    from src.ui.controllers.control import *
    from src.ui.resources.fonts import *
    from src.core.utils import *
    from src.core.auth import auth_system, is_user_authenticated, cleanup_auth
    from src.features.esp import *
    from src.features.aimbot import *
    from src.features.trigger import *

class EnhancedApp:
    def __init__(self):
        # Show authentication window first
        auth_window = AuthenticationWindow(auth_system)
        authenticated = auth_window.run()
        
        if not authenticated:
            print("Authentication failed. Exiting...")
            sys.exit(1)
        
        # Check if CS2 is running
        if not pm.process_exists(processName="cs2.exe"):
            ctypes.windll.user32.MessageBoxW(
                0, 
                "The cs2.exe process was not found.\n\nPlease open the game and try again.", 
                "Warning", 
                0x30
            )
            cleanup_auth()
            os._exit(0)
        
        # Generate random title for overlay
        title = Utils.random_string(10)

        # Initialize overlay with enhanced settings
        pm.overlay_init(target=title, title=title, fps=144, exitKey=0)
        pm.set_fps(pm.get_monitor_refresh_rate())

        # Create directories
        os.makedirs(name="C:/Fury", exist_ok=True)
        os.makedirs(name="C:/Fury/logs", exist_ok=True)
        os.makedirs(name="C:/Fury/configs", exist_ok=True)

        # Load fonts
        Fonts.load(name="arial.ttf", ref=1)
        Fonts.load(name="icons.ttf", ref=2)
        Fonts.load(name="weapon.ttf", ref=3)

        # Initialize process and module
        self.process = pm.open_process("cs2.exe")
        self.module = pm.get_module(self.process, "client.dll")["base"]

        # Initialize features
        self.esp = ESP(self.process, self.module)
        self.aimbot = Aimbot(self.process, self.module)
        self.trigger = Trigger(self.process, self.module)
        
        # Enhanced security checks
        self.security_checks_enabled = True
        self.last_security_check = 0
        
        print("Fury initialized successfully!")

    def security_check(self):
        """Enhanced security checks"""
        if not self.security_checks_enabled:
            return True
            
        current_time = pm.get_time()
        
        # Run security checks every 30 seconds
        if current_time - self.last_security_check < 30000:
            return True
            
        self.last_security_check = current_time
        
        # Check if user is still authenticated
        if not is_user_authenticated():
            return False
            
        # Check if CS2 is still running
        if not pm.process_exists(processName="cs2.exe"):
            return False
            
        return True

    def run(self):
        """Enhanced main loop with security checks"""
        try:
            while pm.overlay_loop():
                try:
                    # Security checks
                    if not self.security_check():
                        print("Security check failed. Exiting...")
                        break
                    
                    pm.begin_drawing()

                    # Update features
                    self.esp.update()
                    self.aimbot.update()
                    self.trigger.update()

                    # Draw UI
                    Draw.draw_menu()

                    # Handle controls
                    Control.update_mouse()
                    Control.toggle_menu()
                    Control.auto_close()
                    Control.drag_menu()

                    pm.end_drawing()
                    
                except Exception as e:
                    # Log errors but continue running
                    self.log_error(f"Runtime error: {e}")
                    continue
                    
        except KeyboardInterrupt:
            print("Application interrupted by user")
        except Exception as e:
            self.log_error(f"Critical error: {e}")
        finally:
            self.cleanup()

    def log_error(self, error_message):
        """Log errors to file"""
        try:
            timestamp = pm.get_time()
            log_file = "C:/Fury/logs/error.log"
            
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] {error_message}\n")
        except:
            pass  # Fail silently if logging fails

    def cleanup(self):
        """Cleanup resources"""
        print("Cleaning up...")
        cleanup_auth()
        pm.overlay_close()

    def __del__(self):
        """Destructor"""
        self.cleanup()