# Handles master password security using bcrypt hashing
# bcrypt is a one-way hash — the plain password is NEVER stored anywhere

import bcrypt
import sqlite3

DATABASE = "database.db"

def hash_master_password(plain_password: str) -> str:
    """
    Hashes the master password using bcrypt with auto-generated salt.
    bcrypt is slow by design, making brute-force attacks very difficult.
    
    Args:
        plain_password: The master password entered by the user
    Returns:
        Hashed password string (safe to store in database)
    """
    # Generate salt and hash the password
    password_bytes = plain_password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def verify_master_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain password against a stored bcrypt hash.
    Returns True if password matches, False otherwise.
    
    Args:
        plain_password: Password entered by user during login
        hashed_password: The stored bcrypt hash from the database
    Returns:
        Boolean — True if correct, False if wrong
    """
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)

def is_master_password_set() -> bool:
    """
    Checks if a master password has already been created.
    Used to decide whether to show 'Create' or 'Login' on the login page.
    Returns True if master password exists in DB, False otherwise.
    """
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM master_password")
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0
    except Exception:
        return False

def save_master_password(plain_password: str):
    """
    Hashes and saves the master password to the database.
    Called only once during initial setup.
    
    Args:
        plain_password: The master password chosen by the user
    """
    hashed = hash_master_password(plain_password)
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    # Store the hashed master password
    cursor.execute("INSERT INTO master_password (hashed_password) VALUES (?)", (hashed,))
    conn.commit()
    conn.close()

def get_stored_master_hash() -> str:
    """
    Retrieves the stored bcrypt hash from the database.
    Used during login verification.
    Returns the hash string or None if not found.
    """
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT hashed_password FROM master_password LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    if row:
        return row[0]
    return None
