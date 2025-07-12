import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime
import threading
import time
import sys

class AuthenticationWindow:
    def __init__(self, auth_system):
        self.auth_system = auth_system
        self.root = tk.Tk()
        self.authenticated = False
        self.stored_key = None
        self.expiration_date = None
        
        # Load stored key if exists
        self.load_stored_key()
        
        self.setup_window()
        self.create_widgets()
        
    def setup_window(self):
        """Setup main window properties"""
        self.root.title("Fury Authentication")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        self.root.configure(bg='#0B0C0E')
        
        # Center window on screen
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.root.winfo_screenheight() // 2) - (400 // 2)
        self.root.geometry(f"500x400+{x}+{y}")
        
        # Configure styles
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure custom styles
        style.configure('Title.TLabel', 
                       background='#0B0C0E', 
                       foreground='#1b90c4', 
                       font=('Arial', 20, 'bold'))
        
        style.configure('Subtitle.TLabel', 
                       background='#0B0C0E', 
                       foreground='#8d969e', 
                       font=('Arial', 12))
        
        style.configure('Info.TLabel', 
                       background='#0B0C0E', 
                       foreground='#747f87', 
                       font=('Arial', 10))
        
        style.configure('Success.TLabel', 
                       background='#0B0C0E', 
                       foreground='#42d680', 
                       font=('Arial', 11, 'bold'))
        
        style.configure('Error.TLabel', 
                       background='#0B0C0E', 
                       foreground='#fc0362', 
                       font=('Arial', 11, 'bold'))
        
        style.configure('Custom.TEntry',
                       fieldbackground='#1C252F',
                       bordercolor='#1b90c4',
                       insertcolor='#ffffff',
                       foreground='#ffffff')
        
        style.configure('Custom.TButton',
                       background='#1b90c4',
                       foreground='#ffffff',
                       font=('Arial', 11, 'bold'),
                       borderwidth=0,
                       relief='flat',
                       padding=(10, 5))
        
        style.map('Custom.TButton',
                 background=[('active', '#2c8cbf')],
                 relief=[('pressed', 'flat'), ('!pressed', 'flat')])
    
    def create_widgets(self):
        """Create and layout all widgets"""
        main_frame = tk.Frame(self.root, bg='#0B0C0E')
        main_frame.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Title
        title_label = ttk.Label(main_frame, text="FURY", style='Title.TLabel')
        title_label.pack(pady=(0, 10))
        
        subtitle_label = ttk.Label(main_frame, text="Authentication System", style='Subtitle.TLabel')
        subtitle_label.pack(pady=(0, 30))
        
        # HWID Section
        hwid_frame = tk.Frame(main_frame, bg='#111316', relief='solid', bd=1)
        hwid_frame.pack(fill='x', pady=(0, 20))
        
        hwid_title = ttk.Label(hwid_frame, text="Hardware ID", style='Subtitle.TLabel')
        hwid_title.pack(pady=(10, 5))
        
        # Get and display HWID
        hwid = self.auth_system.get_hwid()
        self.hwid_label = ttk.Label(hwid_frame, text=hwid[:32] + "...", style='Info.TLabel', cursor='hand2')
        self.hwid_label.pack(pady=(0, 10))
        
        # Make HWID clickable to copy
        self.hwid_label.bind("<Button-1>", lambda e: self.copy_hwid_to_clipboard(hwid))
        
        # Add copy instruction
        copy_instruction = ttk.Label(hwid_frame, text="(Click to copy)", style='Info.TLabel')
        copy_instruction.pack(pady=(0, 10))
        
        # Key Input Section
        key_frame = tk.Frame(main_frame, bg='#111316', relief='solid', bd=1)
        key_frame.pack(fill='x', pady=(0, 20))
        
        key_title = ttk.Label(key_frame, text="Authentication Key", style='Subtitle.TLabel')
        key_title.pack(pady=(10, 5))
        
        self.key_entry = ttk.Entry(key_frame, style='Custom.TEntry', font=('Arial', 11), width=40)
        self.key_entry.pack(pady=(0, 10))
        
        # If we have a stored key, check it automatically
        if self.stored_key:
            self.key_entry.insert(0, self.stored_key)
            self.key_entry.configure(state='disabled')
        
        # Status Section
        self.status_frame = tk.Frame(main_frame, bg='#0B0C0E')
        self.status_frame.pack(fill='x', pady=(0, 20))
        
        self.status_label = ttk.Label(self.status_frame, text="", style='Info.TLabel')
        self.status_label.pack()
        
        # Expiration info (hidden initially)
        self.expiry_frame = tk.Frame(main_frame, bg='#111316', relief='solid', bd=1)
        self.expiry_label = ttk.Label(self.expiry_frame, text="", style='Success.TLabel')
        
        # Buttons
        button_frame = tk.Frame(main_frame, bg='#0B0C0E')
        button_frame.pack(fill='x')
        
        if self.stored_key:
            # If we have a stored key, show different buttons
            self.verify_button = ttk.Button(button_frame, text="Verify Stored Key", 
                                          style='Custom.TButton', command=self.verify_stored_key)
            self.verify_button.pack(side='left', padx=(0, 10), pady=10)
            
            self.new_key_button = ttk.Button(button_frame, text="Use New Key", 
                                           style='Custom.TButton', command=self.use_new_key)
            self.new_key_button.pack(side='left', pady=10)
        else:
            self.auth_button = ttk.Button(button_frame, text="Authenticate", 
                                        style='Custom.TButton', command=self.authenticate)
            self.auth_button.pack(side='left', padx=(0, 10), pady=10)
        
        self.exit_button = ttk.Button(button_frame, text="Exit", 
                                    style='Custom.TButton', command=self.exit_app)
        self.exit_button.pack(side='right', pady=10)
        
        # Auto-verify stored key if available
        if self.stored_key:
            self.root.after(1000, self.verify_stored_key)
    
    def copy_hwid_to_clipboard(self, hwid):
        """Copy HWID to clipboard"""
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(hwid)
            self.root.update()  # Required for clipboard to work
            
            # Show temporary feedback
            original_text = self.hwid_label.cget('text')
            self.hwid_label.configure(text="HWID Copied to Clipboard!")
            self.root.after(2000, lambda: self.hwid_label.configure(text=original_text))
            
        except Exception as e:
            print(f"Error copying to clipboard: {e}")
            # Fallback: print HWID to console
            print(f"HWID: {hwid}")
    
    def load_stored_key(self):
        """Load stored authentication key"""
        try:
            key_file = "C:/Fury/auth_key.json"
            if os.path.exists(key_file):
                with open(key_file, 'r') as f:
                    data = json.load(f)
                    self.stored_key = data.get('key')
        except Exception as e:
            print(f"Error loading stored key: {e}")
    
    def save_key(self, key):
        """Save authentication key"""
        try:
            os.makedirs("C:/Fury", exist_ok=True)
            key_file = "C:/Fury/auth_key.json"
            with open(key_file, 'w') as f:
                json.dump({'key': key, 'saved_at': datetime.now().isoformat()}, f)
        except Exception as e:
            print(f"Error saving key: {e}")
    
    def clear_stored_key(self):
        """Clear stored authentication key"""
        try:
            key_file = "C:/Fury/auth_key.json"
            if os.path.exists(key_file):
                os.remove(key_file)
        except Exception as e:
            print(f"Error clearing stored key: {e}")
    
    def update_status(self, message, style='Info.TLabel'):
        """Update status message"""
        self.status_label.configure(text=message, style=style)
        self.root.update()
    
    def show_expiry_info(self, expiry_date):
        """Show expiration information"""
        try:
            if isinstance(expiry_date, str):
                expiry_dt = datetime.fromisoformat(expiry_date.replace('Z', '+00:00'))
            else:
                expiry_dt = expiry_date
            
            days_left = (expiry_dt - datetime.now()).days
            
            if days_left > 0:
                expiry_text = f"Key expires in {days_left} days ({expiry_dt.strftime('%Y-%m-%d %H:%M')})"
                self.expiry_label.configure(text=expiry_text, style='Success.TLabel')
            else:
                expiry_text = f"Key expired on {expiry_dt.strftime('%Y-%m-%d %H:%M')}"
                self.expiry_label.configure(text=expiry_text, style='Error.TLabel')
            
            self.expiry_label.pack(pady=(5, 10))
            self.expiry_frame.pack(fill='x', pady=(0, 20))
            
        except Exception as e:
            print(f"Error showing expiry info: {e}")
    
    def verify_stored_key(self):
        """Verify the stored authentication key"""
        if not self.stored_key:
            return
        
        self.update_status("Verifying stored key...", 'Info.TLabel')
        
        # Run authentication in a separate thread
        threading.Thread(target=self._authenticate_thread, args=(self.stored_key,), daemon=True).start()
    
    def use_new_key(self):
        """Allow user to enter a new key"""
        self.clear_stored_key()
        self.key_entry.configure(state='normal')
        self.key_entry.delete(0, tk.END)
        
        # Update buttons
        for widget in self.status_frame.winfo_children():
            widget.destroy()
        
        self.status_label = ttk.Label(self.status_frame, text="Enter your new authentication key", style='Info.TLabel')
        self.status_label.pack()
        
        # Hide expiry info
        self.expiry_frame.pack_forget()
        
        # Update buttons
        button_frame = self.status_frame.master.winfo_children()[-1]
        for widget in button_frame.winfo_children():
            widget.destroy()
        
        self.auth_button = ttk.Button(button_frame, text="Authenticate", 
                                    style='Custom.TButton', command=self.authenticate)
        self.auth_button.pack(side='left', padx=(0, 10), pady=10)
        
        self.exit_button = ttk.Button(button_frame, text="Exit", 
                                    style='Custom.TButton', command=self.exit_app)
        self.exit_button.pack(side='right', pady=10)
    
    def authenticate(self):
        """Authenticate with entered key"""
        key = self.key_entry.get().strip()
        if not key:
            self.update_status("Please enter an authentication key", 'Error.TLabel')
            return
        
        self.update_status("Authenticating...", 'Info.TLabel')
        
        # Disable button during authentication
        self.auth_button.configure(state='disabled')
        
        # Run authentication in a separate thread
        threading.Thread(target=self._authenticate_thread, args=(key,), daemon=True).start()
    
    def _authenticate_thread(self, key):
        """Authentication thread"""
        try:
            # Connect to database
            if not self.auth_system.connect_to_database():
                self.root.after(0, lambda: self.update_status("Failed to connect to authentication server", 'Error.TLabel'))
                self.root.after(0, lambda: self._enable_auth_button())
                return
            
            # Check versions
            if not self.auth_system.check_versions():
                self.root.after(0, lambda: self.update_status("Version check failed. Please update the application.", 'Error.TLabel'))
                self.root.after(0, lambda: self._enable_auth_button())
                return
            
            # Get HWID
            hwid = self.auth_system.get_hwid()
            if not hwid:
                self.root.after(0, lambda: self.update_status("Failed to generate hardware ID", 'Error.TLabel'))
                self.root.after(0, lambda: self._enable_auth_button())
                return
            
            # Validate key and HWID
            result = self.auth_system.validate_key_and_hwid_detailed(key, hwid)
            
            if result['success']:
                # Authentication successful
                self.save_key(key)
                self.auth_system.user_key = key
                self.authenticated = True
                
                # Get public IP and send Discord notification
                public_ip = self.auth_system.get_public_ip()
                self.auth_system.send_discord_webhook(key, public_ip)
                
                # Connect to WebSocket
                self.auth_system.connect_websocket()
                
                self.root.after(0, lambda: self.update_status("Authentication successful!", 'Success.TLabel'))
                self.root.after(0, lambda: self.show_expiry_info(result['expiration_date']))
                self.root.after(0, lambda: self._show_success_screen())
                
            else:
                # Authentication failed
                error_msg = result['error']
                if 'expired' in error_msg.lower():
                    error_msg += "\n\nPlease purchase a new key to continue."
                elif 'hwid mismatch' in error_msg.lower():
                    error_msg += "\n\nPlease contact support to reset your HWID."
                
                self.root.after(0, lambda: self.update_status(error_msg, 'Error.TLabel'))
                self.root.after(0, lambda: self._enable_auth_button())
                
        except Exception as e:
            self.root.after(0, lambda: self.update_status(f"Authentication error: {str(e)}", 'Error.TLabel'))
            self.root.after(0, lambda: self._enable_auth_button())
    
    def _enable_auth_button(self):
        """Re-enable authentication button"""
        if hasattr(self, 'auth_button'):
            self.auth_button.configure(state='normal')
        if hasattr(self, 'verify_button'):
            self.verify_button.configure(state='normal')
    
    def _show_success_screen(self):
        """Show success screen with countdown"""
        # Update button to show launch
        button_frame = None
        for widget in self.root.winfo_children():
            for child in widget.winfo_children():
                if isinstance(child, tk.Frame) and child.winfo_children():
                    last_child = child.winfo_children()[-1]
                    if isinstance(last_child, tk.Frame):
                        button_frame = last_child
                        break
        
        if button_frame:
            for widget in button_frame.winfo_children():
                widget.destroy()
            
            self.launch_button = ttk.Button(button_frame, text="Launch Fury", 
                                          style='Custom.TButton', command=self.launch_fury)
            self.launch_button.pack(side='left', padx=(0, 10), pady=10)
            
            self.exit_button = ttk.Button(button_frame, text="Exit", 
                                        style='Custom.TButton', command=self.exit_app)
            self.exit_button.pack(side='right', pady=10)
    
    def launch_fury(self):
        """Launch the main Fury application"""
        self.update_status("Launching Fury...", 'Success.TLabel')
        
        # Start countdown
        for i in range(3, 0, -1):
            self.update_status(f"Launching Fury in {i}...", 'Success.TLabel')
            time.sleep(1)
        
        self.root.destroy()
    
    def exit_app(self):
        """Exit the application"""
        try:
            input()
        except:
            import time
            time.sleep(3)
        self.root.destroy()
    
    def run(self):
        """Run the authentication window"""
        self.root.mainloop()
        return self.authenticated