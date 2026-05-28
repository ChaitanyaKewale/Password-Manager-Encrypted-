# app.py
# Main Flask application — handles all routes, sessions, and database operations
# This is the entry point of the Password Manager web app

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import sqlite3
import os
from encryption import encrypt_password, decrypt_password
from auth import (
    is_master_password_set,
    save_master_password,
    verify_master_password,
    get_stored_master_hash
)

# App Configuration


app = Flask(__name__)

# Secret key for session management — in production, use a long random string
app.secret_key = os.urandom(24)

DATABASE = "database.db"

# Database Initialization

def init_db():
    """
    Creates the database and required tables if they don't already exist.
    Called automatically when the app starts.
    Tables:
        - master_password: stores the bcrypt hashed master password
        - passwords: stores website credentials with encrypted passwords
    """
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Table for storing the master password hash (only 1 row ever)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS master_password (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hashed_password TEXT NOT NULL
        )
    """)

    # Table for storing all user credentials
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS passwords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            website TEXT NOT NULL,
            username TEXT NOT NULL,
            encrypted_password TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()

# Helper: Check if user is logged in


def is_logged_in():
    """Returns True if the user has an active authenticated session."""
    return session.get('authenticated') == True

# Route: Login / Setup Page

@app.route('/', methods=['GET', 'POST'])
def login():
    """
    Handles both master password creation (first time) and login (returning user).
    GET: Shows login or setup form depending on whether master password exists.
    POST: Processes the form — either creates or verifies master password.
    """
    master_exists = is_master_password_set()

    if request.method == 'POST':
        password = request.form.get('master_password', '').strip()
        action = request.form.get('action', '')

        # ── First-time Setup ──
        if action == 'create' and not master_exists:
            confirm = request.form.get('confirm_password', '').strip()
            if len(password) < 8:
                flash('Master password must be at least 8 characters.', 'error')
                return redirect(url_for('login'))
            if password != confirm:
                flash('Passwords do not match. Please try again.', 'error')
                return redirect(url_for('login'))
            save_master_password(password)
            flash('Master password created successfully! Please log in.', 'success')
            return redirect(url_for('login'))

        # ── Login ──
        elif action == 'login' and master_exists:
            stored_hash = get_stored_master_hash()
            if verify_master_password(password, stored_hash):
                # Set session as authenticated
                session['authenticated'] = True
                flash('Welcome back! Vault unlocked.', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Incorrect master password. Access denied.', 'error')
                return redirect(url_for('login'))

    return render_template('login.html', master_exists=master_exists)

# Route: Logout

@app.route('/logout')
def logout():
    """Clears the session and redirects to login page."""
    session.clear()
    flash('You have been logged out. Vault locked.', 'success')
    return redirect(url_for('login'))

# Route: Dashboard

@app.route('/dashboard')
def dashboard():
    """
    Main dashboard page shown after successful login.
    Displays total saved passwords and a quick summary.
    Requires authentication — redirects to login if not logged in.
    """
    if not is_logged_in():
        flash('Please log in to access the vault.', 'error')
        return redirect(url_for('login'))

    # Get total count of saved passwords for stats display
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM passwords")
    total = cursor.fetchone()[0]

    # Get 5 most recently added entries for quick view
    cursor.execute("SELECT id, website, username FROM passwords ORDER BY id DESC LIMIT 5")
    recent = cursor.fetchall()
    conn.close()

    return render_template('dashboard.html', total=total, recent=recent)

# Route: Password Vault (View All)

@app.route('/vault')
def vault():
    """
    Shows all stored credentials in a searchable table.
    Passwords are decrypted on-the-fly before displaying.
    Requires authentication.
    """
    if not is_logged_in():
        flash('Please log in to access the vault.', 'error')
        return redirect(url_for('login'))

    search_query = request.args.get('search', '').strip()
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    if search_query:
        # Search by website name or username (case-insensitive)
        cursor.execute(
            "SELECT id, website, username, encrypted_password FROM passwords WHERE website LIKE ? OR username LIKE ?",
            (f'%{search_query}%', f'%{search_query}%')
        )
    else:
        cursor.execute("SELECT id, website, username, encrypted_password FROM passwords ORDER BY id DESC")

    rows = cursor.fetchall()
    conn.close()

    # Decrypt each password before sending to template
    credentials = []
    for row in rows:
        cred_id, website, username, enc_pass = row
        try:
            plain_pass = decrypt_password(enc_pass)
        except Exception:
            plain_pass = "[Decryption Error]"
        credentials.append({
            'id': cred_id,
            'website': website,
            'username': username,
            'password': plain_pass
        })

    return render_template('vault.html', credentials=credentials, search_query=search_query)

# Route: Add New Password

@app.route('/add', methods=['GET', 'POST'])
def add_password():
    """
    Handles adding a new credential.
    GET: Shows the add password form.
    POST: Encrypts the password and saves to database.
    Requires authentication.
    """
    if not is_logged_in():
        flash('Please log in to access the vault.', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        website = request.form.get('website', '').strip()
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        # Validate all fields are filled
        if not website or not username or not password:
            flash('All fields are required. Please fill in every field.', 'error')
            return redirect(url_for('add_password'))

        # Encrypt the password before saving
        encrypted = encrypt_password(password)

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO passwords (website, username, encrypted_password) VALUES (?, ?, ?)",
            (website, username, encrypted)
        )
        conn.commit()
        conn.close()

        flash(f'Password for "{website}" saved securely!', 'success')
        return redirect(url_for('vault'))

    return render_template('add_password.html')

# Route: Update Existing Password

@app.route('/update/<int:cred_id>', methods=['GET', 'POST'])
def update_password(cred_id):
    """
    Handles updating an existing credential.
    GET: Pre-fills the form with decrypted current data.
    POST: Re-encrypts the new password and updates the database.
    Requires authentication.
    """
    if not is_logged_in():
        flash('Please log in to access the vault.', 'error')
        return redirect(url_for('login'))

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    if request.method == 'POST':
        website = request.form.get('website', '').strip()
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if not website or not username or not password:
            flash('All fields are required.', 'error')
            return redirect(url_for('update_password', cred_id=cred_id))

        # Encrypt the updated password
        encrypted = encrypt_password(password)

        cursor.execute(
            "UPDATE passwords SET website=?, username=?, encrypted_password=? WHERE id=?",
            (website, username, encrypted, cred_id)
        )
        conn.commit()
        conn.close()

        flash(f'Credential updated successfully!', 'success')
        return redirect(url_for('vault'))

    # GET — load existing credential to pre-fill form
    cursor.execute("SELECT id, website, username, encrypted_password FROM passwords WHERE id=?", (cred_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        flash('Credential not found.', 'error')
        return redirect(url_for('vault'))

    credential = {
        'id': row[0],
        'website': row[1],
        'username': row[2],
        'password': decrypt_password(row[3])
    }

    return render_template('update_password.html', credential=credential)

# Route: Delete Credential


@app.route('/delete/<int:cred_id>', methods=['POST'])
def delete_password(cred_id):
    """
    Deletes a credential from the database by its ID.
    Only accepts POST requests (form submission) for security.
    Requires authentication.
    """
    if not is_logged_in():
        flash('Please log in to access the vault.', 'error')
        return redirect(url_for('login'))

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM passwords WHERE id=?", (cred_id,))
    conn.commit()
    conn.close()

    flash('Credential deleted successfully.', 'success')
    return redirect(url_for('vault'))

# Route: Copy Password (API endpoint)

@app.route('/get_password/<int:cred_id>')
def get_password(cred_id):
    """
    Returns the decrypted password as JSON for clipboard copy via JavaScript.
    Only accessible when logged in.
    """
    if not is_logged_in():
        return jsonify({'error': 'Unauthorized'}), 401

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT encrypted_password FROM passwords WHERE id=?", (cred_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return jsonify({'error': 'Not found'}), 404

    plain = decrypt_password(row[0])
    return jsonify({'password': plain})

# App Entry Point

if __name__ == '__main__':
    # Initialize the database before starting the server
    init_db()
    print("=" * 50)
    print(" Password Manager is running!")
    print(" Open: http://127.0.0.1:5000")
    print("=" * 50)
    app.run(debug=True)

# Master Password is : Mypassword@1234