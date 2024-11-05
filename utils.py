# utils.py

import sqlite3
from cryptography.fernet import Fernet
import bcrypt
import os

# Generate or load an encryption key
def load_key():
    if not os.path.exists("secret.key"):
        key = Fernet.generate_key()
        with open("secret.key", "wb") as key_file:
            key_file.write(key)
    else:
        with open("secret.key", "rb") as key_file:
            key = key_file.read()
    return key

# Encryption and decryption functions
def encrypt_data(data, key):
    cipher = Fernet(key)
    encrypted_data = cipher.encrypt(data.encode())
    return encrypted_data

def decrypt_data(encrypted_data, key):
    cipher = Fernet(key)
    decrypted_data = cipher.decrypt(encrypted_data).decode()
    return decrypted_data

# Database setup functions
def init_db():
    conn = sqlite3.connect("vault.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS credentials (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        name TEXT NOT NULL,
        username TEXT,
        password TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)
    conn.commit()
    conn.close()

def create_user(email, password):
    conn = sqlite3.connect("vault.db")
    cursor = conn.cursor()
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    try:
        cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, hashed_password))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return False  # Email already exists
    conn.close()
    return True

def authenticate_user(email, password):
    conn = sqlite3.connect("vault.db")
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    if user and bcrypt.checkpw(password.encode(), user[0]):
        return True
    return False

def add_credential(user_id, name, username, password, key):
    conn = sqlite3.connect("vault.db")
    cursor = conn.cursor()
    encrypted_password = encrypt_data(password, key)
    cursor.execute("INSERT INTO credentials (user_id, name, username, password) VALUES (?, ?, ?, ?)",
                   (user_id, name, username, encrypted_password))
    conn.commit()
    conn.close()

def get_credentials(user_id, key):
    conn = sqlite3.connect("vault.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, username, password FROM credentials WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    credentials = [(row[0], row[1], row[2], decrypt_data(row[3], key)) for row in rows]
    return credentials

# New function to get a specific credential's details and decrypt password
def get_decrypted_credential(cred_id, key):
    conn = sqlite3.connect("vault.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, username, password FROM credentials WHERE id = ?", (cred_id,))
    result = cursor.fetchone()
    conn.close()

    if result:
        name, username, encrypted_password = result
        password = decrypt_data(encrypted_password, key)
        return name, username, password
    return None
