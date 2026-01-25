"""
Feature Service - Check feature availability for users.

Integrates with admin feature flags and user overrides.

Usage:
    service = get_feature_service()

    # Check single feature
    if await service.is_feature_enabled("web_search", user_id):
        # Feature is enabled
        pass

    # Get all enabled features for a user
    features = await service.get_enabled_features(user_id)

    # Get available tools based on features
    tools = await service.get_available_tools(user_id)
"""

import logging
from typing import Optional, Set

from app.services.database import get_database

logger = logging.getLogger(__name__)


class FeatureService:
    """Check feature availability for users."""

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
        3. True (if feature not found - fail open)
        """
        db = get_database()

        # Check user override first
        if user_id:
            row = db.fetchone(
                """SELECT enabled FROM user_feature_overrides
                   WHERE user_id = ? AND feature_key = ?""",
                (user_id, feature_key)
            )
            if row:
                return bool(row[0])

        # Fall back to global default
        row = db.fetchone(
            "SELECT default_enabled FROM feature_flags WHERE feature_key = ?",
            (feature_key,)
        )

        # Default to enabled if feature not found
        return bool(row[0]) if row else True

    async def get_enabled_features(self, user_id: Optional[int] = None) -> Set[str]:
        """Get set of enabled feature keys for a user."""
        db = get_database()

        # Get all global defaults
        rows = db.fetchall("SELECT feature_key, default_enabled FROM feature_flags")
        features = {row[0]: bool(row[1]) for row in rows}

        # Apply user overrides
        if user_id:
            overrides = db.fetchall(
                """SELECT feature_key, enabled FROM user_feature_overrides
                   WHERE user_id = ?""",
                (user_id,)
            )
            for row in overrides:
                features[row[0]] = bool(row[1])

        return {k for k, v in features.items() if v}

    async def get_available_tools(self, user_id: int) -> Set[str]:
        """
        Get set of available tool names based on feature flags.

        Returns tool names that can be included in chat requests.
        """
        enabled = await self.get_enabled_features(user_id)

        tools = set()

        # Check if tool_use is enabled at all
        if "tool_use" not in enabled:
            return tools  # No tools if tool_use disabled

        # Map feature flags to tool names
        feature_to_tools = {
            "web_search": ["web_search"],
            "browse_website": ["browse_website"],
            "memory_system": ["add_memory", "query_memories"],
            "knowledge_base": ["search_knowledge", "add_to_knowledge"],
            "image_generation": ["image"],
            "video_generation": ["video"],
            "mcp_tools": []  # MCP tools handled separately
        }

        for feature, tool_names in feature_to_tools.items():
            if feature in enabled:
                tools.update(tool_names)

        return tools

    async def check_user_mode_restriction(
        self,
        user_id: int,
        requested_mode: str
    ) -> bool:
        """
        Check if user is allowed to use a specific content mode.

        Args:
            user_id: User to check
            requested_mode: Mode being requested (normal, uncensored, full_unlock)

        Returns:
            True if allowed, False if restricted
        """
        db = get_database()

        row = db.fetchone(
            "SELECT mode_restriction FROM users WHERE id = ?",
            (user_id,)
        )

        if not row or not row[0]:
            return True  # No restriction

        restriction = row[0]

        # Restriction enforcement
        if restriction == "normal_only":
            return requested_mode == "normal"
        elif restriction == "no_full_unlock":
            return requested_mode in ("normal", "uncensored")

        return True


# Singleton
_feature_service: Optional[FeatureService] = None


def get_feature_service() -> FeatureService:
    """Get feature service singleton."""
    global _feature_service
    if _feature_service is None:
        _feature_service = FeatureService()
    return _feature_service
