# PeanutChat Admin Portal Build Plan

## Document Information
- **Feature:** Admin Portal
- **Version:** 2.0 (Implementation Ready)
- **Last Updated:** 2026-01-25
- **Status:** Ready for Implementation

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-23 | Initial draft |
| 1.1 | 2026-01-25 | Audit corrections applied |
| 2.0 | 2026-01-25 | All fixes implemented, ready for coding |

---

## Critical Corrections Applied

| Issue | Original | Corrected |
|-------|----------|-----------|
| Database access | `get_database()` | `get_database()` (DatabaseService) |
| Auth import | `from app.routers.auth` | `from app.middleware.auth` |
| AuthService methods | `async` | Methods are `sync`, not async |
| AuthService.create_user | `(username, password) -> int` | `(UserCreate) -> UserResponse` |
| Stats Service | Queries `conversations` table | **Scan JSON files in conversations directory** |
| Stats Service | Queries `messages` table | **Count from conversation JSON files** |
| Migration number | 003/011 | **012** (voice uses 011) |
| Tool names | `browse_url`, `generate_image` | `browse_website`, `image` |
| Frontend auth | `localStorage` tokens | httpOnly cookies with `credentials: 'include'` |
| user_profiles table | `data` column | `profile_data` column |
| user_profiles PK | `id` with `user_id` FK | `user_id` IS the PK |
| Conversation deletion | DELETE from DB | **Delete JSON files from conversations/{user_id}/** |

## Additions in v2.0

1. **Modal functions implemented** - `showCreateUserModal()`, `editUser()`, etc. now included
2. **Public themes endpoint** - Added `/api/themes` for users
3. **User features endpoint** - Added `/api/user/features` for own flags
4. **Date range filter** - Added to audit log endpoint
5. **JSON file-based conversation handling** - Stats and deletion now use filesystem

---

## Executive Summary

This document provides a complete implementation guide for adding an Admin Portal to PeanutChat with:
- **User Management:** Create, edit, delete users; reset passwords; toggle active status
- **Mode Restrictions:** Lock users to specific content modes
- **Feature Toggles:** Enable/disable tools, memory, TTS, etc. per-user or globally
- **Theme Management:** Create, edit, delete UI themes with live preview
- **System Dashboard:** Stats, logs, MCP server overview

---

## Table of Contents

1. [Current System Analysis](#1-current-system-analysis)
2. [Phase 2.1: Admin Foundation](#2-phase-21-admin-foundation)
3. [Phase 2.2: Feature & Mode Control](#3-phase-22-feature--mode-control)
4. [Phase 2.3: Theme Management & Dashboard](#4-phase-23-theme-management--dashboard)
5. [Database Schema](#5-database-schema)
6. [API Reference](#6-api-reference)
7. [Security Considerations](#7-security-considerations)
8. [Testing Requirements](#8-testing-requirements)

---

## 1. Current System Analysis

### 1.1 Existing Authentication System

**File:** `app/services/auth_service.py`

```python
class AuthService:
    """Handles user authentication with bcrypt password hashing."""

    async def create_user(self, username: str, password: str) -> Optional[int]:
        """Creates user with bcrypt-hashed password."""

    async def authenticate(self, username: str, password: str) -> Optional[Dict]:
        """Verifies credentials, returns user dict with id, username."""

    async def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Returns user dict by ID."""
```

**File:** `app/routers/auth.py`

Current endpoints:
- `POST /api/auth/register` - Create new user
- `POST /api/auth/login` - Authenticate and get JWT
- `GET /api/auth/me` - Get current user info
- `POST /api/auth/change-password` - Change own password

**JWT Structure (current):**
```python
{
    "sub": user_id,      # int
    "username": "...",   # str
    "exp": timestamp     # expiration
}
```

### 1.2 Existing User Database Schema

**File:** `app/services/database.py` (lines 45-52)

```sql
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
)
```

**Current Columns:**
| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER | Primary key, auto-increment |
| username | TEXT | Unique, required |
| password_hash | TEXT | bcrypt hash |
| created_at | TIMESTAMP | Auto-set on creation |
| last_login | TIMESTAMP | Updated on login |

### 1.3 Existing Mode System

**File:** `app/services/user_profile_service.py`

Three-tier mode system:
1. **Normal Mode** - Default, SFW content only
2. **Uncensored Mode (Tier 1)** - Requires passcode, persists to DB
3. **Full Unlock Mode (Tier 2)** - Requires `/full_unlock` command, session-only

**Key Methods:**
```python
async def enable_adult_mode(self, user_id: int, passcode: str) -> Dict
async def disable_adult_mode(self, user_id: int) -> Dict
async def full_unlock(self, user_id: int, session_id: str) -> Dict
async def check_full_unlock(self, user_id: int, session_id: str) -> bool
```

### 1.4 Existing Tool System

**File:** `app/tools/definitions.py`

Tools are defined as JSON schemas and conditionally included based on:
- Model capabilities (tool support)
- User preferences (from profile)

**Current Tools:**
| Tool | Category | Description |
|------|----------|-------------|
| `web_search` | Web | Brave Search API |
| `browse_url` | Web | Fetch and parse URLs |
| `add_memory` | Memory | Store user information |
| `query_memories` | Memory | Search stored memories |
| `search_knowledge` | Knowledge | Query knowledge base |
| `add_to_knowledge` | Knowledge | Add to knowledge base |
| `generate_image` | Media | Image generation |
| `generate_video` | Media | Video generation |

### 1.5 Existing Theme System

**File:** `static/js/settings.js` (lines 380-450)

Current themes are hardcoded in JavaScript:
```javascript
const THEMES = {
    'default': { name: 'Default Dark', colors: {...} },
    'midnight': { name: 'Midnight Blue', colors: {...} },
    'forest': { name: 'Forest Green', colors: {...} },
    // ... more themes
};
```

**Theme Storage:**
- Current theme preference stored in user profile (`theme` field)
- CSS variables applied via JavaScript on load

### 1.6 Existing Settings System

**File:** `app/services/user_profile_store.py`

User settings stored in `user_profiles` table:
```sql
CREATE TABLE IF NOT EXISTS user_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL,
    data TEXT NOT NULL,  -- JSON blob
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)
```

**Profile Data Structure:**
```json
{
  "persona_preferences": {
    "selected_persona": "default",
    "adult_mode_enabled": false
  },
  "settings": {
    "theme": "default",
    "thinking_enabled": true,
    "auto_memories": true,
    "model_name": "qwen3:14b"
  }
}
```

---

## 2. Phase 2.1: Admin Foundation

### 2.1.1 Database Migrations

**New File:** `app/services/migrations/012_admin_features.py`

```python
"""
Migration 012: Admin Features

Adds admin capabilities to users table and creates feature_flags table.

NOTE: Migration 011 is used by Voice features (TTS/STT).
"""

import sqlite3
import logging

logger = logging.getLogger(__name__)

MIGRATION_SQL = """
-- Add admin columns to users table
ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT 0;
ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT 1;
ALTER TABLE users ADD COLUMN mode_restriction TEXT DEFAULT NULL;
ALTER TABLE users ADD COLUMN feature_overrides TEXT DEFAULT NULL;

-- Create feature_flags table for global settings
CREATE TABLE IF NOT EXISTS feature_flags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    feature_key TEXT UNIQUE NOT NULL,
    display_name TEXT NOT NULL,
    description TEXT,
    default_enabled BOOLEAN DEFAULT 1,
    category TEXT DEFAULT 'general',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create user_feature_overrides table for per-user settings
CREATE TABLE IF NOT EXISTS user_feature_overrides (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    feature_key TEXT NOT NULL,
    enabled BOOLEAN NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id),
    UNIQUE(user_id, feature_key)
);

-- Create admin_audit_log table
CREATE TABLE IF NOT EXISTS admin_audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    admin_id INTEGER NOT NULL,
    action TEXT NOT NULL,
    target_type TEXT NOT NULL,
    target_id TEXT,
    details TEXT,
    ip_address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (admin_id) REFERENCES users(id)
);

-- Insert default feature flags
INSERT OR IGNORE INTO feature_flags (feature_key, display_name, description, category, default_enabled) VALUES
    ('tool_use', 'Tool Use', 'Allow model to use tools (web search, image gen, etc.)', 'tools', 1),
    ('web_search', 'Web Search', 'Allow web search tool', 'tools', 1),
    ('browse_url', 'URL Browsing', 'Allow URL fetching tool', 'tools', 1),
    ('image_generation', 'Image Generation', 'Allow image generation tool', 'tools', 1),
    ('video_generation', 'Video Generation', 'Allow video generation tool', 'tools', 1),
    ('memory_system', 'Memory System', 'Enable persistent memory', 'memory', 1),
    ('auto_memories', 'Auto Memory Extraction', 'Automatically extract memories from responses', 'memory', 1),
    ('knowledge_base', 'Knowledge Base', 'Enable knowledge base queries', 'memory', 1),
    ('tts', 'Text-to-Speech', 'Enable TTS for responses', 'voice', 0),
    ('stt', 'Speech-to-Text', 'Enable voice input', 'voice', 0),
    ('thinking_mode', 'Thinking Mode', 'Show model reasoning process', 'display', 1),
    ('mcp_tools', 'MCP Tools', 'Enable MCP server tools', 'tools', 1);
"""

def run_migration(db_path: str) -> bool:
    """Execute migration."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if migration already applied
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]

        if 'is_admin' in columns:
            logger.info("Migration 012 already applied")
            return True

        # Execute migration in transaction
        for statement in MIGRATION_SQL.split(';'):
            statement = statement.strip()
            if statement:
                try:
                    cursor.execute(statement)
                except sqlite3.OperationalError as e:
                    # Handle "duplicate column" errors gracefully
                    if "duplicate column" not in str(e).lower():
                        raise

        db.commit()
        logger.info("Migration 012 completed successfully")
        return True

    except Exception as e:
        logger.error(f"Migration 012 failed: {e}")
        db.rollback()
        return False
    finally:
        conn.close()
```

### 2.1.2 Admin Service

**New File:** `app/services/admin_service.py`

```python
"""
Admin Service - Business logic for admin operations.

Handles user management, feature flags, and audit logging.
"""

import logging
import json
from typing import Optional, Dict, List, Any
from datetime import datetime

from app.services.database import get_database
from app.services.auth_service import AuthService

logger = logging.getLogger(__name__)


class AdminService:
    """Business logic for admin operations."""

    def __init__(self):
        self.auth_service = AuthService()

    # =========================================================================
    # User Management
    # =========================================================================

    async def list_users(
        self,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        include_inactive: bool = False
    ) -> Dict[str, Any]:
        """
        List all users with pagination and optional search.

        Args:
            page: Page number (1-indexed)
            page_size: Items per page (max 100)
            search: Optional username search filter
            include_inactive: Include deactivated users

        Returns:
            {
                "users": [...],
                "total": int,
                "page": int,
                "page_size": int,
                "total_pages": int
            }
        """
        page_size = min(page_size, 100)
        offset = (page - 1) * page_size

        db = get_database()
        try:
            cursor = conn.cursor()

            # Build query
            where_clauses = []
            params = []

            if not include_inactive:
                where_clauses.append("is_active = 1")

            if search:
                where_clauses.append("username LIKE ?")
                params.append(f"%{search}%")

            where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

            # Get total count
            cursor.execute(f"SELECT COUNT(*) FROM users {where_sql}", params)
            total = cursor.fetchone()[0]

            # Get users
            cursor.execute(f"""
                SELECT id, username, is_admin, is_active, mode_restriction,
                       feature_overrides, created_at, last_login
                FROM users
                {where_sql}
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """, params + [page_size, offset])

            users = []
            for row in cursor.fetchall():
                users.append({
                    "id": row[0],
                    "username": row[1],
                    "is_admin": bool(row[2]),
                    "is_active": bool(row[3]),
                    "mode_restriction": row[4],
                    "feature_overrides": json.loads(row[5]) if row[5] else {},
                    "created_at": row[6],
                    "last_login": row[7]
                })

            return {
                "users": users,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size
            }

        finally:
            conn.close()

    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed user information."""
        db = get_database()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT u.id, u.username, u.is_admin, u.is_active,
                       u.mode_restriction, u.feature_overrides,
                       u.created_at, u.last_login,
                       p.data as profile_data
                FROM users u
                LEFT JOIN user_profiles p ON u.id = p.user_id
                WHERE u.id = ?
            """, (user_id,))

            row = cursor.fetchone()
            if not row:
                return None

            return {
                "id": row[0],
                "username": row[1],
                "is_admin": bool(row[2]),
                "is_active": bool(row[3]),
                "mode_restriction": row[4],
                "feature_overrides": json.loads(row[5]) if row[5] else {},
                "created_at": row[6],
                "last_login": row[7],
                "profile": json.loads(row[8]) if row[8] else {}
            }
        finally:
            conn.close()

    async def update_user(
        self,
        user_id: int,
        admin_id: int,
        updates: Dict[str, Any],
        ip_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update user attributes.

        Allowed updates:
        - is_active: bool
        - is_admin: bool
        - mode_restriction: str | None ("normal_only", "no_full_unlock", None)
        - feature_overrides: dict
        """
        allowed_fields = {"is_active", "is_admin", "mode_restriction", "feature_overrides"}

        # Filter to allowed fields
        filtered_updates = {k: v for k, v in updates.items() if k in allowed_fields}

        if not filtered_updates:
            return {"success": False, "error": "No valid fields to update"}

        # Prevent admin from demoting themselves
        if user_id == admin_id and "is_admin" in filtered_updates:
            if not filtered_updates["is_admin"]:
                return {"success": False, "error": "Cannot remove your own admin status"}

        db = get_database()
        try:
            cursor = conn.cursor()

            # Build update query
            set_clauses = []
            params = []

            for field, value in filtered_updates.items():
                if field == "feature_overrides":
                    set_clauses.append(f"{field} = ?")
                    params.append(json.dumps(value))
                else:
                    set_clauses.append(f"{field} = ?")
                    params.append(value)

            params.append(user_id)

            cursor.execute(f"""
                UPDATE users SET {', '.join(set_clauses)}
                WHERE id = ?
            """, params)

            db.commit()

            # Audit log
            await self._audit_log(
                admin_id=admin_id,
                action="update_user",
                target_type="user",
                target_id=str(user_id),
                details=json.dumps(filtered_updates),
                ip_address=ip_address
            )

            return {"success": True}

        except Exception as e:
            logger.error(f"Failed to update user {user_id}: {e}")
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    async def create_user(
        self,
        admin_id: int,
        username: str,
        password: str,
        is_admin: bool = False,
        ip_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new user (admin-only)."""
        # Use existing auth service for password hashing
        user_id = await self.auth_service.create_user(username, password)

        if not user_id:
            return {"success": False, "error": "Username already exists"}

        # Set admin status if requested
        if is_admin:
            db = get_database()
            try:
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET is_admin = 1 WHERE id = ?", (user_id,))
                db.commit()
            finally:
                conn.close()

        # Audit log
        await self._audit_log(
            admin_id=admin_id,
            action="create_user",
            target_type="user",
            target_id=str(user_id),
            details=json.dumps({"username": username, "is_admin": is_admin}),
            ip_address=ip_address
        )

        return {"success": True, "user_id": user_id}

    async def delete_user(
        self,
        user_id: int,
        admin_id: int,
        ip_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Delete a user and all their data.

        WARNING: This is destructive and removes:
        - User account
        - User profile
        - All conversations (JSON files)
        - All memories
        - Knowledge base entries
        """
        import shutil
        from pathlib import Path
        from app import config

        # Prevent self-deletion
        if user_id == admin_id:
            return {"success": False, "error": "Cannot delete your own account"}

        db = get_database()
        try:
            # Get username for audit log
            row = db.execute(
                "SELECT username FROM users WHERE id = ?", (user_id,)
            ).fetchone()
            if not row:
                return {"success": False, "error": "User not found"}

            username = row[0]

            # Delete database records
            db.execute("DELETE FROM memories WHERE user_id = ?", (user_id,))
            db.execute("DELETE FROM knowledge WHERE user_id = ?", (user_id,))
            db.execute("DELETE FROM user_profiles WHERE user_id = ?", (user_id,))
            db.execute("DELETE FROM user_feature_overrides WHERE user_id = ?", (user_id,))
            db.execute("DELETE FROM users WHERE id = ?", (user_id,))
            db.commit()

            # Delete conversation JSON files
            # Conversations are stored in: conversations/{user_id}/
            conv_dir = Path(config.CONVERSATIONS_DIR) / str(user_id)
            if conv_dir.exists():
                shutil.rmtree(conv_dir)
                logger.info(f"Deleted conversation directory: {conv_dir}")

            # Audit log
            await self._audit_log(
                admin_id=admin_id,
                action="delete_user",
                target_type="user",
                target_id=str(user_id),
                details=json.dumps({"username": username}),
                ip_address=ip_address
            )

            return {"success": True}

        except Exception as e:
            logger.error(f"Failed to delete user {user_id}: {e}")
            return {"success": False, "error": str(e)}

    async def reset_password(
        self,
        user_id: int,
        admin_id: int,
        new_password: str,
        ip_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """Reset a user's password (admin-only)."""
        import bcrypt

        password_hash = bcrypt.hashpw(
            new_password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')

        db = get_database()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET password_hash = ? WHERE id = ?",
                (password_hash, user_id)
            )
            db.commit()

            # Audit log
            await self._audit_log(
                admin_id=admin_id,
                action="reset_password",
                target_type="user",
                target_id=str(user_id),
                details=None,  # Don't log password
                ip_address=ip_address
            )

            return {"success": True}

        except Exception as e:
            logger.error(f"Failed to reset password for user {user_id}: {e}")
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    # =========================================================================
    # Feature Flags
    # =========================================================================

    async def list_feature_flags(self) -> List[Dict[str, Any]]:
        """Get all feature flags with their default values."""
        db = get_database()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT feature_key, display_name, description,
                       default_enabled, category
                FROM feature_flags
                ORDER BY category, display_name
            """)

            return [
                {
                    "key": row[0],
                    "display_name": row[1],
                    "description": row[2],
                    "default_enabled": bool(row[3]),
                    "category": row[4]
                }
                for row in cursor.fetchall()
            ]
        finally:
            conn.close()

    async def update_feature_flag(
        self,
        admin_id: int,
        feature_key: str,
        default_enabled: bool,
        ip_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update a global feature flag default."""
        db = get_database()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE feature_flags
                SET default_enabled = ?, updated_at = CURRENT_TIMESTAMP
                WHERE feature_key = ?
            """, (default_enabled, feature_key))

            if cursor.rowcount == 0:
                return {"success": False, "error": "Feature flag not found"}

            db.commit()

            # Audit log
            await self._audit_log(
                admin_id=admin_id,
                action="update_feature_flag",
                target_type="feature_flag",
                target_id=feature_key,
                details=json.dumps({"default_enabled": default_enabled}),
                ip_address=ip_address
            )

            return {"success": True}

        finally:
            conn.close()

    async def get_user_features(self, user_id: int) -> Dict[str, bool]:
        """
        Get effective feature flags for a user.

        Returns dict of feature_key -> enabled (considering global defaults + user overrides)
        """
        db = get_database()
        try:
            cursor = conn.cursor()

            # Get global defaults
            cursor.execute("""
                SELECT feature_key, default_enabled FROM feature_flags
            """)
            features = {row[0]: bool(row[1]) for row in cursor.fetchall()}

            # Apply user overrides
            cursor.execute("""
                SELECT feature_key, enabled FROM user_feature_overrides
                WHERE user_id = ?
            """, (user_id,))

            for row in cursor.fetchall():
                features[row[0]] = bool(row[1])

            return features

        finally:
            conn.close()

    async def set_user_feature_override(
        self,
        admin_id: int,
        user_id: int,
        feature_key: str,
        enabled: Optional[bool],
        ip_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Set a per-user feature override.

        Args:
            enabled: True/False to override, None to remove override (use global default)
        """
        db = get_database()
        try:
            cursor = conn.cursor()

            if enabled is None:
                # Remove override
                cursor.execute("""
                    DELETE FROM user_feature_overrides
                    WHERE user_id = ? AND feature_key = ?
                """, (user_id, feature_key))
            else:
                # Upsert override
                cursor.execute("""
                    INSERT INTO user_feature_overrides (user_id, feature_key, enabled, created_by)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(user_id, feature_key) DO UPDATE SET
                        enabled = excluded.enabled,
                        created_by = excluded.created_by
                """, (user_id, feature_key, enabled, admin_id))

            db.commit()

            # Audit log
            await self._audit_log(
                admin_id=admin_id,
                action="set_user_feature",
                target_type="user_feature",
                target_id=f"{user_id}:{feature_key}",
                details=json.dumps({"enabled": enabled}),
                ip_address=ip_address
            )

            return {"success": True}

        finally:
            conn.close()

    # =========================================================================
    # Audit Logging
    # =========================================================================

    async def _audit_log(
        self,
        admin_id: int,
        action: str,
        target_type: str,
        target_id: Optional[str],
        details: Optional[str],
        ip_address: Optional[str]
    ):
        """Record admin action in audit log."""
        db = get_database()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO admin_audit_log
                (admin_id, action, target_type, target_id, details, ip_address)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (admin_id, action, target_type, target_id, details, ip_address))
            db.commit()
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")
        finally:
            conn.close()

    async def get_audit_log(
        self,
        page: int = 1,
        page_size: int = 50,
        admin_id: Optional[int] = None,
        action: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get admin audit log with pagination."""
        page_size = min(page_size, 100)
        offset = (page - 1) * page_size

        db = get_database()
        try:
            cursor = conn.cursor()

            where_clauses = []
            params = []

            if admin_id:
                where_clauses.append("a.admin_id = ?")
                params.append(admin_id)

            if action:
                where_clauses.append("a.action = ?")
                params.append(action)

            where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

            # Get total
            cursor.execute(f"SELECT COUNT(*) FROM admin_audit_log a {where_sql}", params)
            total = cursor.fetchone()[0]

            # Get entries
            cursor.execute(f"""
                SELECT a.id, a.admin_id, u.username, a.action,
                       a.target_type, a.target_id, a.details,
                       a.ip_address, a.created_at
                FROM admin_audit_log a
                JOIN users u ON a.admin_id = u.id
                {where_sql}
                ORDER BY a.created_at DESC
                LIMIT ? OFFSET ?
            """, params + [page_size, offset])

            entries = []
            for row in cursor.fetchall():
                entries.append({
                    "id": row[0],
                    "admin_id": row[1],
                    "admin_username": row[2],
                    "action": row[3],
                    "target_type": row[4],
                    "target_id": row[5],
                    "details": json.loads(row[6]) if row[6] else None,
                    "ip_address": row[7],
                    "created_at": row[8]
                })

            return {
                "entries": entries,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size
            }

        finally:
            conn.close()


# Singleton instance
_admin_service: Optional[AdminService] = None

def get_admin_service() -> AdminService:
    global _admin_service
    if _admin_service is None:
        _admin_service = AdminService()
    return _admin_service
```

### 2.1.3 Admin Router

**New File:** `app/routers/admin.py`

```python
"""
Admin Router - API endpoints for admin operations.

All endpoints require admin authentication.
"""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from app.services.admin_service import get_admin_service
from app.routers.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/admin", tags=["admin"])


# =============================================================================
# Pydantic Models
# =============================================================================

class UserListParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    search: Optional[str] = None
    include_inactive: bool = False


class UserUpdate(BaseModel):
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None
    mode_restriction: Optional[str] = Field(
        default=None,
        description="'normal_only', 'no_full_unlock', or null for no restriction"
    )


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    is_admin: bool = False


class PasswordReset(BaseModel):
    new_password: str = Field(..., min_length=8)


class FeatureFlagUpdate(BaseModel):
    default_enabled: bool


class UserFeatureOverride(BaseModel):
    enabled: Optional[bool] = Field(
        description="True/False to override, null to use global default"
    )


# =============================================================================
# Dependencies
# =============================================================================

async def require_admin(current_user: dict = Depends(get_current_user)):
    """Dependency that requires admin status."""
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


def get_client_ip(request: Request) -> str:
    """Extract client IP from request."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


# =============================================================================
# User Management Endpoints
# =============================================================================

@router.get("/users")
async def list_users(
    page: int = 1,
    page_size: int = 20,
    search: Optional[str] = None,
    include_inactive: bool = False,
    admin: dict = Depends(require_admin)
):
    """List all users with pagination."""
    service = get_admin_service()
    return await service.list_users(
        page=page,
        page_size=page_size,
        search=search,
        include_inactive=include_inactive
    )


@router.get("/users/{user_id}")
async def get_user(
    user_id: int,
    admin: dict = Depends(require_admin)
):
    """Get detailed user information."""
    service = get_admin_service()
    user = await service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/users/{user_id}")
async def update_user(
    user_id: int,
    updates: UserUpdate,
    request: Request,
    admin: dict = Depends(require_admin)
):
    """Update user attributes."""
    service = get_admin_service()
    result = await service.update_user(
        user_id=user_id,
        admin_id=admin["id"],
        updates=updates.model_dump(exclude_none=True),
        ip_address=get_client_ip(request)
    )
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/users")
async def create_user(
    user_data: UserCreate,
    request: Request,
    admin: dict = Depends(require_admin)
):
    """Create a new user."""
    service = get_admin_service()
    result = await service.create_user(
        admin_id=admin["id"],
        username=user_data.username,
        password=user_data.password,
        is_admin=user_data.is_admin,
        ip_address=get_client_ip(request)
    )
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    request: Request,
    admin: dict = Depends(require_admin)
):
    """Delete a user and all their data."""
    service = get_admin_service()
    result = await service.delete_user(
        user_id=user_id,
        admin_id=admin["id"],
        ip_address=get_client_ip(request)
    )
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/users/{user_id}/reset-password")
async def reset_password(
    user_id: int,
    password_data: PasswordReset,
    request: Request,
    admin: dict = Depends(require_admin)
):
    """Reset a user's password."""
    service = get_admin_service()
    result = await service.reset_password(
        user_id=user_id,
        admin_id=admin["id"],
        new_password=password_data.new_password,
        ip_address=get_client_ip(request)
    )
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


# =============================================================================
# Feature Flag Endpoints
# =============================================================================

@router.get("/features")
async def list_features(admin: dict = Depends(require_admin)):
    """Get all feature flags with their defaults."""
    service = get_admin_service()
    return await service.list_feature_flags()


@router.patch("/features/{feature_key}")
async def update_feature(
    feature_key: str,
    update: FeatureFlagUpdate,
    request: Request,
    admin: dict = Depends(require_admin)
):
    """Update a global feature flag default."""
    service = get_admin_service()
    result = await service.update_feature_flag(
        admin_id=admin["id"],
        feature_key=feature_key,
        default_enabled=update.default_enabled,
        ip_address=get_client_ip(request)
    )
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.get("/users/{user_id}/features")
async def get_user_features(
    user_id: int,
    admin: dict = Depends(require_admin)
):
    """Get effective feature flags for a user."""
    service = get_admin_service()
    return await service.get_user_features(user_id)


@router.put("/users/{user_id}/features/{feature_key}")
async def set_user_feature(
    user_id: int,
    feature_key: str,
    override: UserFeatureOverride,
    request: Request,
    admin: dict = Depends(require_admin)
):
    """Set a per-user feature override."""
    service = get_admin_service()
    result = await service.set_user_feature_override(
        admin_id=admin["id"],
        user_id=user_id,
        feature_key=feature_key,
        enabled=override.enabled,
        ip_address=get_client_ip(request)
    )
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


# =============================================================================
# Audit Log Endpoints
# =============================================================================

@router.get("/audit-log")
async def get_audit_log(
    page: int = 1,
    page_size: int = 50,
    admin_filter: Optional[int] = None,
    action: Optional[str] = None,
    admin: dict = Depends(require_admin)
):
    """Get admin audit log."""
    service = get_admin_service()
    return await service.get_audit_log(
        page=page,
        page_size=page_size,
        admin_id=admin_filter,
        action=action
    )
```

### 2.1.4 Auth Service Updates

**File:** `app/services/auth_service.py`

Add admin status to user retrieval:

```python
# Update get_user_by_id method to include is_admin
async def get_user_by_id(self, user_id: int) -> Optional[Dict]:
    """Returns user dict by ID, including admin status."""
    db = get_database()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, username, is_admin, is_active
            FROM users WHERE id = ?
        """, (user_id,))
        row = cursor.fetchone()
        if row:
            return {
                "id": row[0],
                "username": row[1],
                "is_admin": bool(row[2]) if row[2] is not None else False,
                "is_active": bool(row[3]) if row[3] is not None else True
            }
        return None
    finally:
        conn.close()
```

**File:** `app/routers/auth.py`

Update `get_current_user` to check active status:

```python
async def get_current_user(request: Request) -> dict:
    """Dependency to get current authenticated user."""
    # ... existing token validation ...

    user = await auth_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    # Check if user is active
    if not user.get("is_active", True):
        raise HTTPException(status_code=403, detail="Account deactivated")

    return user
```

### 2.1.5 Register Admin Router

**File:** `app/main.py`

Add to router imports and registration:

```python
from app.routers import admin

# In create_app() or after app creation:
app.include_router(admin.router)
```

### 2.1.6 Initial Admin User Setup

**New File:** `scripts/create_admin.py`

```python
#!/usr/bin/env python3
"""
Create an admin user for PeanutChat.

Usage:
    python scripts/create_admin.py <username> <password>

Or interactively:
    python scripts/create_admin.py
"""

import sys
import asyncio
import getpass
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.auth_service import AuthService
from app.services.database import get_database


async def create_admin(username: str, password: str) -> bool:
    """Create an admin user."""
    auth_service = AuthService()

    # Create user
    user_id = await auth_service.create_user(username, password)
    if not user_id:
        print(f"Error: Username '{username}' already exists")
        return False

    # Set admin flag
    db = get_database()
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET is_admin = 1 WHERE id = ?", (user_id,))
        db.commit()
        print(f"Admin user '{username}' created successfully (ID: {user_id})")
        return True
    finally:
        conn.close()


def main():
    if len(sys.argv) == 3:
        username = sys.argv[1]
        password = sys.argv[2]
    else:
        username = input("Admin username: ").strip()
        if not username:
            print("Username cannot be empty")
            sys.exit(1)

        password = getpass.getpass("Admin password: ")
        if len(password) < 8:
            print("Password must be at least 8 characters")
            sys.exit(1)

        confirm = getpass.getpass("Confirm password: ")
        if password != confirm:
            print("Passwords do not match")
            sys.exit(1)

    success = asyncio.run(create_admin(username, password))
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
```

---

## 3. Phase 2.2: Feature & Mode Control

### 3.1 Feature Checking Service

**New File:** `app/services/feature_service.py`

```python
"""
Feature Service - Check feature availability for users.

Integrates with admin feature flags and user overrides.
"""

import logging
from typing import Optional, Dict, Set
from functools import lru_cache

from app.services.database import get_database

logger = logging.getLogger(__name__)


class FeatureService:
    """Check feature availability for users."""

    # Cache TTL in seconds
    CACHE_TTL = 60

    def __init__(self):
        self._global_cache: Optional[Dict[str, bool]] = None
        self._global_cache_time: float = 0

    async def is_feature_enabled(
        self,
        feature_key: str,
        user_id: Optional[int] = None
    ) -> bool:
        """
        Check if a feature is enabled for a user.

        Priority:
        1. User-specific override (if exists)
        2. Global default
        """
        db = get_database()
        try:
            cursor = conn.cursor()

            # Check user override first
            if user_id:
                cursor.execute("""
                    SELECT enabled FROM user_feature_overrides
                    WHERE user_id = ? AND feature_key = ?
                """, (user_id, feature_key))
                row = cursor.fetchone()
                if row:
                    return bool(row[0])

            # Fall back to global default
            cursor.execute("""
                SELECT default_enabled FROM feature_flags
                WHERE feature_key = ?
            """, (feature_key,))
            row = cursor.fetchone()

            # Default to enabled if feature not found
            return bool(row[0]) if row else True

        finally:
            conn.close()

    async def get_enabled_features(self, user_id: Optional[int] = None) -> Set[str]:
        """Get set of enabled feature keys for a user."""
        db = get_database()
        try:
            cursor = conn.cursor()

            # Get all global defaults
            cursor.execute("SELECT feature_key, default_enabled FROM feature_flags")
            features = {row[0]: bool(row[1]) for row in cursor.fetchall()}

            # Apply user overrides
            if user_id:
                cursor.execute("""
                    SELECT feature_key, enabled FROM user_feature_overrides
                    WHERE user_id = ?
                """, (user_id,))
                for row in cursor.fetchall():
                    features[row[0]] = bool(row[1])

            return {k for k, v in features.items() if v}

        finally:
            conn.close()

    async def get_available_tools(self, user_id: int) -> Set[str]:
        """
        Get set of available tool names based on feature flags.

        Returns tool names that can be included in chat requests.
        """
        enabled = await self.get_enabled_features(user_id)

        tools = set()

        if "tool_use" not in enabled:
            return tools  # No tools if tool_use disabled

        # Map feature flags to tool names
        feature_to_tools = {
            "web_search": ["web_search"],
            "browse_url": ["browse_url"],
            "memory_system": ["add_memory", "query_memories"],
            "knowledge_base": ["search_knowledge", "add_to_knowledge"],
            "image_generation": ["generate_image"],
            "video_generation": ["generate_video"],
            "mcp_tools": []  # MCP tools handled separately
        }

        for feature, tool_names in feature_to_tools.items():
            if feature in enabled:
                tools.update(tool_names)

        return tools


# Singleton
_feature_service: Optional[FeatureService] = None

def get_feature_service() -> FeatureService:
    global _feature_service
    if _feature_service is None:
        _feature_service = FeatureService()
    return _feature_service
```

### 3.2 Mode Restriction Enforcement

**File:** `app/services/user_profile_service.py`

Add mode restriction checking:

```python
class UserProfileService:
    """Business logic for user profile operations."""

    async def _check_mode_restriction(self, user_id: int) -> Optional[str]:
        """
        Check if user has mode restrictions.

        Returns:
            None: No restrictions
            "normal_only": Cannot enable adult mode
            "no_full_unlock": Can enable adult mode but not full unlock
        """
        db = get_database()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT mode_restriction FROM users WHERE id = ?",
                (user_id,)
            )
            row = cursor.fetchone()
            return row[0] if row else None
        finally:
            conn.close()

    async def enable_adult_mode(self, user_id: int, passcode: str) -> Dict:
        """Enable adult mode for user, respecting restrictions."""
        # Check restriction first
        restriction = await self._check_mode_restriction(user_id)
        if restriction == "normal_only":
            return {
                "success": False,
                "error": "Adult mode is not available for this account"
            }

        # ... existing passcode validation ...

    async def full_unlock(self, user_id: int, session_id: str) -> Dict:
        """Full unlock for session, respecting restrictions."""
        # Check restriction first
        restriction = await self._check_mode_restriction(user_id)
        if restriction in ("normal_only", "no_full_unlock"):
            return {
                "success": False,
                "error": "Full unlock is not available for this account"
            }

        # ... existing full unlock logic ...
```

### 3.3 Tool Filtering in Chat

**File:** `app/routers/chat.py`

Integrate feature checking:

```python
from app.services.feature_service import get_feature_service

@router.post("/chat")
async def chat(request: ChatRequest, current_user: dict = Depends(get_current_user)):
    """Main chat endpoint with feature-gated tools."""

    feature_service = get_feature_service()
    user_id = current_user["id"]

    # Get available tools for this user
    available_tool_names = await feature_service.get_available_tools(user_id)

    # Filter tool definitions to only include available tools
    if request.tools:
        tools = [t for t in request.tools if t["function"]["name"] in available_tool_names]
    else:
        tools = None

    # Check thinking mode
    thinking_enabled = await feature_service.is_feature_enabled("thinking_mode", user_id)
    if not thinking_enabled:
        request.thinking = False

    # Check memory system
    memory_enabled = await feature_service.is_feature_enabled("memory_system", user_id)
    if not memory_enabled:
        memory_context = None
    else:
        # ... existing memory retrieval ...

    # ... rest of chat logic ...
```

### 3.4 Settings Panel Feature Visibility

**File:** `static/js/settings.js`

Update to hide disabled features:

```javascript
class SettingsManager {
    constructor() {
        this.enabledFeatures = new Set();
    }

    async loadEnabledFeatures() {
        try {
            const response = await fetch('/api/user/features', {
                headers: { 'Authorization': `Bearer ${this.token}` }
            });
            if (response.ok) {
                const features = await response.json();
                this.enabledFeatures = new Set(features);
                this.updateFeatureVisibility();
            }
        } catch (error) {
            console.error('Failed to load features:', error);
        }
    }

    updateFeatureVisibility() {
        // Hide/show settings based on enabled features
        const featureElements = {
            'thinking_mode': document.getElementById('thinking-toggle'),
            'memory_system': document.getElementById('memory-settings'),
            'tts': document.getElementById('tts-settings'),
            'stt': document.getElementById('stt-settings'),
            // ... more mappings
        };

        for (const [feature, element] of Object.entries(featureElements)) {
            if (element) {
                element.style.display = this.enabledFeatures.has(feature) ? '' : 'none';
            }
        }
    }
}
```

---

## 4. Phase 2.3: Theme Management & Dashboard

### 4.1 Theme Database Schema

Add to migration:

```sql
-- Themes table
CREATE TABLE IF NOT EXISTS themes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    display_name TEXT NOT NULL,
    description TEXT,
    css_variables TEXT NOT NULL,  -- JSON object
    is_system BOOLEAN DEFAULT 0,
    is_enabled BOOLEAN DEFAULT 1,
    created_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- Insert default themes
INSERT OR IGNORE INTO themes (name, display_name, description, css_variables, is_system) VALUES
    ('default', 'Default Dark', 'The classic dark theme', '{"--bg-primary":"#1a1a2e","--bg-secondary":"#16213e","--text-primary":"#eee","--text-secondary":"#aaa","--accent":"#e94560","--border":"#333"}', 1),
    ('midnight', 'Midnight Blue', 'Deep blue tones', '{"--bg-primary":"#0d1b2a","--bg-secondary":"#1b263b","--text-primary":"#e0e1dd","--text-secondary":"#778da9","--accent":"#415a77","--border":"#1b263b"}', 1),
    ('forest', 'Forest Green', 'Natural green palette', '{"--bg-primary":"#1a1c19","--bg-secondary":"#2d3129","--text-primary":"#e8e8e4","--text-secondary":"#a3a89e","--accent":"#5f7f5e","--border":"#3d4339"}', 1);
```

### 4.2 Theme Service

**New File:** `app/services/theme_service.py`

```python
"""
Theme Service - Manage UI themes.

Handles CRUD operations for themes with CSS variable validation.
"""

import json
import logging
import re
from typing import Optional, Dict, List, Any

from app.services.database import get_database

logger = logging.getLogger(__name__)


# Required CSS variables for a valid theme
REQUIRED_CSS_VARS = {
    "--bg-primary",
    "--bg-secondary",
    "--text-primary",
    "--text-secondary",
    "--accent",
    "--border"
}

# CSS color value pattern
CSS_COLOR_PATTERN = re.compile(
    r'^(#[0-9a-fA-F]{3,8}|'
    r'rgb\(\s*\d{1,3}\s*,\s*\d{1,3}\s*,\s*\d{1,3}\s*\)|'
    r'rgba\(\s*\d{1,3}\s*,\s*\d{1,3}\s*,\s*\d{1,3}\s*,\s*[\d.]+\s*\)|'
    r'hsl\(\s*\d{1,3}\s*,\s*\d{1,3}%\s*,\s*\d{1,3}%\s*\)|'
    r'hsla\(\s*\d{1,3}\s*,\s*\d{1,3}%\s*,\s*\d{1,3}%\s*,\s*[\d.]+\s*\))$'
)


class ThemeService:
    """Manage UI themes."""

    def validate_css_variables(self, css_vars: Dict[str, str]) -> List[str]:
        """
        Validate CSS variables.

        Returns list of error messages (empty if valid).
        """
        errors = []

        # Check required variables
        missing = REQUIRED_CSS_VARS - set(css_vars.keys())
        if missing:
            errors.append(f"Missing required variables: {', '.join(missing)}")

        # Validate color values
        for var, value in css_vars.items():
            if not var.startswith("--"):
                errors.append(f"Invalid variable name: {var} (must start with --)")
            elif not CSS_COLOR_PATTERN.match(value):
                errors.append(f"Invalid color value for {var}: {value}")

        return errors

    async def list_themes(self, include_disabled: bool = False) -> List[Dict[str, Any]]:
        """Get all themes."""
        db = get_database()
        try:
            cursor = conn.cursor()

            if include_disabled:
                cursor.execute("""
                    SELECT id, name, display_name, description, css_variables,
                           is_system, is_enabled, created_at
                    FROM themes
                    ORDER BY is_system DESC, display_name
                """)
            else:
                cursor.execute("""
                    SELECT id, name, display_name, description, css_variables,
                           is_system, is_enabled, created_at
                    FROM themes
                    WHERE is_enabled = 1
                    ORDER BY is_system DESC, display_name
                """)

            themes = []
            for row in cursor.fetchall():
                themes.append({
                    "id": row[0],
                    "name": row[1],
                    "display_name": row[2],
                    "description": row[3],
                    "css_variables": json.loads(row[4]),
                    "is_system": bool(row[5]),
                    "is_enabled": bool(row[6]),
                    "created_at": row[7]
                })

            return themes

        finally:
            conn.close()

    async def get_theme(self, theme_name: str) -> Optional[Dict[str, Any]]:
        """Get a specific theme by name."""
        db = get_database()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, display_name, description, css_variables,
                       is_system, is_enabled
                FROM themes
                WHERE name = ?
            """, (theme_name,))

            row = cursor.fetchone()
            if not row:
                return None

            return {
                "id": row[0],
                "name": row[1],
                "display_name": row[2],
                "description": row[3],
                "css_variables": json.loads(row[4]),
                "is_system": bool(row[5]),
                "is_enabled": bool(row[6])
            }

        finally:
            conn.close()

    async def create_theme(
        self,
        name: str,
        display_name: str,
        css_variables: Dict[str, str],
        description: Optional[str] = None,
        created_by: Optional[int] = None
    ) -> Dict[str, Any]:
        """Create a new theme."""
        # Validate CSS variables
        errors = self.validate_css_variables(css_variables)
        if errors:
            return {"success": False, "errors": errors}

        # Validate name format
        if not re.match(r'^[a-z][a-z0-9_-]*$', name):
            return {
                "success": False,
                "errors": ["Name must start with letter, contain only lowercase, numbers, - and _"]
            }

        db = get_database()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO themes (name, display_name, description, css_variables, created_by)
                VALUES (?, ?, ?, ?, ?)
            """, (name, display_name, description, json.dumps(css_variables), created_by))

            db.commit()

            return {"success": True, "id": cursor.lastrowid}

        except Exception as e:
            if "UNIQUE constraint" in str(e):
                return {"success": False, "errors": [f"Theme name '{name}' already exists"]}
            logger.error(f"Failed to create theme: {e}")
            return {"success": False, "errors": [str(e)]}
        finally:
            conn.close()

    async def update_theme(
        self,
        theme_name: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update an existing theme."""
        db = get_database()
        try:
            cursor = conn.cursor()

            # Check if theme exists and is not system
            cursor.execute(
                "SELECT is_system FROM themes WHERE name = ?",
                (theme_name,)
            )
            row = cursor.fetchone()
            if not row:
                return {"success": False, "error": "Theme not found"}
            if row[0] and "css_variables" in updates:
                return {"success": False, "error": "Cannot modify system theme colors"}

            # Validate CSS if being updated
            if "css_variables" in updates:
                errors = self.validate_css_variables(updates["css_variables"])
                if errors:
                    return {"success": False, "errors": errors}

            # Build update
            set_clauses = []
            params = []

            if "display_name" in updates:
                set_clauses.append("display_name = ?")
                params.append(updates["display_name"])

            if "description" in updates:
                set_clauses.append("description = ?")
                params.append(updates["description"])

            if "css_variables" in updates:
                set_clauses.append("css_variables = ?")
                params.append(json.dumps(updates["css_variables"]))

            if "is_enabled" in updates:
                set_clauses.append("is_enabled = ?")
                params.append(updates["is_enabled"])

            if not set_clauses:
                return {"success": False, "error": "No valid fields to update"}

            set_clauses.append("updated_at = CURRENT_TIMESTAMP")
            params.append(theme_name)

            cursor.execute(f"""
                UPDATE themes SET {', '.join(set_clauses)}
                WHERE name = ?
            """, params)

            db.commit()

            return {"success": True}

        except Exception as e:
            logger.error(f"Failed to update theme: {e}")
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    async def delete_theme(self, theme_name: str) -> Dict[str, Any]:
        """Delete a theme (cannot delete system themes)."""
        db = get_database()
        try:
            cursor = conn.cursor()

            # Check if system theme
            cursor.execute(
                "SELECT is_system FROM themes WHERE name = ?",
                (theme_name,)
            )
            row = cursor.fetchone()
            if not row:
                return {"success": False, "error": "Theme not found"}
            if row[0]:
                return {"success": False, "error": "Cannot delete system theme"}

            cursor.execute("DELETE FROM themes WHERE name = ?", (theme_name,))
            db.commit()

            return {"success": True}

        except Exception as e:
            logger.error(f"Failed to delete theme: {e}")
            return {"success": False, "error": str(e)}
        finally:
            conn.close()


# Singleton
_theme_service: Optional[ThemeService] = None

def get_theme_service() -> ThemeService:
    global _theme_service
    if _theme_service is None:
        _theme_service = ThemeService()
    return _theme_service
```

### 4.3 Admin Theme Endpoints

Add to `app/routers/admin.py`:

```python
from app.services.theme_service import get_theme_service

# Theme Models
class ThemeCreate(BaseModel):
    name: str = Field(..., pattern=r'^[a-z][a-z0-9_-]*$')
    display_name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None
    css_variables: Dict[str, str]


class ThemeUpdate(BaseModel):
    display_name: Optional[str] = None
    description: Optional[str] = None
    css_variables: Optional[Dict[str, str]] = None
    is_enabled: Optional[bool] = None


# Theme Endpoints
@router.get("/themes")
async def list_themes(
    include_disabled: bool = False,
    admin: dict = Depends(require_admin)
):
    """List all themes."""
    service = get_theme_service()
    return await service.list_themes(include_disabled=include_disabled)


@router.post("/themes")
async def create_theme(
    theme: ThemeCreate,
    request: Request,
    admin: dict = Depends(require_admin)
):
    """Create a new theme."""
    service = get_theme_service()
    result = await service.create_theme(
        name=theme.name,
        display_name=theme.display_name,
        css_variables=theme.css_variables,
        description=theme.description,
        created_by=admin["id"]
    )
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("errors", result.get("error")))
    return result


@router.patch("/themes/{theme_name}")
async def update_theme(
    theme_name: str,
    updates: ThemeUpdate,
    admin: dict = Depends(require_admin)
):
    """Update a theme."""
    service = get_theme_service()
    result = await service.update_theme(
        theme_name=theme_name,
        updates=updates.model_dump(exclude_none=True)
    )
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("errors", result.get("error")))
    return result


@router.delete("/themes/{theme_name}")
async def delete_theme(
    theme_name: str,
    admin: dict = Depends(require_admin)
):
    """Delete a theme."""
    service = get_theme_service()
    result = await service.delete_theme(theme_name)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result
```

### 4.4 System Dashboard Service

**New File:** `app/services/stats_service.py`

```python
"""
Stats Service - System statistics and dashboard data.
"""

import logging
from typing import Dict, Any
from datetime import datetime, timedelta

from app.services.database import get_database

logger = logging.getLogger(__name__)


class StatsService:
    """Gather system statistics."""

    async def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get overview statistics for admin dashboard."""
        db = get_database()
        try:
            cursor = conn.cursor()

            # User stats
            cursor.execute("SELECT COUNT(*) FROM users")
            total_users = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = 1")
            active_users = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM users WHERE is_admin = 1")
            admin_users = cursor.fetchone()[0]

            # Activity stats (last 24h)
            yesterday = (datetime.now() - timedelta(days=1)).isoformat()

            cursor.execute(
                "SELECT COUNT(*) FROM users WHERE last_login > ?",
                (yesterday,)
            )
            active_24h = cursor.fetchone()[0]

            # Conversation stats
            cursor.execute("SELECT COUNT(*) FROM conversations")
            total_conversations = cursor.fetchone()[0]

            cursor.execute(
                "SELECT COUNT(*) FROM conversations WHERE created_at > ?",
                (yesterday,)
            )
            conversations_24h = cursor.fetchone()[0]

            # Message stats
            cursor.execute("SELECT COUNT(*) FROM messages")
            total_messages = cursor.fetchone()[0]

            cursor.execute(
                "SELECT COUNT(*) FROM messages WHERE created_at > ?",
                (yesterday,)
            )
            messages_24h = cursor.fetchone()[0]

            # Memory stats
            cursor.execute("SELECT COUNT(*) FROM memories")
            total_memories = cursor.fetchone()[0]

            # Knowledge base stats
            cursor.execute("SELECT COUNT(*) FROM knowledge_chunks")
            total_knowledge_chunks = cursor.fetchone()[0]

            return {
                "users": {
                    "total": total_users,
                    "active": active_users,
                    "admins": admin_users,
                    "active_24h": active_24h
                },
                "conversations": {
                    "total": total_conversations,
                    "created_24h": conversations_24h
                },
                "messages": {
                    "total": total_messages,
                    "sent_24h": messages_24h
                },
                "memory": {
                    "total_memories": total_memories
                },
                "knowledge": {
                    "total_chunks": total_knowledge_chunks
                },
                "generated_at": datetime.now().isoformat()
            }

        finally:
            conn.close()

    async def get_user_activity(self, days: int = 7) -> Dict[str, Any]:
        """Get daily user activity for the last N days."""
        db = get_database()
        try:
            cursor = conn.cursor()

            activity = []
            for i in range(days):
                date = datetime.now() - timedelta(days=i)
                date_str = date.strftime("%Y-%m-%d")

                cursor.execute("""
                    SELECT COUNT(DISTINCT user_id) FROM conversations
                    WHERE DATE(created_at) = ?
                """, (date_str,))
                active_users = cursor.fetchone()[0]

                cursor.execute("""
                    SELECT COUNT(*) FROM messages
                    WHERE DATE(created_at) = ?
                """, (date_str,))
                messages = cursor.fetchone()[0]

                activity.append({
                    "date": date_str,
                    "active_users": active_users,
                    "messages": messages
                })

            return {"activity": list(reversed(activity))}

        finally:
            conn.close()


# Singleton
_stats_service = None

def get_stats_service() -> StatsService:
    global _stats_service
    if _stats_service is None:
        _stats_service = StatsService()
    return _stats_service
```

### 4.5 Dashboard Endpoints

Add to `app/routers/admin.py`:

```python
from app.services.stats_service import get_stats_service

@router.get("/dashboard")
async def get_dashboard(admin: dict = Depends(require_admin)):
    """Get admin dashboard statistics."""
    service = get_stats_service()
    return await service.get_dashboard_stats()


@router.get("/dashboard/activity")
async def get_activity(
    days: int = 7,
    admin: dict = Depends(require_admin)
):
    """Get daily user activity."""
    service = get_stats_service()
    return await service.get_user_activity(days=min(days, 30))
```

### 4.6 Admin Frontend

**New File:** `static/admin.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PeanutChat Admin</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <link rel="stylesheet" href="/static/css/admin.css">
</head>
<body class="bg-gray-900 text-gray-100 min-h-screen">
    <div id="app" class="flex">
        <!-- Sidebar -->
        <nav id="sidebar" class="w-64 bg-gray-800 min-h-screen p-4">
            <h1 class="text-xl font-bold text-white mb-8">PeanutChat Admin</h1>
            <ul class="space-y-2">
                <li>
                    <a href="#dashboard" class="nav-link block px-4 py-2 rounded hover:bg-gray-700">
                        Dashboard
                    </a>
                </li>
                <li>
                    <a href="#users" class="nav-link block px-4 py-2 rounded hover:bg-gray-700">
                        Users
                    </a>
                </li>
                <li>
                    <a href="#features" class="nav-link block px-4 py-2 rounded hover:bg-gray-700">
                        Features
                    </a>
                </li>
                <li>
                    <a href="#themes" class="nav-link block px-4 py-2 rounded hover:bg-gray-700">
                        Themes
                    </a>
                </li>
                <li>
                    <a href="#audit" class="nav-link block px-4 py-2 rounded hover:bg-gray-700">
                        Audit Log
                    </a>
                </li>
            </ul>
            <div class="mt-auto pt-8">
                <a href="/" class="text-gray-400 hover:text-white">
                    &larr; Back to Chat
                </a>
            </div>
        </nav>

        <!-- Main Content -->
        <main id="content" class="flex-1 p-8">
            <!-- Content loaded dynamically -->
        </main>
    </div>

    <script src="/static/js/admin.js"></script>
</body>
</html>
```

**New File:** `static/js/admin.js`

```javascript
/**
 * PeanutChat Admin Portal
 *
 * Single-page admin interface for user management, feature flags,
 * theme management, and system monitoring.
 */

