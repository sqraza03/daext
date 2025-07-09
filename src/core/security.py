import hashlib
import time
import threading
import psutil
import os
import ctypes
from ctypes import wintypes
import winreg

class SecurityManager:
    def __init__(self):
        self.security_enabled = True
        self.last_integrity_check = 0
        self.process_whitelist = ["cs2.exe", "steam.exe"]
        self.suspicious_processes = [
            "cheatengine", "processhacker", "x64dbg", "ollydbg", 
            "ida", "wireshark", "fiddler", "charles"
        ]
        self.monitoring_thread = None
        self.stop_monitoring = False

    def calculate_file_hash(self, filepath):
        """Calculate SHA256 hash of a file"""
        try:
            with open(filepath, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except:
            return None

    def check_file_integrity(self, filepath, expected_hash):
        """Check if file integrity is maintained"""
        current_hash = self.calculate_file_hash(filepath)
        return current_hash == expected_hash

    def scan_suspicious_processes(self):
        """Scan for suspicious processes"""
        suspicious_found = []
        
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                process_name = proc.info['name'].lower()
                for suspicious in self.suspicious_processes:
                    if suspicious in process_name:
                        suspicious_found.append(proc.info['name'])
            except:
                continue
                
        return suspicious_found

    def check_debugger_presence(self):
        """Check for debugger presence"""
        try:
            # Check IsDebuggerPresent
            kernel32 = ctypes.windll.kernel32
            if kernel32.IsDebuggerPresent():
                return True
                
            # Check remote debugger
            remote_debugger = ctypes.c_bool()
            kernel32.CheckRemoteDebuggerPresent(
                kernel32.GetCurrentProcess(),
                ctypes.byref(remote_debugger)
            )
            
            return remote_debugger.value
        except:
            return False

    def check_vm_environment(self):
        """Check if running in virtual machine"""
        vm_indicators = [
            "VBOX", "VMWARE", "QEMU", "VIRTUAL", "PARALLELS"
        ]
        
        try:
            # Check system manufacturer
            import platform
            system_info = platform.uname()
            system_str = str(system_info).upper()
            
            for indicator in vm_indicators:
                if indicator in system_str:
                    return True
                    
            # Check registry for VM indicators
            try:
                key = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    r"HARDWARE\DESCRIPTION\System\BIOS"
                )
                
                bios_vendor = winreg.QueryValueEx(key, "SystemManufacturer")[0].upper()
                winreg.CloseKey(key)
                
                for indicator in vm_indicators:
                    if indicator in bios_vendor:
                        return True
            except:
                pass
                
        except:
            pass
            
        return False

    def anti_dump_protection(self):
        """Basic anti-dump protection"""
        try:
            # Make critical sections of memory non-readable
            kernel32 = ctypes.windll.kernel32
            current_process = kernel32.GetCurrentProcess()
            
            # This is a simplified example
            # In practice, you'd protect specific memory regions
            return True
        except:
            return False

    def start_monitoring(self):
        """Start security monitoring thread"""
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            return
            
        self.stop_monitoring = False
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True
        )
        self.monitoring_thread.start()

    def stop_security_monitoring(self):
        """Stop security monitoring"""
        self.stop_monitoring = True
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=1)

    def _monitoring_loop(self):
        """Security monitoring loop"""
        while not self.stop_monitoring:
            try:
                # Check for suspicious processes
                suspicious = self.scan_suspicious_processes()
                if suspicious:
                    print(f"Suspicious processes detected: {suspicious}")
                    # Could implement automatic shutdown here
                
                # Check for debugger
                if self.check_debugger_presence():
                    print("Debugger detected!")
                    # Could implement automatic shutdown here
                
                # Sleep for 5 seconds before next check
                time.sleep(5)
                
            except Exception as e:
                print(f"Security monitoring error: {e}")
                time.sleep(5)

    def perform_integrity_check(self):
        """Perform comprehensive integrity check"""
        current_time = time.time()
        
        # Only run integrity check every 60 seconds
        if current_time - self.last_integrity_check < 60:
            return True
            
        self.last_integrity_check = current_time
        
        try:
            # Check for suspicious processes
            suspicious = self.scan_suspicious_processes()
            if suspicious:
                return False
                
            # Check for debugger
            if self.check_debugger_presence():
                return False
                
            # Check VM environment (optional - might be too restrictive)
            # if self.check_vm_environment():
            #     return False
                
            return True
            
        except Exception as e:
            print(f"Integrity check error: {e}")
            return True  # Fail open to avoid false positives

# Global security manager instance
security_manager = SecurityManager()

def initialize_security():
    """Initialize security system"""
    security_manager.start_monitoring()
    return True

def check_security():
    """Check security status"""
    return security_manager.perform_integrity_check()

def cleanup_security():
    """Cleanup security system"""
    security_manager.stop_security_monitoring()