from passlib.hash import pbkdf2_sha256

# Simple in-memory users for demo: passwords are hashed
USERS = {
    "alice": {"pw": pbkdf2_sha256.hash("alicepass"), "role":"admin"},
    "bob":   {"pw": pbkdf2_sha256.hash("bobpass"),   "role":"user"},
    "aud":   {"pw": pbkdf2_sha256.hash("audpass"),   "role":"auditor"},
}

def verify(username, password):
    if username not in USERS: return False
    return pbkdf2_sha256.verify(password, USERS[username]["pw"])

def role_of(username):
    return USERS.get(username, {}).get("role", "user")