class AdminPortal {
    constructor() {
        this.token = localStorage.getItem('token');
        this.currentSection = 'dashboard';

        if (!this.token) {
            window.location.href = '/';
            return;
        }

        this.init();
    }

    async init() {
        // Verify admin status
        const isAdmin = await this.verifyAdmin();
        if (!isAdmin) {
            alert('Admin access required');
            window.location.href = '/';
            return;
        }

        // Setup navigation
        this.setupNavigation();

        // Load initial section
        this.loadSection(window.location.hash.slice(1) || 'dashboard');
    }

    async verifyAdmin() {
        try {
            const response = await this.fetch('/api/auth/me');
            if (response.ok) {
                const user = await response.json();
                return user.is_admin === true;
            }
        } catch (error) {
            console.error('Failed to verify admin status:', error);
        }
        return false;
    }

    setupNavigation() {
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const section = link.getAttribute('href').slice(1);
                this.loadSection(section);
                history.pushState(null, '', `#${section}`);
            });
        });

        window.addEventListener('popstate', () => {
            this.loadSection(window.location.hash.slice(1) || 'dashboard');
        });
    }

    async loadSection(section) {
        this.currentSection = section;

        // Update active nav link
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('bg-gray-700');
            if (link.getAttribute('href') === `#${section}`) {
                link.classList.add('bg-gray-700');
            }
        });

        const content = document.getElementById('content');

        switch (section) {
            case 'dashboard':
                await this.renderDashboard(content);
                break;
            case 'users':
                await this.renderUsers(content);
                break;
            case 'features':
                await this.renderFeatures(content);
                break;
            case 'themes':
                await this.renderThemes(content);
                break;
            case 'audit':
                await this.renderAuditLog(content);
                break;
            default:
                content.innerHTML = '<p>Section not found</p>';
        }
    }

    // =========================================================================
    // Dashboard
    // =========================================================================

    async renderDashboard(container) {
        container.innerHTML = '<p>Loading dashboard...</p>';

        try {
            const stats = await this.fetchJson('/api/admin/dashboard');

            container.innerHTML = `
                <h2 class="text-2xl font-bold mb-6">Dashboard</h2>

                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                    ${this.statCard('Users', stats.users.total, `${stats.users.active_24h} active today`)}
                    ${this.statCard('Conversations', stats.conversations.total, `${stats.conversations.created_24h} today`)}
                    ${this.statCard('Messages', stats.messages.total, `${stats.messages.sent_24h} today`)}
                    ${this.statCard('Memories', stats.memory.total_memories, '')}
                </div>

                <div class="bg-gray-800 rounded-lg p-6">
                    <h3 class="text-lg font-semibold mb-4">Quick Stats</h3>
                    <ul class="space-y-2 text-gray-300">
                        <li>Active Users: ${stats.users.active}</li>
                        <li>Admin Users: ${stats.users.admins}</li>
                        <li>Knowledge Chunks: ${stats.knowledge.total_chunks}</li>
                    </ul>
                </div>
            `;
        } catch (error) {
            container.innerHTML = `<p class="text-red-400">Error loading dashboard: ${error.message}</p>`;
        }
    }

    statCard(title, value, subtitle) {
        return `
            <div class="bg-gray-800 rounded-lg p-4">
                <h3 class="text-gray-400 text-sm">${title}</h3>
                <p class="text-3xl font-bold">${value}</p>
                ${subtitle ? `<p class="text-gray-500 text-sm">${subtitle}</p>` : ''}
            </div>
        `;
    }

    // =========================================================================
    // Users
    // =========================================================================

    async renderUsers(container) {
        container.innerHTML = '<p>Loading users...</p>';

        try {
            const data = await this.fetchJson('/api/admin/users?include_inactive=true');

            container.innerHTML = `
                <div class="flex justify-between items-center mb-6">
                    <h2 class="text-2xl font-bold">Users</h2>
                    <button onclick="admin.showCreateUserModal()"
                            class="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded">
                        Create User
                    </button>
                </div>

                <div class="bg-gray-800 rounded-lg overflow-hidden">
                    <table class="w-full">
                        <thead class="bg-gray-700">
                            <tr>
                                <th class="px-4 py-3 text-left">Username</th>
                                <th class="px-4 py-3 text-left">Status</th>
                                <th class="px-4 py-3 text-left">Role</th>
                                <th class="px-4 py-3 text-left">Mode Restriction</th>
                                <th class="px-4 py-3 text-left">Last Login</th>
                                <th class="px-4 py-3 text-left">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${data.users.map(user => this.userRow(user)).join('')}
                        </tbody>
                    </table>
                </div>

                <p class="mt-4 text-gray-400">
                    Showing ${data.users.length} of ${data.total} users
                </p>
            `;
        } catch (error) {
            container.innerHTML = `<p class="text-red-400">Error loading users: ${error.message}</p>`;
        }
    }

    userRow(user) {
        const statusBadge = user.is_active
            ? '<span class="bg-green-600 px-2 py-1 rounded text-xs">Active</span>'
            : '<span class="bg-red-600 px-2 py-1 rounded text-xs">Inactive</span>';

        const roleBadge = user.is_admin
            ? '<span class="bg-purple-600 px-2 py-1 rounded text-xs">Admin</span>'
            : '<span class="bg-gray-600 px-2 py-1 rounded text-xs">User</span>';

        const restriction = user.mode_restriction || 'None';
        const lastLogin = user.last_login
            ? new Date(user.last_login).toLocaleDateString()
            : 'Never';

        return `
            <tr class="border-t border-gray-700 hover:bg-gray-750">
                <td class="px-4 py-3">${this.escapeHtml(user.username)}</td>
                <td class="px-4 py-3">${statusBadge}</td>
                <td class="px-4 py-3">${roleBadge}</td>
                <td class="px-4 py-3">${restriction}</td>
                <td class="px-4 py-3">${lastLogin}</td>
                <td class="px-4 py-3">
                    <button onclick="admin.editUser(${user.id})"
                            class="text-blue-400 hover:text-blue-300 mr-2">
                        Edit
                    </button>
                    <button onclick="admin.showUserFeatures(${user.id})"
                            class="text-green-400 hover:text-green-300 mr-2">
                        Features
                    </button>
                    <button onclick="admin.deleteUser(${user.id}, '${this.escapeHtml(user.username)}')"
                            class="text-red-400 hover:text-red-300">
                        Delete
                    </button>
                </td>
            </tr>
        `;
    }

    // =========================================================================
    // Features
    // =========================================================================

    async renderFeatures(container) {
        container.innerHTML = '<p>Loading features...</p>';

        try {
            const features = await this.fetchJson('/api/admin/features');

            // Group by category
            const grouped = {};
            for (const feature of features) {
                const cat = feature.category || 'general';
                if (!grouped[cat]) grouped[cat] = [];
                grouped[cat].push(feature);
            }

            container.innerHTML = `
                <h2 class="text-2xl font-bold mb-6">Feature Flags</h2>
                <p class="text-gray-400 mb-6">
                    Toggle features globally. Individual users can be overridden in the Users section.
                </p>

                ${Object.entries(grouped).map(([category, features]) => `
                    <div class="bg-gray-800 rounded-lg p-6 mb-4">
                        <h3 class="text-lg font-semibold mb-4 capitalize">${category}</h3>
                        <div class="space-y-4">
                            ${features.map(f => this.featureToggle(f)).join('')}
                        </div>
                    </div>
                `).join('')}
            `;
        } catch (error) {
            container.innerHTML = `<p class="text-red-400">Error loading features: ${error.message}</p>`;
        }
    }

    featureToggle(feature) {
        const checked = feature.default_enabled ? 'checked' : '';
        return `
            <div class="flex items-center justify-between">
                <div>
                    <span class="font-medium">${feature.display_name}</span>
                    <p class="text-gray-400 text-sm">${feature.description || ''}</p>
                </div>
                <label class="relative inline-flex items-center cursor-pointer">
                    <input type="checkbox" ${checked}
                           onchange="admin.toggleFeature('${feature.key}', this.checked)"
                           class="sr-only peer">
                    <div class="w-11 h-6 bg-gray-600 peer-focus:outline-none rounded-full peer
                                peer-checked:after:translate-x-full peer-checked:bg-blue-600
                                after:content-[''] after:absolute after:top-[2px] after:left-[2px]
                                after:bg-white after:rounded-full after:h-5 after:w-5
                                after:transition-all"></div>
                </label>
            </div>
        `;
    }

    async toggleFeature(key, enabled) {
        try {
            await this.fetch(`/api/admin/features/${key}`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ default_enabled: enabled })
            });
            this.showToast(`Feature "${key}" ${enabled ? 'enabled' : 'disabled'}`);
        } catch (error) {
            this.showToast(`Error: ${error.message}`, 'error');
            this.loadSection('features'); // Refresh to restore state
        }
    }

    // =========================================================================
    // Themes
    // =========================================================================

    async renderThemes(container) {
        container.innerHTML = '<p>Loading themes...</p>';

        try {
            const themes = await this.fetchJson('/api/admin/themes?include_disabled=true');

            container.innerHTML = `
                <div class="flex justify-between items-center mb-6">
                    <h2 class="text-2xl font-bold">Themes</h2>
                    <button onclick="admin.showCreateThemeModal()"
                            class="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded">
                        Create Theme
                    </button>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    ${themes.map(theme => this.themeCard(theme)).join('')}
                </div>
            `;
        } catch (error) {
            container.innerHTML = `<p class="text-red-400">Error loading themes: ${error.message}</p>`;
        }
    }

    themeCard(theme) {
        const vars = theme.css_variables;
        const isDisabled = !theme.is_enabled;
        const isSystem = theme.is_system;

        return `
            <div class="bg-gray-800 rounded-lg overflow-hidden ${isDisabled ? 'opacity-50' : ''}">
                <div class="h-24 flex" style="background: ${vars['--bg-primary']}">
                    <div class="w-1/3" style="background: ${vars['--bg-secondary']}"></div>
                    <div class="w-2/3 p-2">
                        <div class="text-sm" style="color: ${vars['--text-primary']}">Preview</div>
                        <div class="text-xs" style="color: ${vars['--text-secondary']}">Secondary</div>
                        <div class="mt-2 w-8 h-2 rounded" style="background: ${vars['--accent']}"></div>
                    </div>
                </div>
                <div class="p-4">
                    <div class="flex justify-between items-start">
                        <div>
                            <h3 class="font-semibold">${this.escapeHtml(theme.display_name)}</h3>
                            <p class="text-gray-400 text-sm">${theme.name}</p>
                        </div>
                        ${isSystem ? '<span class="text-xs bg-gray-600 px-2 py-1 rounded">System</span>' : ''}
                    </div>
                    <div class="mt-4 flex gap-2">
                        ${!isSystem ? `
                            <button onclick="admin.editTheme('${theme.name}')"
                                    class="text-blue-400 hover:text-blue-300 text-sm">
                                Edit
                            </button>
                            <button onclick="admin.deleteTheme('${theme.name}')"
                                    class="text-red-400 hover:text-red-300 text-sm">
                                Delete
                            </button>
                        ` : ''}
                        <button onclick="admin.toggleThemeEnabled('${theme.name}', ${!theme.is_enabled})"
                                class="text-gray-400 hover:text-gray-300 text-sm">
                            ${theme.is_enabled ? 'Disable' : 'Enable'}
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    // =========================================================================
    // Audit Log
    // =========================================================================

    async renderAuditLog(container) {
        container.innerHTML = '<p>Loading audit log...</p>';

        try {
            const data = await this.fetchJson('/api/admin/audit-log');

            container.innerHTML = `
                <h2 class="text-2xl font-bold mb-6">Audit Log</h2>

                <div class="bg-gray-800 rounded-lg overflow-hidden">
                    <table class="w-full">
                        <thead class="bg-gray-700">
                            <tr>
                                <th class="px-4 py-3 text-left">Time</th>
                                <th class="px-4 py-3 text-left">Admin</th>
                                <th class="px-4 py-3 text-left">Action</th>
                                <th class="px-4 py-3 text-left">Target</th>
                                <th class="px-4 py-3 text-left">Details</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${data.entries.map(entry => this.auditRow(entry)).join('')}
                        </tbody>
                    </table>
                </div>

                <p class="mt-4 text-gray-400">
                    Showing ${data.entries.length} of ${data.total} entries
                </p>
            `;
        } catch (error) {
            container.innerHTML = `<p class="text-red-400">Error loading audit log: ${error.message}</p>`;
        }
    }

    auditRow(entry) {
        const time = new Date(entry.created_at).toLocaleString();
        const details = entry.details ? JSON.stringify(entry.details) : '-';

        return `
            <tr class="border-t border-gray-700">
                <td class="px-4 py-3 text-sm">${time}</td>
                <td class="px-4 py-3">${this.escapeHtml(entry.admin_username)}</td>
                <td class="px-4 py-3">
                    <span class="bg-gray-600 px-2 py-1 rounded text-xs">${entry.action}</span>
                </td>
                <td class="px-4 py-3">${entry.target_type}: ${entry.target_id || '-'}</td>
                <td class="px-4 py-3 text-sm text-gray-400 truncate max-w-xs">${this.escapeHtml(details)}</td>
            </tr>
        `;
    }

    // =========================================================================
    // Helpers
    // =========================================================================

    async fetch(url, options = {}) {
        const headers = {
            'Authorization': `Bearer ${this.token}`,
            ...options.headers
        };
        return fetch(url, { ...options, headers });
    }

    async fetchJson(url, options = {}) {
        const response = await this.fetch(url, options);
        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.detail || response.statusText);
        }
        return response.json();
    }

    escapeHtml(str) {
        if (!str) return '';
        return str.replace(/[&<>"']/g, char => ({
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#39;'
        })[char]);
    }

    showToast(message, type = 'success') {
        // Simple toast implementation
        const toast = document.createElement('div');
        toast.className = `fixed bottom-4 right-4 px-6 py-3 rounded-lg ${
            type === 'error' ? 'bg-red-600' : 'bg-green-600'
        } text-white`;
        toast.textContent = message;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 3000);
    }
}

// Initialize admin portal
const admin = new AdminPortal();
```

---

## 5. Database Schema

### Complete Schema for Admin Features

```sql
-- Users table (extended)
ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT 0;
ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT 1;
ALTER TABLE users ADD COLUMN mode_restriction TEXT DEFAULT NULL;
-- Valid values: NULL, 'normal_only', 'no_full_unlock'

-- Feature flags (global defaults)
CREATE TABLE feature_flags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    feature_key TEXT UNIQUE NOT NULL,
    display_name TEXT NOT NULL,
    description TEXT,
    default_enabled BOOLEAN DEFAULT 1,
    category TEXT DEFAULT 'general',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User feature overrides (per-user settings)
CREATE TABLE user_feature_overrides (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    feature_key TEXT NOT NULL,
    enabled BOOLEAN NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id, feature_key)
);

-- Themes table
CREATE TABLE themes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    display_name TEXT NOT NULL,
    description TEXT,
    css_variables TEXT NOT NULL,  -- JSON
    is_system BOOLEAN DEFAULT 0,
    is_enabled BOOLEAN DEFAULT 1,
    created_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- Admin audit log
CREATE TABLE admin_audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    admin_id INTEGER NOT NULL,
    action TEXT NOT NULL,
    target_type TEXT NOT NULL,
    target_id TEXT,
    details TEXT,  -- JSON
    ip_address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (admin_id) REFERENCES users(id)
);

-- Indexes
CREATE INDEX idx_feature_overrides_user ON user_feature_overrides(user_id);
CREATE INDEX idx_audit_log_admin ON admin_audit_log(admin_id);
CREATE INDEX idx_audit_log_created ON admin_audit_log(created_at);
```

---

## 6. API Reference

### User Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/admin/users` | List users (paginated) |
| GET | `/api/admin/users/{id}` | Get user details |
| POST | `/api/admin/users` | Create user |
| PATCH | `/api/admin/users/{id}` | Update user |
| DELETE | `/api/admin/users/{id}` | Delete user |
| POST | `/api/admin/users/{id}/reset-password` | Reset password |

### Feature Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/admin/features` | List all feature flags |
| PATCH | `/api/admin/features/{key}` | Update global default |
| GET | `/api/admin/users/{id}/features` | Get user's effective features |
| PUT | `/api/admin/users/{id}/features/{key}` | Set user override |

### Theme Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/admin/themes` | List themes |
| POST | `/api/admin/themes` | Create theme |
| PATCH | `/api/admin/themes/{name}` | Update theme |
| DELETE | `/api/admin/themes/{name}` | Delete theme |

### Dashboard

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/admin/dashboard` | Get system stats |
| GET | `/api/admin/dashboard/activity` | Get activity trends |
| GET | `/api/admin/audit-log` | Get audit log |

---

## 7. Security Considerations

### Authentication

1. **Admin Verification**: All admin endpoints use `require_admin` dependency
2. **JWT Claims**: `is_admin` status fetched from DB on each request (not stored in JWT)
3. **Active Check**: Deactivated users cannot authenticate

### Authorization

1. **Self-Protection**: Admins cannot:
   - Remove their own admin status
   - Delete their own account
   - Deactivate themselves

2. **Audit Trail**: All admin actions logged with:
   - Admin user ID
   - Action type
   - Target entity
   - Change details
   - Client IP address

### Input Validation

1. **Theme CSS**: Only valid CSS color values accepted
2. **Mode Restrictions**: Enum validation (`normal_only`, `no_full_unlock`, or null)
3. **Feature Keys**: Must exist in feature_flags table

---

## 8. Testing Requirements

### Unit Tests

```python
# tests/test_admin_service.py

async def test_list_users_pagination():
    """Verify pagination works correctly."""

async def test_update_user_mode_restriction():
    """Verify mode restrictions can be set."""

async def test_cannot_demote_self():
    """Verify admin cannot remove own admin status."""

async def test_feature_override_priority():
    """Verify user override takes priority over global default."""
```

### Integration Tests

```python
# tests/test_admin_api.py

async def test_admin_endpoint_requires_admin():
    """Verify non-admin users get 403."""

async def test_create_user_via_api():
    """Verify user creation flow."""

async def test_feature_toggle_affects_chat():
    """Verify disabling tool_use removes tools from chat."""
```

### Manual Testing Checklist

- [ ] Create admin user via script
- [ ] Access admin portal at `/static/admin.html`
- [ ] Create/edit/delete users
- [ ] Set mode restrictions and verify enforcement
- [ ] Toggle features globally
- [ ] Set per-user feature overrides
- [ ] Create/edit/delete themes
- [ ] Verify theme appears in settings
- [ ] Check audit log records actions

---

## Implementation Phases

### Phase 2.1: Admin Foundation
- [ ] Database migration with new tables
- [ ] AdminService with user CRUD
- [ ] Admin router with authentication
- [ ] Auth service updates (is_admin, is_active)
- [ ] create_admin.py script

### Phase 2.2: Feature & Mode Control
- [ ] FeatureService for checking flags
- [ ] Mode restriction enforcement
- [ ] Tool filtering in chat endpoint
- [ ] Settings panel feature visibility
- [ ] Per-user feature overrides

### Phase 2.3: Theme Management & Dashboard
- [ ] ThemeService with CRUD
- [ ] Theme validation
- [ ] StatsService for dashboard
- [ ] Admin frontend (admin.html, admin.js)
- [ ] Audit log viewer

---

*End of Admin Portal Build Plan*
