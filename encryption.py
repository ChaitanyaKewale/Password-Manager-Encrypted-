# Handles all encryption and decryption of passwords using Fernet (AES symmetric encryption)
# Fernet guarantees that a message encrypted cannot be manipulated or read without the key

import os
from cryptography.fernet import Fernet

# Path where the secret encryption key is stored
KEY_FILE = "secret.key"

def generate_key():
    """
    Generates a new Fernet encryption key and saves it to a file.
    This key is used to encrypt and decrypt all stored passwords.
    Called only ONCE when the app is first set up.
    """
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as key_file:
        key_file.write(key)
    return key

def load_key():
    """
    Loads the existing encryption key from the key file.
    If the key file does not exist, generates a new one automatically.
    Returns the key as bytes.
    """
    if not os.path.exists(KEY_FILE):
        return generate_key()
    with open(KEY_FILE, "rb") as key_file:
        return key_file.read()

def encrypt_password(plain_password: str) -> str:
    """
    Encrypts a plain text password using the Fernet key.
    Returns the encrypted password as a UTF-8 decoded string (safe to store in DB).
    
    Args:
        plain_password: The raw password string entered by the user
    Returns:
        Encrypted password string
    """
    key = load_key()
    fernet = Fernet(key)
    # Encode the plain password to bytes, then encrypt
    encrypted = fernet.encrypt(plain_password.encode())
    # Decode to string so it can be stored in SQLite TEXT column
    return encrypted.decode()

def decrypt_password(encrypted_password: str) -> str:
    """
    Decrypts an encrypted password back to plain text.
    Only works if the same key is used that was used to encrypt.
    
    Args:
        encrypted_password: The encrypted password string retrieved from DB
    Returns:
        Decrypted plain text password string
    """
    key = load_key()
    fernet = Fernet(key)
    # Encode encrypted string back to bytes, then decrypt
    decrypted = fernet.decrypt(encrypted_password.encode())
    return decrypted.decode()
