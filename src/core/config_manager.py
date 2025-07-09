import json
import os
from datetime import datetime
import hashlib

class ConfigManager:
    def __init__(self):
        self.config_dir = "C:/Fury/configs"
        self.user_config_file = os.path.join(self.config_dir, "user_settings.json")
        self.default_config = {
            "version": "2.0",
            "created": datetime.now().isoformat(),
            "security": {
                "enable_integrity_checks": True,
                "enable_process_monitoring": True,
                "enable_anti_debug": True
            },
            "features": {
                "aimbot": {
                    "enabled": False,
                    "fov": 90,
                    "smooth": 5,
                    "only_spotted": True,
                    "keybind": "none"
                },
                "trigger": {
                    "enabled": False,
                    "delay": 0.1,
                    "keybind": "none"
                },
                "esp": {
                    "enemy": {
                        "box": {"enabled": True, "color": "#d1c75c"},
                        "bone": {"enabled": True, "color": "#fc0362"},
                        "name": {"enabled": True, "color": "#e0e0e0"},
                        "health": {"enabled": True, "color": "#42d680"},
                        "weapon": {"enabled": True, "color": "#fc0362"}
                    },
                    "friend": {
                        "box": {"enabled": False, "color": "#2c8cbf"},
                        "bone": {"enabled": False, "color": "#2c8cbf"},
                        "name": {"enabled": False, "color": "#e0e0e0"},
                        "health": {"enabled": False, "color": "#42d680"},
                        "weapon": {"enabled": False, "color": "#2c8cbf"}
                    }
                },
                "misc": {
                    "crosshair": {"enabled": False, "color": "#c71844"},
                    "ignore_team": False
                }
            }
        }

    def ensure_config_dir(self):
        """Ensure config directory exists"""
        os.makedirs(self.config_dir, exist_ok=True)

    def load_config(self):
        """Load user configuration"""
        self.ensure_config_dir()
        
        try:
            if os.path.exists(self.user_config_file):
                with open(self.user_config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    
                # Merge with default config to ensure all keys exist
                return self.merge_configs(self.default_config, config)
            else:
                # Create default config file
                self.save_config(self.default_config)
                return self.default_config.copy()
                
        except Exception as e:
            print(f"Error loading config: {e}")
            return self.default_config.copy()

    def save_config(self, config):
        """Save user configuration"""
        self.ensure_config_dir()
        
        try:
            config["last_modified"] = datetime.now().isoformat()
            
            with open(self.user_config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
                
            return True
            
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    def merge_configs(self, default, user):
        """Merge user config with default config"""
        result = default.copy()
        
        for key, value in user.items():
            if key in result:
                if isinstance(value, dict) and isinstance(result[key], dict):
                    result[key] = self.merge_configs(result[key], value)
                else:
                    result[key] = value
            else:
                result[key] = value
                
        return result

    def get_config_hash(self, config):
        """Get hash of configuration for integrity checking"""
        config_str = json.dumps(config, sort_keys=True)
        return hashlib.sha256(config_str.encode()).hexdigest()

    def backup_config(self):
        """Create backup of current configuration"""
        try:
            if os.path.exists(self.user_config_file):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_file = os.path.join(
                    self.config_dir, 
                    f"backup_{timestamp}.json"
                )
                
                import shutil
                shutil.copy2(self.user_config_file, backup_file)
                return True
                
        except Exception as e:
            print(f"Error creating config backup: {e}")
            
        return False

    def restore_config(self, backup_file):
        """Restore configuration from backup"""
        try:
            if os.path.exists(backup_file):
                import shutil
                shutil.copy2(backup_file, self.user_config_file)
                return True
                
        except Exception as e:
            print(f"Error restoring config: {e}")
            
        return False

# Global config manager instance
config_manager = ConfigManager()

def load_user_config():
    """Load user configuration"""
    return config_manager.load_config()

def save_user_config(config):
    """Save user configuration"""
    return config_manager.save_config(config)

def backup_user_config():
    """Backup user configuration"""
    return config_manager.backup_config()