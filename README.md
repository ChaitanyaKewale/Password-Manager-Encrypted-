# SecureVault – Encrypted Password Manager

Developer:
Chaitanya Kewale
INTERN ID - CITS1513

SecureVault is a web-based password management system developed using Python and Flask.
The application allows users to securely store, manage, update, and retrieve credentials using encryption techniques.

The project focuses on secure password handling, clean user interface design, and CRUD operations with database integration.

---

# Project Features

* Secure password storage using encryption
* Add new credentials
* Update existing credentials
* Delete saved credentials
* Search functionality for websites and usernames
* Show and hide password option
* Copy username and password functionality
* Responsive and user-friendly interface
* Master password authentication

---

# Technologies Used

Backend:

* Python
* Flask
* SQLite

Frontend:

* HTML
* CSS
* JavaScript

Libraries:

* Cryptography (Fernet Encryption)
* Bootstrap Icons

---

# Project Structure

```bash
Password-Manager-Encrypted-
│
├── app.py
├── database.db
├── requirements.txt
├── key.key
│
├── templates/
│   ├── base.html
│   ├── vault.html
│   ├── login.html
│   ├── add_password.html
│   └── update_password.html
│
├── static/
│   ├── style.css
│   └── script.js
│
└── README.md
```

---

# Installation Steps

## Clone the Repository

```bash
git clone https://github.com/ChaitanyaKewale/Password-Manager-Encrypted-.git
```

## Navigate to Project Directory

```bash
cd Password-Manager-Encrypted-
```

## Install Required Dependencies

```bash
pip install -r requirements.txt
```

## Run the Application

```bash
python app.py
```

---

# Access the Application

Open the following URL in the browser:

```bash
http://127.0.0.1:5000
```

---

# Encryption Mechanism

This project uses Fernet Encryption from Python’s Cryptography library to secure user passwords.

* Passwords are encrypted before being stored in the database
* Passwords are decrypted only when required
* Encryption keys are managed locally using a key file

---

# Learning Outcomes

This project helped in understanding:

* Flask web development
* Database integration using SQLite
* CRUD operations
* Encryption and secure data handling
* Frontend and backend integration
* User authentication concepts

---

# Future Enhancements

* Password generator
* Two-factor authentication
* Dark mode support
* Cloud database integration
* Password strength checker
* Export and import functionality

---

# License

This project is developed for educational and internship purposes.
