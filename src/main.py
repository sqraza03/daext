from core.enhanced_overlay import *
from core.security import initialize_security, cleanup_security
import sys

def main():
    """Enhanced main function with security"""
    try:
        # Initialize security system
        if not initialize_security():
            print("Security initialization failed")
            sys.exit(1)
        
        # Create and run enhanced app
        app = EnhancedApp()
        app.run()
        
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
    except Exception as e:
        print(f"Critical error: {e}")
    finally:
        cleanup_security()
        print("Application closed")

if __name__ == "__main__":
    main()