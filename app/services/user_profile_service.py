"""User profile service with business logic."""
import json
import logging
import yaml
from datetime import datetime
from typing import Optional, Dict, Any, List
from app.services.user_profile_store import get_user_profile_store, get_default_profile_template
from app import config

logger = logging.getLogger(__name__)


class UserProfileService:
    """Business logic for user profile operations."""

    # Passcode loaded from environment variable for security
    ADULT_PASSCODE = config.ADULT_PASSCODE

    # Sensitive sections requiring explicit enablement
    SENSITIVE_SECTIONS = [
        "sexual_romantic",
        "substances_health",
        "dark_content",
        "private_self",
        "financial_context"
    ]

    # Visibility tiers for export
    DEFAULT_PUBLIC_FIELDS = [
        "identity.preferred_name",
        "identity.city",
        "technical.os_preference",
        "communication.conversation_style"
    ]

    DEFAULT_EXPORTABLE_SECTIONS = [
        "identity",
        "technical",
        "communication",
        "persona_preferences",
        "interaction",
        "preferences",
        "pet_peeves",
        "boundaries",
        "goals_aspirations",
        "learning_context",
        "work_context",
        "social_context"
    ]

    def __init__(self):
        self.store = get_user_profile_store()

    # CRUD Operations

    async def get_profile(self, user_id: int) -> Dict[str, Any]:
        """Get user's full profile."""
        profile = self.store.get_profile(user_id)
        if not profile:
            return {}
        return {
            "profile": profile.profile_data,
            "adult_mode_enabled": profile.adult_mode_enabled,
            "adult_mode_unlocked_at": profile.adult_mode_unlocked_at,
            "full_unlock_enabled": profile.full_unlock_enabled,
            "full_unlock_at": profile.full_unlock_at,
            "created_at": profile.created_at,
            "updated_at": profile.updated_at
        }

    async def update_profile(
        self,
        user_id: int,
        updates: List[Dict[str, Any]],
        reason: str
    ) -> Dict[str, Any]:
        """Update specific fields in the profile."""
        logger.info(f"Profile update for user {user_id}: {reason}")

        for update in updates:
            path = update.get("path", "")
            value = update.get("value")
            operation = update.get("operation", "set")

            # Validate sensitive section access
            section = path.split(".")[0] if path else ""
            if section in self.SENSITIVE_SECTIONS:
                profile = self.store.get_profile(user_id)
                if profile:
                    section_data = profile.profile_data.get(section, {})
                    if not section_data.get("enabled", False):
                        logger.warning(f"Attempted to update disabled section: {section}")
                        continue

            self.store.patch_profile_field(user_id, path, value, operation)

        return await self.get_profile(user_id)

    async def reset_profile(
        self,
        user_id: int,
        sections: List[str],
        preserve_identity: bool = True
    ) -> Dict[str, Any]:
        """Reset profile sections to defaults."""
        profile = self.store.get_profile(user_id)
        if not profile:
            return {}

        data = profile.profile_data
        default = get_default_profile_template()

        if "all" in sections:
            sections = list(default.keys())

        for section in sections:
            if preserve_identity and section == "identity":
                continue
            if section in default:
                data[section] = default[section]

        self.store.update_profile_data(user_id, data)
        logger.info(f"Reset sections {sections} for user {user_id}")
        return await self.get_profile(user_id)

    # Section Management

    async def read_sections(
        self,
        user_id: int,
        sections: List[str],
        include_disabled: bool = False
    ) -> Dict[str, Any]:
        """Read specific sections from profile."""
        profile = self.store.get_profile(user_id)
        if not profile:
            return {}

        data = profile.profile_data

        # If "all" requested, return all sections
        if "all" in sections:
            result = {}
            for key, value in data.items():
                # Skip disabled sensitive sections unless explicitly requested
                if key in self.SENSITIVE_SECTIONS and not include_disabled:
                    if isinstance(value, dict) and not value.get("enabled", False):
                        continue
                result[key] = value
            return result

        # Return requested sections
        result = {}
        for section in sections:
            if section in data:
                section_data = data[section]
                # Skip disabled sensitive sections unless explicitly requested
                if section in self.SENSITIVE_SECTIONS and not include_disabled:
                    if isinstance(section_data, dict) and not section_data.get("enabled", False):
                        continue
                result[section] = section_data

        return result

    async def enable_section(
        self,
        user_id: int,
        section: str,
        user_confirmed: bool,
        enabled: bool = True
    ) -> Dict[str, Any]:
        """Enable or disable a sensitive section."""
        if not user_confirmed:
            return {"success": False, "error": "User confirmation required"}

        if section not in self.SENSITIVE_SECTIONS:
            return {"success": False, "error": f"Section {section} is not a sensitive section"}

        self.store.patch_profile_field(user_id, f"{section}.enabled", enabled, "set")
        logger.info(f"Section {section} {'enabled' if enabled else 'disabled'} for user {user_id}")

        return {"success": True, "section": section, "enabled": enabled}

    # Field Operations

    async def update_field(
        self,
        user_id: int,
        path: str,
        value: Any,
        operation: str = "set"
    ) -> Dict[str, Any]:
        """Update a single field with operation."""
        profile = self.store.patch_profile_field(user_id, path, value, operation)
        if profile:
            return {"success": True, "updated_path": path}
        return {"success": False, "error": "Failed to update field"}

    async def add_nested(
        self,
        user_id: int,
        section: str,
        domain: str,
        key: str,
        value: str
    ) -> Dict[str, Any]:
        """Add a key-value pair to a nested object."""
        # Build the path based on section
        if section in ["preferences", "pet_peeves"]:
            path = f"{section}.{domain}.{key}" if domain != "custom" else f"{section}.custom.{key}"
        elif section.startswith("boundaries."):
            path = f"{section}.{key}"
        elif section.startswith("private_self."):
            path = f"{section}.{key}"
        elif section.startswith("values_beliefs."):
            path = f"{section}.{key}"
        elif section == "custom_fields.fields":
            path = f"custom_fields.fields.{key}"
        else:
            path = f"{section}.{domain}.{key}"

        self.store.patch_profile_field(user_id, path, value, "set")
        return {"success": True, "path": path}

    # Event Logging

    async def log_event(
        self,
        user_id: int,
        event_type: str,
        context: Optional[str] = None,
        severity: str = "moderate"
    ) -> Dict[str, Any]:
        """Log an interaction event."""
        profile = self.store.get_profile(user_id)
        if not profile:
            return {"success": False, "error": "Profile not found"}

        data = profile.profile_data
        now = datetime.utcnow().isoformat() + "Z"

        event = {
            "event_type": event_type,
            "context": context,
            "severity": severity,
            "timestamp": now
        }

        # Add to current session events
        if "interaction_log" not in data:
            data["interaction_log"] = {
                "current_session_events": [],
                "pending_evaluation": False,
                "last_evaluation": None,
                "evaluation_frequency_messages": 10
            }

        data["interaction_log"]["current_session_events"].append(event)
        data["interaction_log"]["pending_evaluation"] = True

        self.store.update_profile_data(user_id, data)
        logger.debug(f"Logged event {event_type} for user {user_id}")

        return {"success": True, "event_type": event_type, "timestamp": now}

    # Query

    async def query_profile(self, user_id: int, query: str) -> Dict[str, Any]:
        """Answer a natural language question about the profile."""
        profile = self.store.get_profile(user_id)
        if not profile:
            return {"success": False, "error": "Profile not found"}

        data = profile.profile_data
        query_lower = query.lower()

        # Simple keyword matching for common queries
        results = []

        if "name" in query_lower or "called" in query_lower:
            name = data.get("identity", {}).get("preferred_name")
            if name:
                results.append(f"Preferred name: {name}")

        if "language" in query_lower or "programming" in query_lower:
            langs = data.get("technical", {}).get("primary_languages", [])
            if langs:
                results.append(f"Primary languages: {', '.join(langs)}")

        if "style" in query_lower or "communication" in query_lower:
            style = data.get("communication", {}).get("conversation_style")
            if style:
                results.append(f"Conversation style: {style}")

        if "boundary" in query_lower or "boundaries" in query_lower:
            hard = data.get("boundaries", {}).get("hard_boundaries", [])
            soft = data.get("boundaries", {}).get("soft_boundaries", {})
            if hard:
                results.append(f"Hard boundaries: {', '.join(hard)}")
            if soft:
                results.append(f"Soft boundaries: {', '.join(soft.keys())}")

        if "peeve" in query_lower or "annoy" in query_lower or "hate" in query_lower:
            peeves = data.get("pet_peeves", {})
            all_peeves = []
            for category, items in peeves.items():
                if isinstance(items, list):
                    all_peeves.extend(items)
            if all_peeves:
                results.append(f"Pet peeves: {', '.join(all_peeves[:5])}")

        if "trust" in query_lower or "satisfaction" in query_lower or "relationship" in query_lower:
            metrics = data.get("relationship_metrics", {})
            results.append(f"Trust level: {metrics.get('trust_level', 50)}")
            results.append(f"Satisfaction level: {metrics.get('satisfaction_level', 50)}")
            results.append(f"Relationship stage: {metrics.get('relationship_stage', 'new')}")

        if "preference" in query_lower:
            prefs = data.get("preferences", {})
            for domain, items in prefs.items():
                if isinstance(items, dict) and items:
                    for k, v in list(items.items())[:2]:
                        results.append(f"{domain}/{k}: {v}")

        if not results:
            return {
                "success": True,
                "query": query,
                "answer": "No specific information found for that query.",
                "suggestion": "Try asking about: name, languages, communication style, boundaries, pet peeves, or preferences"
            }

        return {
            "success": True,
            "query": query,
            "answer": "\n".join(results)
        }

    # Export

    async def export_profile(
        self,
        user_id: int,
        format: str = "json",
        tier: str = "exportable",
        user_confirmed: bool = False
    ) -> str:
        """Export profile in specified format."""
        profile = self.store.get_profile(user_id)
        if not profile:
            return '{"error": "Profile not found"}'

        data = profile.profile_data

        # Filter based on tier
        if tier == "public":
            # Only public fields
            export_data = {}
            for field_path in self.DEFAULT_PUBLIC_FIELDS:
                parts = field_path.split(".")
                value = data
                for part in parts:
                    value = value.get(part, {}) if isinstance(value, dict) else None
                    if value is None:
                        break
                if value is not None:
                    section = parts[0]
                    if section not in export_data:
                        export_data[section] = {}
                    if len(parts) > 1:
                        export_data[section][parts[1]] = value
        elif tier == "exportable":
            # Exportable sections
            export_data = {}
            for section in self.DEFAULT_EXPORTABLE_SECTIONS:
                if section in data:
                    export_data[section] = data[section]
        elif tier == "full":
            if not user_confirmed:
                return '{"error": "Full export requires user confirmation"}'
            export_data = data
        else:
            export_data = data

        # Format output
        if format == "json":
            return json.dumps(export_data, indent=2)
        elif format == "yaml":
            return yaml.dump(export_data, default_flow_style=False)
        elif format == "summary":
            return self._generate_summary(export_data)
        else:
            return json.dumps(export_data, indent=2)

    def _generate_summary(self, data: Dict[str, Any]) -> str:
        """Generate a human-readable summary."""
        lines = ["# Profile Summary\n"]

        if "identity" in data:
            identity = data["identity"]
            if identity.get("preferred_name"):
                lines.append(f"**Name:** {identity['preferred_name']}")
            if identity.get("city"):
                lines.append(f"**Location:** {identity.get('city')}, {identity.get('state', '')}")

        if "communication" in data:
            comm = data["communication"]
            lines.append(f"\n**Communication Style:** {comm.get('conversation_style', 'adaptive')}")
            lines.append(f"**Response Length:** {comm.get('response_length', 'adaptive')}")

        if "technical" in data:
            tech = data["technical"]
            if tech.get("primary_languages"):
                lines.append(f"\n**Languages:** {', '.join(tech['primary_languages'])}")
            if tech.get("skill_level"):
                lines.append(f"**Skill Level:** {tech['skill_level']}")

        if "relationship_metrics" in data:
            metrics = data["relationship_metrics"]
            lines.append(f"\n**Relationship Stage:** {metrics.get('relationship_stage', 'new')}")
            lines.append(f"**Trust:** {metrics.get('trust_level', 50)}/100")
            lines.append(f"**Satisfaction:** {metrics.get('satisfaction_level', 50)}/100")

        return "\n".join(lines)

    # Adult Mode

    async def verify_passcode(self, user_id: int, passcode: str) -> Dict[str, Any]:
        """Verify passcode and enable adult mode."""
        if passcode != self.ADULT_PASSCODE:
            logger.warning(f"Failed adult mode unlock attempt for user {user_id}")
            return {"success": False, "error": "Invalid passcode"}

        profile = self.store.set_adult_mode(user_id, True)
        if profile:
            return {
                "success": True,
                "adult_mode_enabled": True,
                "unlocked_at": profile.adult_mode_unlocked_at
            }
        return {"success": False, "error": "Failed to enable adult mode"}

    async def disable_adult_mode(self, user_id: int) -> Dict[str, Any]:
        """Disable adult mode."""
        profile = self.store.set_adult_mode(user_id, False)
        if profile:
            return {"success": True, "adult_mode_enabled": False}
        return {"success": False, "error": "Failed to disable adult mode"}

    async def get_adult_mode_status(self, user_id: int) -> Dict[str, Any]:
        """Get adult mode status."""
        return self.store.get_adult_mode_status(user_id)

    # Full Unlock (Tier 2 Gate)

    async def set_full_unlock(self, user_id: int, enabled: bool) -> Dict[str, Any]:
        """Enable or disable full unlock (Tier 2 adult content gate).

        Requires adult_mode_enabled to be True first.
        """
        # Check adult mode is enabled first
        adult_status = self.store.get_adult_mode_status(user_id)
        if not adult_status.get("enabled") and enabled:
            return {
                "success": False,
                "error": "Adult mode must be enabled first via Settings"
            }

        profile = self.store.set_full_unlock(user_id, enabled)
        if profile:
            return {
                "success": True,
                "full_unlock_enabled": profile.full_unlock_enabled,
                "unlocked_at": profile.full_unlock_at
            }
        return {"success": False, "error": "Failed to update full unlock status"}

    async def get_full_unlock_status(self, user_id: int) -> Dict[str, Any]:
        """Get full unlock status (Tier 2 adult content gate) from database.

        NOTE: This returns the persistent database status.
        For runtime session-scoped unlock, use get_session_unlock_status().
        """
        return self.store.get_full_unlock_status(user_id)

    # Session-scoped unlock methods (CRITICAL for child safety)

    async def set_session_unlock(
        self,
        user_id: int,
        session_id: str,
        enabled: bool
    ) -> Dict[str, Any]:
        """Enable or disable session-scoped adult content access.

        This is the primary gate for adult content. New sessions start LOCKED.
        Users must explicitly run /full_unlock enable in each new session.

        Requires:
        - adult_mode_enabled = True (Tier 1, via passcode in Settings)

        Args:
            user_id: The user's ID
            session_id: The browser session ID (from X-Session-ID header)
            enabled: Whether to enable or disable

        Returns:
            Dict with success status and current state
        """
        if not session_id:
            return {"success": False, "error": "Session ID required"}

        # Check Tier 1 (uncensored mode) is enabled first (only for enabling adult mode)
        if enabled:
            adult_status = self.store.get_adult_mode_status(user_id)
            if not adult_status.get("enabled"):
                return {
                    "success": False,
                    "error": "Uncensored mode must be enabled first via Settings"
                }

        self.store.set_session_unlock(user_id, session_id, enabled)
        return {
            "success": True,
            "enabled": enabled,
            "session_id": session_id[:8] + "..."  # Truncated for privacy
        }

    async def get_session_unlock_status(
        self,
        user_id: int,
        session_id: str
    ) -> Dict[str, Any]:
        """Check if current session has adult content unlocked.

        Returns False (locked) for:
        - New sessions
        - Sessions where user called /full_unlock disable
        - Missing session ID
        """
        return self.store.get_session_unlock_status(user_id, session_id)

    async def clear_user_sessions(self, user_id: int) -> Dict[str, Any]:
        """Clear all session unlocks for a user (e.g., on logout)."""
        count = self.store.clear_user_sessions(user_id)
        return {"success": True, "sessions_cleared": count}

    # Helpers

    def _get_nested(self, data: Dict[str, Any], path: str) -> Any:
        """Get value at dot-notation path."""
        parts = path.split(".")
        value = data
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return None
        return value

    def _set_nested(self, data: Dict[str, Any], path: str, value: Any) -> Dict[str, Any]:
        """Set value at dot-notation path."""
        parts = path.split(".")
        current = data
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        current[parts[-1]] = value
        return data


# Global instance
_service_instance: Optional[UserProfileService] = None


def get_user_profile_service() -> UserProfileService:
    """Get the global user profile service instance."""
    global _service_instance
    if _service_instance is None:
        _service_instance = UserProfileService()
    return _service_instance
