import sys
import os
import traceback
import io

# Fix for PyInstaller - ensure stdin is available
if not hasattr(sys, 'stdin') or sys.stdin is None:
    sys.stdin = io.StringIO()

# Add paths for PyInstaller
if hasattr(sys, '_MEIPASS'):
    # Running as PyInstaller bundle
    base_path = sys._MEIPASS
    sys.path.insert(0, base_path)
    sys.path.insert(0, os.path.join(base_path, 'src'))
else:
    # Running as script
    base_path = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, base_path)
    sys.path.insert(0, os.path.join(base_path, '..'))

def safe_import():
    """Safely import all required modules with detailed error reporting"""
    try:
        # Import core modules
        from core.enhanced_overlay import EnhancedApp
        from core.security import initialize_security, cleanup_security
        return EnhancedApp, initialize_security, cleanup_security
    except ImportError as e:
        print(f"Failed to import core modules: {e}")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Python path: {sys.path}")
        print(f"Base path: {base_path if 'base_path' in locals() else 'Unknown'}")
        
        # Try to list available modules for debugging
        try:
            if hasattr(sys, '_MEIPASS'):
                print(f"PyInstaller temp path: {sys._MEIPASS}")
                if os.path.exists(sys._MEIPASS):
                    print("Contents of PyInstaller temp path:")
                    for item in os.listdir(sys._MEIPASS):
                        print(f"  {item}")
        except:
            pass
        
        return None, None, None

def show_error_and_wait(message):
    """Show error message and wait for user input"""
    print(f"\nERROR: {message}")
    print("\nPress Enter to exit...")
    try:
        input()
    except:
        import time
        time.sleep(10)

def main():
    """Enhanced main function with comprehensive error handling"""
    try:
        # Ensure we're on Windows
        if os.name != 'nt':
            show_error_and_wait("This application only runs on Windows")
            return
        
        # Import required modules
        EnhancedApp, initialize_security, cleanup_security = safe_import()
        
        if not EnhancedApp:
            show_error_and_wait("Failed to load required modules. Please check the installation.")
            return
        
        # Initialize security system
        try:
            if not initialize_security():
                show_error_and_wait("Security initialization failed")
                return
        except Exception as e:
            print(f"Security initialization error: {e}")
            # Continue without security if it fails
        
        # Create and run enhanced app
        print("Starting Fury...")
        app = EnhancedApp()
        app.run()
        
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
    except Exception as e:
        error_msg = f"Critical error: {e}\n\nTraceback:\n{traceback.format_exc()}"
        show_error_and_wait(error_msg)
    finally:
        try:
            if 'cleanup_security' in locals() and cleanup_security:
                cleanup_security()
        except:
            pass
        
        print("Application closed")

if __name__ == "__main__":
    main()