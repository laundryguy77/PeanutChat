#!/usr/bin/env python3
"""
Create an admin user for PeanutChat.

Usage:
    python scripts/create_admin.py <username> <password>

Or interactively:
    python scripts/create_admin.py
"""

import sys
import getpass
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import bcrypt
from app.services.database import get_database


def create_admin(username: str, password: str) -> bool:
    """Create an admin user."""
    db = get_database()

    # Check if username exists
    existing = db.fetchone(
        "SELECT id FROM users WHERE username = ?",
        (username,)
    )
    if existing:
        print(f"Error: Username '{username}' already exists")
        return False

    # Hash password
    password_hash = bcrypt.hashpw(
        password.encode('utf-8'),
        bcrypt.gensalt()
    ).decode('utf-8')

    # Create user with admin flag
    from datetime import datetime
    now = datetime.utcnow().isoformat() + "Z"

    db.execute(
        """INSERT INTO users (username, password_hash, is_admin, is_active, created_at)
           VALUES (?, ?, 1, 1, ?)""",
        (username, password_hash, now)
    )

    # Get new user ID
    row = db.fetchone("SELECT last_insert_rowid()")
    user_id = row[0]

    print(f"Admin user '{username}' created successfully (ID: {user_id})")
    return True


def promote_to_admin(username: str) -> bool:
    """Promote an existing user to admin."""
    db = get_database()

    row = db.fetchone(
        "SELECT id, is_admin FROM users WHERE username = ?",
        (username,)
    )

    if not row:
        print(f"Error: User '{username}' not found")
        return False

    if row[1]:
        print(f"User '{username}' is already an admin")
        return True

    db.execute(
        "UPDATE users SET is_admin = 1 WHERE id = ?",
        (row[0],)
    )

    print(f"User '{username}' promoted to admin")
    return True


def main():
    print("PeanutChat Admin User Creation")
    print("=" * 40)

    if len(sys.argv) == 3:
        username = sys.argv[1]
        password = sys.argv[2]
    elif len(sys.argv) == 2 and sys.argv[1] == "--promote":
        username = input("Username to promote: ").strip()
        if not username:
            print("Username cannot be empty")
            sys.exit(1)
        success = promote_to_admin(username)
        sys.exit(0 if success else 1)
    else:
        print("\nOptions:")
        print("  1. Create new admin user")
        print("  2. Promote existing user to admin")
        choice = input("\nChoice (1/2): ").strip()

        if choice == "2":
            username = input("Username to promote: ").strip()
            if not username:
                print("Username cannot be empty")
                sys.exit(1)
            success = promote_to_admin(username)
            sys.exit(0 if success else 1)

        # Create new user
        username = input("Admin username: ").strip()
        if not username:
            print("Username cannot be empty")
            sys.exit(1)

        if len(username) < 3:
            print("Username must be at least 3 characters")
            sys.exit(1)

        password = getpass.getpass("Admin password: ")
        if len(password) < 8:
            print("Password must be at least 8 characters")
            sys.exit(1)

        confirm = getpass.getpass("Confirm password: ")
        if password != confirm:
            print("Passwords do not match")
            sys.exit(1)

    success = create_admin(username, password)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
