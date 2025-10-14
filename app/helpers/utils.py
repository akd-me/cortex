import hashlib
import json
from datetime import datetime
from typing import Any, Dict, Optional


def generate_hash(data: str) -> str:
    """Generate SHA-256 hash of data"""
    return hashlib.sha256(data.encode()).hexdigest()


def format_timestamp(dt: datetime) -> str:
    """Format datetime to ISO string"""
    return dt.isoformat()


def safe_json_dumps(obj: Any) -> str:
    """Safely serialize object to JSON string"""
    try:
        return json.dumps(obj, default=str)
    except (TypeError, ValueError):
        return str(obj)


def validate_email(email: str) -> bool:
    """Basic email validation"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def sanitize_string(text: str) -> str:
    """Sanitize string input"""
    if not text:
        return ""
    return text.strip()


def get_env_var(key: str, default: Optional[str] = None) -> Optional[str]:
    """Get environment variable with default"""
    import os
    return os.getenv(key, default)
