"""
Generates a user API key
"""
import secrets

API_KEY_LENGTH = 20  # Must be dividable by 2 !!!


def generate_api_key() -> str:
    """
    Generates an API key.
    Returns:
        Return a random text string, in hexadecimal.
        The string has API_KEY_LENGTH/2 random bytes, each byte converted to two hex digits.
    """
    api_key = secrets.token_hex(int(API_KEY_LENGTH / 2))
    return api_key
