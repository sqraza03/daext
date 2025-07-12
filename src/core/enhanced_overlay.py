import sys
import os
import ctypes

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

try:
    import pyMeow as pm
except ImportError:
    print("Error: pyMeow library not found. Please ensure it's installed.")
    sys.exit(1)

# Import all required modules with error handling
try:
    from ui.auth_window import AuthenticationWindow
    from ui.materials.draw import Draw
    from ui.controllers.control import Control
    from ui.resources.fonts import Fonts
    from core.utils import Utils
    from core.auth import auth_system, is_user_authenticated, cleanup_auth
    from features.esp import ESP
    from features.aimbot import Aimbot
    from features.trigger import Trigger
except ImportError as e:
    print(f"Import error in enhanced_overlay: {e}")
    print("Attempting alternative import paths...")
    try:
        # Try absolute imports
        import ui.auth_window
        import ui.materials.draw
        import ui.controllers.control
        import ui.resources.fonts
        import core.utils
        import core.auth
        import features.esp
        import features.aimbot
        import features.trigger
        
        AuthenticationWindow = ui.auth_window.AuthenticationWindow
        Draw = ui.materials.draw.Draw
        Control = ui.controllers.control.Control
        Fonts = ui.resources.fonts.Fonts
        Utils = core.utils.Utils
        auth_system = core.auth.auth_system
        is_user_authenticated = core.auth.is_user_authenticated
        cleanup_auth = core.auth.cleanup_auth
        ESP = features.esp.ESP
        Aimbot = features.aimbot.Aimbot
        Trigger = features.trigger.Trigger
    except ImportError as e2:
        print(f"Failed to import required modules: {e2}")
        sys.exit(1)

class EnhancedApp:
    def __init__(self):
        print("Initializing Fury...")
        
        # Show authentication window first
        try:
            auth_window = AuthenticationWindow(auth_system)
            authenticated = auth_window.run()
            
            if not authenticated:
                print("Authentication failed. Exiting...")
                sys.exit(1)
        except Exception as e:
            print(f"Authentication window error: {e}")
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
            sys.exit(0)
        
        # Generate random title for overlay
        title = Utils.random_string(10)

        # Initialize overlay with enhanced settings
        try:
            pm.overlay_init(target=title, title=title, fps=144, exitKey=0)
            pm.set_fps(pm.get_monitor_refresh_rate())
        except Exception as e:
            print(f"Failed to initialize overlay: {e}")
            sys.exit(1)

        # Create directories
        os.makedirs(name="C:/Fury", exist_ok=True)
        os.makedirs(name="C:/Fury/logs", exist_ok=True)
        os.makedirs(name="C:/Fury/configs", exist_ok=True)

        # Load fonts
        try:
            Fonts.load(name="arial.ttf", ref=1)
            Fonts.load(name="icons.ttf", ref=2)
            Fonts.load(name="weapon.ttf", ref=3)
        except Exception as e:
            print(f"Failed to load fonts: {e}")
            # Continue without custom fonts

        # Initialize process and module
        try:
            self.process = pm.open_process("cs2.exe")
            self.module = pm.get_module(self.process, "client.dll")["base"]
        except Exception as e:
            print(f"Failed to attach to CS2 process: {e}")
            sys.exit(1)

        # Initialize features
        try:
            self.esp = ESP(self.process, self.module)
            self.aimbot = Aimbot(self.process, self.module)
            self.trigger = Trigger(self.process, self.module)
        except Exception as e:
            print(f"Failed to initialize features: {e}")
            sys.exit(1)
        
        # Enhanced security checks
        self.security_checks_enabled = True
        self.last_security_check = 0
        
        print("Fury initialized successfully!")

    def security_check(self):
        """Enhanced security checks"""
        if not self.security_checks_enabled:
            return True
            
        try:
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
        except:
            return True  # Fail safe

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
            import time
            timestamp = time.time()
            log_file = "C:/Fury/logs/error.log"
            
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] {error_message}\n")
        except:
            pass  # Fail silently if logging fails

    def cleanup(self):
        """Cleanup resources"""
        print("Cleaning up...")
        try:
            cleanup_auth()
        except:
            pass
        try:
            pm.overlay_close()
        except:
            pass

    def __del__(self):
        """Destructor"""
        self.cleanup()