import sys
import os
import traceback
import io

# Add the src directory to Python path for imports
if hasattr(sys, '_MEIPASS'):
    # Running as PyInstaller bundle
    sys.path.insert(0, sys._MEIPASS)
    sys.path.insert(0, os.path.join(sys._MEIPASS, 'src'))
else:
    # Running as script
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

# Fix stdin issue for PyInstaller
if not hasattr(sys, 'stdin') or sys.stdin is None:
    sys.stdin = io.StringIO()

try:
    # Try different import paths
    try:
        from core.enhanced_overlay import EnhancedApp
        from core.security import initialize_security, cleanup_security
    except ImportError:
        # Try absolute imports
        from src.core.enhanced_overlay import EnhancedApp
        from src.core.security import initialize_security, cleanup_security
except ImportError as e:
    print(f"Import error: {e}")
    print("Current working directory:", os.getcwd())
    print("Python path:", sys.path)
    print("Press any key to exit...")
    try:
        input()
    except:
        import time
        time.sleep(5)
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
        print("Press any key to exit...")
        try:
            input()
        except:
            import time
            time.sleep(5)
    finally:
        cleanup_security()
        print("Application closed")
        print("Press any key to exit...")
        try:
            input()
        except:
            import time
            time.sleep(5)

if __name__ == "__main__":
    main()