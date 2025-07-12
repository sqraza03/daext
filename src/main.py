import sys
import os
import traceback

# Add the src directory to Python path for imports
if hasattr(sys, '_MEIPASS'):
    # Running as PyInstaller bundle
    sys.path.insert(0, sys._MEIPASS)
else:
    # Running as script
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from core.enhanced_overlay import EnhancedApp
    from core.security import initialize_security, cleanup_security
except ImportError as e:
    print(f"Import error: {e}")
    print("Current working directory:", os.getcwd())
    print("Python path:", sys.path)
    input("Press Enter to exit...")
    sys.exit(1)

def main():
    """Enhanced main function with security"""
    try:
        # Ensure we're on Windows
        if os.name != 'nt':
            print("This application only runs on Windows")
            input("Press Enter to exit...")
            sys.exit(1)
        
        # Initialize security system
        if not initialize_security():
            print("Security initialization failed")
            input("Press Enter to exit...")
            sys.exit(1)
        
        # Create and run enhanced app
        app = EnhancedApp()
        app.run()
        
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
    except Exception as e:
        print(f"Critical error: {e}")
        input("Press Enter to exit...")
    finally:
        cleanup_security()
        print("Application closed")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()