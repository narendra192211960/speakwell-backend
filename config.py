import os
from dotenv import load_dotenv

# Load .env file from the same directory as this file
basedir = os.path.abspath(os.path.dirname(__file__))
env_path = os.path.join(basedir, '.env')
print(f"[Config] --- Startup Diagnostics ---")
print(f"[Config] Base directory: {basedir}")
print(f"[Config] Loading .env from: {env_path}")

if os.path.exists(env_path):
    print(f"[Config] .env file FOUND. Size: {os.path.getsize(env_path)} bytes")
    # Using override=True to ensure we take values from .env even if already set in shell
    load_dotenv(dotenv_path=env_path, override=True)
    print(f"[Config] load_dotenv called.")
else:
    print(f"[Config] ERROR: .env file NOT FOUND at {env_path}")

class Config:
    # Database Configuration - Read once at startup
    DB_HOST = os.environ.get("DB_HOST", "localhost")
    DB_USER = os.environ.get("DB_USER", "root")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
    DB_NAME = os.environ.get("DB_NAME", "speakwell")

    # Flask Configuration
    FLASK_HOST = "0.0.0.0"
    FLASK_PORT = 5000
    DEBUG = True

    # SMTP Configuration (Email)
    SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
    SMTP_USER = os.environ.get("SMTP_USER", "aispeakwell@gmail.com")
    SMTP_APP_PASSWORD = os.environ.get("SMTP_APP_PASSWORD", "")

    # Gemini API Configuration - Use a property to ensure we get latest env if needed
    @property
    def GEMINI_API_KEYS(self):
        keys_str = os.environ.get("GEMINI_API_KEYS", "")
        return [k.strip() for k in keys_str.split(",") if k.strip()]

# Create an instance to be used by the app, but also allow class access if needed
# Note: Since the app uses 'Config.GEMINI_API_KEYS', we'll wrap it in a smarter way.
class ConfigWrapper:
    def __init__(self, original_config):
        self._config = original_config
    
    def __getattr__(self, name):
        val = getattr(self._config, name)
        if isinstance(val, property):
            return val.__get__(self._config, self._config.__class__)
        return val
    
    @property
    def GEMINI_API_KEYS(self):
        keys_str = os.environ.get("GEMINI_API_KEYS", "")
        return [k.strip() for k in keys_str.split(",") if k.strip()]

Config = ConfigWrapper(Config)

