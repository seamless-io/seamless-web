"""
Generates a user API key
"""
import secrets

API_KEY_LENGTH = 20


def generate_api_key():
    """
    Generates an API key.
    Returns:
        str
    """
    api_key = secrets.token_urlsafe(API_KEY_LENGTH)
    return api_key
