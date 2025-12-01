"""Fingerprint management utilities."""
import hashlib
from typing import Optional, Dict


def hash_fingerprint(fingerprint: str) -> str:
    """Hash a fingerprint using SHA-256."""
    return hashlib.sha256(fingerprint.encode()).hexdigest()


def validate_fingerprint(fingerprint: str) -> bool:
    """Validate fingerprint format."""
    if not fingerprint or len(fingerprint) < 10:
        return False
    return True


def normalize_device_info(device_info: Optional[Dict]) -> Optional[Dict]:
    """Normalize device information."""
    if not device_info:
        return None
    
    # Extract relevant information
    normalized = {
        "browser": device_info.get("browser", {}).get("name", "Unknown"),
        "os": device_info.get("os", {}).get("name", "Unknown"),
        "device": device_info.get("device", {}).get("type", "Unknown"),
    }
    
    return normalized

