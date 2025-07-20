import re
from typing import Optional

def validate_username(username: str) -> bool:
    """Validate X username format"""
    if not username:
        return False
    
    # Remove @ if present
    username = username.replace('@', '').strip()
    
    # Check length (1-15 characters)
    if len(username) < 1 or len(username) > 15:
        return False
    
    # Check format (alphanumeric and underscores only)
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False
    
    return True

def validate_pagination(page: int, per_page: int, max_per_page: int = 100) -> tuple:
    """Validate pagination parameters"""
    page = max(1, page)
    per_page = min(max(1, per_page), max_per_page)
    return page, per_page