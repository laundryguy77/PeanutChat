"""
Admin Service - User management and system administration.

Provides:
- User CRUD operations (create, list, edit, delete)
- Feature flag management (global + per-user overrides)
- Mode restriction enforcement
- Password reset
- Audit logging
- System statistics

Usage:
    service = get_admin_service()
    users = await service.list_users()
    await service.create_user(admin_id, "username", "password")
"""

import json
import logging
import shutil
import bcrypt
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

from app.services.database import get_database
from app import config

logger = logging.getLogger(__name__)


class AdminService:
    """Admin operations service."""

    # ==========================================================================
    # User Management
    # ==========================================================================

    async def list_users(
        self,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        include_inactive: bool = False
    ) -> Dict[str, Any]:
        """List all users with pagination."""
        db = get_database()

        offset = (page - 1) * page_size

        # Build query
        where_clauses = []
        params = []

        if not include_inactive:
            where_clauses.append("(is_active = 1 OR is_active IS NULL)")

        if search:
            where_clauses.append("username LIKE ?")
            params.append(f"%{search}%")

        where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

        # Get total count
        count_row = db.fetchone(
            f"SELECT COUNT(*) FROM users {where_sql}",
            tuple(params)
        )
        total = count_row[0] if count_row else 0

        # Get users
        params.extend([page_size, offset])
        rows = db.fetchall(
            f"""SELECT id, username, is_admin, is_active, mode_restriction,
                       voice_enabled, created_at
                FROM users {where_sql}
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?""",
            tuple(params)
        )

        users = []
        for row in rows:
            users.append({
                "id": row[0],
                "username": row[1],
                "is_admin": bool(row[2]) if row[2] is not None else False,
                "is_active": bool(row[3]) if row[3] is not None else True,
                "mode_restriction": row[4],
                "voice_enabled": bool(row[5]) if row[5] is not None else True,
                "created_at": row[6]
            })

        return {
            "users": users,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }

    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed user information."""
        db = get_database()

        row = db.fetchone(
            """SELECT id, username, is_admin, is_active, mode_restriction,
                      voice_enabled, created_at
               FROM users WHERE id = ?""",
            (user_id,)
        )

        if not row:
            return None

        # Get profile info
        profile_row = db.fetchone(
            """SELECT adult_mode_enabled, full_unlock_enabled, updated_at
               FROM user_profiles WHERE user_id = ?""",
            (user_id,)
        )

        # Get feature overrides
        overrides = db.fetchall(
            """SELECT feature_key, enabled FROM user_feature_overrides
               WHERE user_id = ?""",
            (user_id,)
        )

        return {
            "id": row[0],
            "username": row[1],
            "is_admin": bool(row[2]) if row[2] is not None else False,
            "is_active": bool(row[3]) if row[3] is not None else True,
            "mode_restriction": row[4],
            "voice_enabled": bool(row[5]) if row[5] is not None else True,
            "created_at": row[6],
            "adult_mode_enabled": bool(profile_row[0]) if profile_row else False,
            "full_unlock_enabled": bool(profile_row[1]) if profile_row else False,
            "profile_updated_at": profile_row[2] if profile_row else None,
            "feature_overrides": {r[0]: bool(r[1]) for r in overrides}
        }

    async def create_user(
        self,
        admin_id: int,
        username: str,
        password: str,
        is_admin: bool = False,
        ip_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new user."""
        db = get_database()

        # Check if username exists
        existing = db.fetchone(
            "SELECT id FROM users WHERE username = ?",
            (username,)
        )
        if existing:
            return {"success": False, "error": "Username already exists"}

        # Hash password
        password_hash = bcrypt.hashpw(
            password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')

        # Create user
        now = datetime.utcnow().isoformat() + "Z"
        db.execute(
            """INSERT INTO users (username, password_hash, is_admin, is_active, created_at)
               VALUES (?, ?, ?, 1, ?)""",
            (username, password_hash, 1 if is_admin else 0, now)
        )

        # Get new user ID
        row = db.fetchone("SELECT last_insert_rowid()")
        user_id = row[0]

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

    async def update_user(
        self,
        user_id: int,
        admin_id: int,
        updates: Dict[str, Any],
        ip_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update user attributes."""
        db = get_database()

        # Prevent admin from demoting themselves
        if user_id == admin_id and updates.get("is_admin") is False:
            return {"success": False, "error": "Cannot remove your own admin status"}

        # Build update query
        allowed_fields = {"is_admin", "is_active", "mode_restriction", "voice_enabled"}
        set_clauses = []
        params = []

        for field, value in updates.items():
            if field in allowed_fields:
                set_clauses.append(f"{field} = ?")
                if isinstance(value, bool):
                    params.append(1 if value else 0)
                else:
                    params.append(value)

        if not set_clauses:
            return {"success": False, "error": "No valid fields to update"}

        params.append(user_id)
        db.execute(
            f"UPDATE users SET {', '.join(set_clauses)} WHERE id = ?",
            tuple(params)
        )

        # Audit log
        await self._audit_log(
            admin_id=admin_id,
            action="update_user",
            target_type="user",
            target_id=str(user_id),
            details=json.dumps(updates),
            ip_address=ip_address
        )

        return {"success": True}

    async def delete_user(
        self,
        user_id: int,
        admin_id: int,
        ip_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """Delete a user and all their data."""
        # Prevent self-deletion
        if user_id == admin_id:
            return {"success": False, "error": "Cannot delete your own account"}

        db = get_database()

        # Get username for audit log
        row = db.fetchone(
            "SELECT username FROM users WHERE id = ?",
            (user_id,)
        )
        if not row:
            return {"success": False, "error": "User not found"}

        username = row[0]

        try:
            # Delete database records
            db.execute("DELETE FROM memories WHERE user_id = ?", (user_id,))
            db.execute("DELETE FROM user_profiles WHERE user_id = ?", (user_id,))
            db.execute("DELETE FROM user_feature_overrides WHERE user_id = ?", (user_id,))
            db.execute("DELETE FROM user_settings WHERE user_id = ?", (user_id,))
            db.execute("DELETE FROM mcp_servers WHERE user_id = ?", (user_id,))
            db.execute("DELETE FROM documents WHERE user_id = ?", (user_id,))
            db.execute("DELETE FROM users WHERE id = ?", (user_id,))

            # Delete conversation JSON files
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
        """Reset a user's password."""
        password_hash = bcrypt.hashpw(
            new_password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')

        db = get_database()
        db.execute(
            "UPDATE users SET password_hash = ? WHERE id = ?",
            (password_hash, user_id)
        )

        # Audit log (don't log password)
        await self._audit_log(
            admin_id=admin_id,
            action="reset_password",
            target_type="user",
            target_id=str(user_id),
            details=None,
            ip_address=ip_address
        )

        return {"success": True}

    # ==========================================================================
    # Feature Flag Management
    # ==========================================================================

    async def list_feature_flags(self) -> List[Dict[str, Any]]:
        """Get all feature flags with their defaults."""
        db = get_database()

        rows = db.fetchall(
            """SELECT feature_key, display_name, description, default_enabled, category
               FROM feature_flags ORDER BY category, display_name"""
        )

        return [
            {
                "key": row[0],
                "display_name": row[1],
                "description": row[2],
                "default_enabled": bool(row[3]),
                "category": row[4]
            }
            for row in rows
        ]

    async def update_feature_flag(
        self,
        admin_id: int,
        feature_key: str,
        default_enabled: bool,
        ip_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update a global feature flag default."""
        db = get_database()

        # Check feature exists
        row = db.fetchone(
            "SELECT id FROM feature_flags WHERE feature_key = ?",
            (feature_key,)
        )
        if not row:
            return {"success": False, "error": "Feature not found"}

        db.execute(
            """UPDATE feature_flags
               SET default_enabled = ?, updated_at = datetime('now')
               WHERE feature_key = ?""",
            (1 if default_enabled else 0, feature_key)
        )

        # Audit log
        await self._audit_log(
            admin_id=admin_id,
            action="update_feature",
            target_type="feature",
            target_id=feature_key,
            details=json.dumps({"default_enabled": default_enabled}),
            ip_address=ip_address
        )

        return {"success": True}

    async def get_user_features(self, user_id: int) -> Dict[str, Any]:
        """Get effective feature flags for a user."""
        db = get_database()

        # Get all global defaults
        flags = db.fetchall(
            "SELECT feature_key, default_enabled FROM feature_flags"
        )
        features = {row[0]: bool(row[1]) for row in flags}

        # Apply user overrides
        overrides = db.fetchall(
            """SELECT feature_key, enabled FROM user_feature_overrides
               WHERE user_id = ?""",
            (user_id,)
        )

        override_map = {}
        for row in overrides:
            features[row[0]] = bool(row[1])
            override_map[row[0]] = bool(row[1])

        return {
            "user_id": user_id,
            "features": features,
            "overrides": override_map
        }

    async def set_user_feature_override(
        self,
        admin_id: int,
        user_id: int,
        feature_key: str,
        enabled: Optional[bool],
        ip_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """Set or clear a per-user feature override."""
        db = get_database()

        # Check feature exists
        row = db.fetchone(
            "SELECT id FROM feature_flags WHERE feature_key = ?",
            (feature_key,)
        )
        if not row:
            return {"success": False, "error": "Feature not found"}

        if enabled is None:
            # Clear override
            db.execute(
                """DELETE FROM user_feature_overrides
                   WHERE user_id = ? AND feature_key = ?""",
                (user_id, feature_key)
            )
        else:
            # Set override (upsert)
            db.execute(
                """INSERT INTO user_feature_overrides
                   (user_id, feature_key, enabled, created_at, created_by)
                   VALUES (?, ?, ?, datetime('now'), ?)
                   ON CONFLICT(user_id, feature_key) DO UPDATE SET
                   enabled = excluded.enabled""",
                (user_id, feature_key, 1 if enabled else 0, admin_id)
            )

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

    # ==========================================================================
    # Audit Log
    # ==========================================================================

    async def _audit_log(
        self,
        admin_id: int,
        action: str,
        target_type: str,
        target_id: Optional[str],
        details: Optional[str],
        ip_address: Optional[str]
    ) -> None:
        """Log an admin action."""
        db = get_database()

        db.execute(
            """INSERT INTO admin_audit_log
               (admin_id, action, target_type, target_id, details, ip_address, created_at)
               VALUES (?, ?, ?, ?, ?, ?, datetime('now'))""",
            (admin_id, action, target_type, target_id, details, ip_address)
        )

    async def get_audit_log(
        self,
        page: int = 1,
        page_size: int = 50,
        admin_id: Optional[int] = None,
        action: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get admin audit log with filtering."""
        db = get_database()

        offset = (page - 1) * page_size

        # Build query
        where_clauses = []
        params = []

        if admin_id:
            where_clauses.append("l.admin_id = ?")
            params.append(admin_id)

        if action:
            where_clauses.append("l.action = ?")
            params.append(action)

        if start_date:
            where_clauses.append("l.created_at >= ?")
            params.append(start_date)

        if end_date:
            where_clauses.append("l.created_at <= ?")
            params.append(end_date)

        where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

        # Get total count
        count_row = db.fetchone(
            f"SELECT COUNT(*) FROM admin_audit_log l {where_sql}",
            tuple(params)
        )
        total = count_row[0] if count_row else 0

        # Get entries
        params.extend([page_size, offset])
        rows = db.fetchall(
            f"""SELECT l.id, l.admin_id, u.username, l.action, l.target_type,
                       l.target_id, l.details, l.ip_address, l.created_at
                FROM admin_audit_log l
                JOIN users u ON l.admin_id = u.id
                {where_sql}
                ORDER BY l.created_at DESC
                LIMIT ? OFFSET ?""",
            tuple(params)
        )

        entries = []
        for row in rows:
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
            "page_size": page_size
        }

    # ==========================================================================
    # Dashboard Statistics
    # ==========================================================================

    async def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get system statistics for dashboard."""
        db = get_database()

        # User counts
        user_row = db.fetchone("SELECT COUNT(*) FROM users")
        total_users = user_row[0] if user_row else 0

        active_row = db.fetchone(
            "SELECT COUNT(*) FROM users WHERE is_active = 1 OR is_active IS NULL"
        )
        active_users = active_row[0] if active_row else 0

        admin_row = db.fetchone("SELECT COUNT(*) FROM users WHERE is_admin = 1")
        admin_count = admin_row[0] if admin_row else 0

        # Memory count
        memory_row = db.fetchone("SELECT COUNT(*) FROM memories")
        memory_count = memory_row[0] if memory_row else 0

        # Document count
        doc_row = db.fetchone("SELECT COUNT(*) FROM documents")
        doc_count = doc_row[0] if doc_row else 0

        # Conversation count (from JSON files)
        conv_count = 0
        conv_dir = Path(config.CONVERSATIONS_DIR)
        if conv_dir.exists():
            for user_dir in conv_dir.iterdir():
                if user_dir.is_dir():
                    conv_count += len(list(user_dir.glob("*.json")))

        # Recent activity (last 24h)
        recent_row = db.fetchone(
            """SELECT COUNT(*) FROM admin_audit_log
               WHERE created_at > datetime('now', '-1 day')"""
        )
        recent_actions = recent_row[0] if recent_row else 0

        # Feature flags status
        features_row = db.fetchone(
            """SELECT COUNT(*), SUM(CASE WHEN default_enabled = 1 THEN 1 ELSE 0 END)
               FROM feature_flags"""
        )
        total_features = features_row[0] if features_row else 0
        enabled_features = features_row[1] if features_row and features_row[1] else 0

        return {
            "users": {
                "total": total_users,
                "active": active_users,
                "admins": admin_count
            },
            "content": {
                "conversations": conv_count,
                "memories": memory_count,
                "documents": doc_count
            },
            "features": {
                "total": total_features,
                "enabled": enabled_features
            },
            "activity": {
                "recent_admin_actions": recent_actions
            }
        }


# Singleton
_admin_service: Optional[AdminService] = None


def get_admin_service() -> AdminService:
    """Get admin service singleton."""
    global _admin_service
    if _admin_service is None:
        _admin_service = AdminService()
    return _admin_service
