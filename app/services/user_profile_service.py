"""User profile service with business logic.

Uses markdown files for storage instead of SQLite.
"""
import json
import logging
from typing import Optional, Dict, Any, List
from app.services.profile_markdown_service import get_profile_markdown_service

logger = logging.getLogger(__name__)


class UserProfileService:
    """Business logic for user profile operations."""

    def __init__(self):
        self.md_service = get_profile_markdown_service()

    async def get_profile(self, user_id: int) -> Dict[str, Any]:
        """Get user's full profile."""
        profile = await self.md_service.get_profile(user_id)
        return {"profile": profile}

    async def update_profile(
        self,
        user_id: int,
        updates: List[Dict[str, Any]],
        reason: str
    ) -> Dict[str, Any]:
        """Update specific fields in the profile.

        Args:
            user_id: The user ID
            updates: List of updates with path, value, operation
            reason: Reason for the update (for logging)
        """
        logger.info(f"Profile update for user {user_id}: {reason}")

        profile = await self.md_service.get_profile(user_id)

        for update in updates:
            path = update.get("path", "")
            value = update.get("value")

            # Handle dot-notation paths by mapping to flat fields
            # Old format: identity.preferred_name -> name
            # Old format: persona_preferences.assistant_name -> assistant_name
            # Old format: communication.conversation_style -> communication_style
            # Old format: communication.response_length -> response_length

            field_mapping = {
                "identity.preferred_name": "name",
                "identity.timezone": "timezone",
                "identity.pronouns": "pronouns",
                "persona_preferences.assistant_name": "assistant_name",
                "communication.conversation_style": "communication_style",
                "communication.response_length": "response_length",
            }

            field = field_mapping.get(path, path)
            if field in profile:
                profile[field] = value

        await self.md_service.save_profile(user_id, profile)
        return await self.get_profile(user_id)

    async def reset_profile(
        self,
        user_id: int,
        sections: List[str] = None,
        preserve_identity: bool = True
    ) -> Dict[str, Any]:
        """Reset profile to defaults."""
        if preserve_identity:
            # Get current profile to preserve name
            current = await self.md_service.get_profile(user_id)
            await self.md_service.reset_profile(user_id)
            profile = await self.md_service.get_profile(user_id)
            # Restore name
            if current.get("name"):
                profile["name"] = current["name"]
                await self.md_service.save_profile(user_id, profile)
        else:
            await self.md_service.reset_profile(user_id)

        return await self.get_profile(user_id)

    async def read_sections(
        self,
        user_id: int,
        sections: List[str] = None,
        include_disabled: bool = False
    ) -> Dict[str, Any]:
        """Read profile sections.

        For backwards compatibility, returns data in the old nested format.
        """
        profile = await self.md_service.get_profile(user_id)

        # Map flat fields back to nested structure for compatibility
        return {
            "identity": {
                "preferred_name": profile.get("name"),
                "timezone": profile.get("timezone"),
                "pronouns": profile.get("pronouns"),
            },
            "persona_preferences": {
                "assistant_name": profile.get("assistant_name"),
            },
            "communication": {
                "conversation_style": profile.get("communication_style"),
                "response_length": profile.get("response_length"),
            },
            "relationship_metrics": {
                "satisfaction_level": 50,
                "trust_level": 50,
                "interaction_count": 0,
                "relationship_stage": "new",
            },
            "notes": profile.get("notes", ""),
        }

    async def update_field(
        self,
        user_id: int,
        path: str,
        value: Any,
        operation: str = "set"
    ) -> Dict[str, Any]:
        """Update a single field."""
        updates = [{"path": path, "value": value, "operation": operation}]
        await self.update_profile(user_id, updates, "Field update")
        return {"success": True, "updated_path": path}

    async def add_nested(
        self,
        user_id: int,
        section: str,
        domain: str,
        key: str,
        value: str
    ) -> Dict[str, Any]:
        """Add a key-value pair - appends to notes for markdown format."""
        profile = await self.md_service.get_profile(user_id)
        notes = profile.get("notes", "")
        notes += f"\n{section}/{domain}/{key}: {value}"
        profile["notes"] = notes.strip()
        await self.md_service.save_profile(user_id, profile)
        return {"success": True, "path": f"{section}.{domain}.{key}"}

    async def log_event(
        self,
        user_id: int,
        event_type: str,
        context: Optional[str] = None,
        severity: str = "moderate"
    ) -> Dict[str, Any]:
        """Log an interaction event - no-op in simplified version."""
        from datetime import datetime
        now = datetime.utcnow().isoformat() + "Z"
        logger.debug(f"Event {event_type} for user {user_id}: {context}")
        return {"success": True, "event_type": event_type, "timestamp": now}

    async def query_profile(self, user_id: int, query: str) -> Dict[str, Any]:
        """Answer a natural language question about the profile."""
        profile = await self.md_service.get_profile(user_id)
        query_lower = query.lower()

        results = []

        if "name" in query_lower or "called" in query_lower:
            if profile.get("name"):
                results.append(f"Preferred name: {profile['name']}")

        if "style" in query_lower or "communication" in query_lower:
            if profile.get("communication_style"):
                results.append(f"Communication style: {profile['communication_style']}")

        if "assistant" in query_lower:
            if profile.get("assistant_name"):
                results.append(f"Assistant name: {profile['assistant_name']}")

        if not results:
            return {
                "success": True,
                "query": query,
                "answer": "No specific information found for that query.",
                "suggestion": "Try asking about: name, communication style, or assistant name"
            }

        return {
            "success": True,
            "query": query,
            "answer": "\n".join(results)
        }

    async def export_profile(
        self,
        user_id: int,
        format: str = "json",
        tier: str = "exportable",
        user_confirmed: bool = False
    ) -> str:
        """Export profile in specified format."""
        profile = await self.md_service.get_profile(user_id)

        if format == "json":
            return json.dumps(profile, indent=2)
        elif format == "summary":
            lines = ["# Profile Summary\n"]
            if profile.get("name"):
                lines.append(f"**Name:** {profile['name']}")
            if profile.get("communication_style"):
                lines.append(f"**Communication Style:** {profile['communication_style']}")
            if profile.get("assistant_name"):
                lines.append(f"**Assistant Name:** {profile['assistant_name']}")
            return "\n".join(lines)
        else:
            return json.dumps(profile, indent=2)


# Global instance
_service_instance: Optional[UserProfileService] = None


def get_user_profile_service() -> UserProfileService:
    """Get the global user profile service instance."""
    global _service_instance
    if _service_instance is None:
        _service_instance = UserProfileService()
    return _service_instance
