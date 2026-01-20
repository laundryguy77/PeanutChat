import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import JWTError, jwt
import bcrypt

from app.config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRE_MINUTES
from app.services.database import get_database
from app.models.auth_schemas import UserCreate, UserResponse, UserSettings

logger = logging.getLogger(__name__)


class AuthService:
    """Service for authentication operations"""

    def __init__(self):
        self.db = get_database()

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )

    def hash_password(self, password: str) -> str:
        """Hash a password"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    def create_access_token(self, user_id: int, username: str) -> str:
        """Create a JWT access token"""
        expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)
        to_encode = {
            "sub": str(user_id),
            "username": username,
            "exp": expire
        }
        encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return encoded_jwt

    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Decode and validate a JWT token"""
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return payload
        except JWTError as e:
            logger.debug(f"Token decode error: {e}")
            return None

    def create_user(self, user_data: UserCreate) -> Optional[UserResponse]:
        """Create a new user"""
        # Check if username exists
        existing = self.db.fetchone(
            "SELECT id FROM users WHERE username = ?",
            (user_data.username,)
        )
        if existing:
            logger.warning(f"Username already exists: {user_data.username}")
            return None

        # Check if email exists (if provided)
        if user_data.email:
            existing_email = self.db.fetchone(
                "SELECT id FROM users WHERE email = ?",
                (user_data.email,)
            )
            if existing_email:
                logger.warning(f"Email already exists: {user_data.email}")
                return None

        # Hash password and create user
        password_hash = self.hash_password(user_data.password)
        created_at = datetime.now(timezone.utc).isoformat()

        cursor = self.db.execute(
            """INSERT INTO users (username, password_hash, email, created_at)
               VALUES (?, ?, ?, ?)""",
            (user_data.username, password_hash, user_data.email, created_at)
        )
        user_id = cursor.lastrowid

        # Create default user settings
        self.db.execute(
            "INSERT INTO user_settings (user_id) VALUES (?)",
            (user_id,)
        )

        logger.info(f"Created new user: {user_data.username} (id={user_id})")

        return UserResponse(
            id=user_id,
            username=user_data.username,
            email=user_data.email,
            created_at=created_at
        )

    def authenticate_user(self, username: str, password: str) -> Optional[UserResponse]:
        """Authenticate a user by username and password"""
        user = self.db.fetchone(
            "SELECT id, username, password_hash, email, created_at FROM users WHERE username = ?",
            (username,)
        )
        if not user:
            logger.debug(f"User not found: {username}")
            return None

        if not self.verify_password(password, user["password_hash"]):
            logger.debug(f"Invalid password for user: {username}")
            return None

        return UserResponse(
            id=user["id"],
            username=user["username"],
            email=user["email"],
            created_at=user["created_at"]
        )

    def get_user_by_id(self, user_id: int) -> Optional[UserResponse]:
        """Get user by ID"""
        user = self.db.fetchone(
            "SELECT id, username, email, created_at FROM users WHERE id = ?",
            (user_id,)
        )
        if not user:
            return None

        return UserResponse(
            id=user["id"],
            username=user["username"],
            email=user["email"],
            created_at=user["created_at"]
        )

    def change_password(self, user_id: int, current_password: str, new_password: str) -> bool:
        """Change user's password"""
        user = self.db.fetchone(
            "SELECT password_hash FROM users WHERE id = ?",
            (user_id,)
        )
        if not user:
            return False

        if not self.verify_password(current_password, user["password_hash"]):
            return False

        new_hash = self.hash_password(new_password)
        self.db.execute(
            "UPDATE users SET password_hash = ? WHERE id = ?",
            (new_hash, user_id)
        )
        logger.info(f"Password changed for user {user_id}")
        return True

    def get_user_settings(self, user_id: int) -> Optional[UserSettings]:
        """Get user-specific settings"""
        settings = self.db.fetchone(
            """SELECT model, temperature, top_p, top_k, num_ctx, repeat_penalty, persona
               FROM user_settings WHERE user_id = ?""",
            (user_id,)
        )
        if not settings:
            return None

        return UserSettings(
            model=settings["model"],
            temperature=settings["temperature"],
            top_p=settings["top_p"],
            top_k=settings["top_k"],
            num_ctx=settings["num_ctx"],
            repeat_penalty=settings["repeat_penalty"],
            persona=settings["persona"]
        )

    def update_user_settings(self, user_id: int, settings: UserSettings) -> bool:
        """Update user-specific settings"""
        # Build dynamic update query for non-None values
        updates = []
        values = []

        for field, value in settings.model_dump().items():
            if value is not None:
                updates.append(f"{field} = ?")
                values.append(value)

        if not updates:
            return True

        values.append(user_id)
        query = f"UPDATE user_settings SET {', '.join(updates)} WHERE user_id = ?"

        self.db.execute(query, tuple(values))
        return True

    def delete_user(self, user_id: int) -> bool:
        """Delete a user and all their data"""
        self.db.execute("DELETE FROM users WHERE id = ?", (user_id,))
        logger.info(f"Deleted user {user_id}")
        return True


# Global service instance (initialized lazily)
_auth_service: Optional[AuthService] = None


def get_auth_service() -> AuthService:
    """Get the global auth service instance"""
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService()
    return _auth_service
