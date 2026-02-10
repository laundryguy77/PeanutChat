"""Markdown-based user profile service.

Stores user profiles as simple markdown files with YAML frontmatter.
"""
import logging
import re
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# Profile storage directory
PROFILES_DIR = Path(__file__).parent.parent.parent / "data" / "profiles"


def get_default_profile() -> Dict[str, Any]:
    """Get default profile data."""
    return {
        "name": None,
        "timezone": None,
        "assistant_name": None,
        "communication_style": "casual",
        "response_length": "adaptive",
        "pronouns": None,
        "notes": ""
    }


def parse_frontmatter(content: str) -> tuple[Dict[str, Any], str]:
    """Parse YAML frontmatter from markdown content.

    Returns (frontmatter_dict, body_content)
    """
    frontmatter = {}
    body = content

    # Check for frontmatter delimiters
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            yaml_content = parts[1].strip()
            body = parts[2].strip()

            # Simple YAML parsing (key: value format)
            for line in yaml_content.split("\n"):
                line = line.strip()
                if ":" in line and not line.startswith("#"):
                    key, value = line.split(":", 1)
                    key = key.strip()
                    value = value.strip()

                    # Handle quoted strings
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]

                    # Handle null/empty values
                    if value.lower() in ("null", "~", ""):
                        value = None

                    frontmatter[key] = value

    return frontmatter, body


def format_frontmatter(data: Dict[str, Any]) -> str:
    """Format profile data as YAML frontmatter."""
    lines = ["---"]

    # Define field order
    field_order = ["name", "timezone", "assistant_name", "communication_style",
                   "response_length", "pronouns"]

    for key in field_order:
        if key in data:
            value = data[key]
            if value is None:
                lines.append(f"{key}: null")
            elif isinstance(value, str) and (" " in value or ":" in value):
                # Quote strings with spaces or colons
                lines.append(f'{key}: "{value}"')
            else:
                lines.append(f"{key}: {value}")

    lines.append("---")
    return "\n".join(lines)


class ProfileMarkdownService:
    """Service for managing markdown-based user profiles."""

    def __init__(self):
        # Ensure profiles directory exists
        PROFILES_DIR.mkdir(parents=True, exist_ok=True)

    def _get_profile_path(self, user_id: int) -> Path:
        """Get the path to a user's profile file."""
        return PROFILES_DIR / f"{user_id}.md"

    async def get_profile(self, user_id: int) -> Dict[str, Any]:
        """Get a user's profile, creating default if doesn't exist."""
        profile_path = self._get_profile_path(user_id)

        if not profile_path.exists():
            return await self.create_profile(user_id)

        try:
            content = profile_path.read_text(encoding="utf-8")
            frontmatter, notes = parse_frontmatter(content)

            # Merge with defaults to ensure all fields exist
            profile = get_default_profile()
            profile.update(frontmatter)
            profile["notes"] = notes

            return profile
        except Exception as e:
            logger.error(f"Failed to read profile for user {user_id}: {e}")
            return get_default_profile()

    async def create_profile(self, user_id: int) -> Dict[str, Any]:
        """Create a new profile with default values."""
        profile = get_default_profile()
        await self.save_profile(user_id, profile)
        logger.info(f"Created default profile for user {user_id}")
        return profile

    async def save_profile(self, user_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Save profile data to markdown file."""
        profile_path = self._get_profile_path(user_id)

        # Separate notes from frontmatter fields
        notes = data.pop("notes", "") if "notes" in data else ""

        # Build markdown content
        frontmatter = format_frontmatter(data)

        content = frontmatter
        if notes:
            content += f"\n\n# Notes\n\n{notes}"

        # Write to file
        try:
            profile_path.write_text(content, encoding="utf-8")
            logger.info(f"Saved profile for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to save profile for user {user_id}: {e}")
            raise

        # Re-add notes to return data
        data["notes"] = notes
        return data

    async def update_profile(self, user_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update specific fields in a user's profile."""
        profile = await self.get_profile(user_id)
        profile.update(updates)
        return await self.save_profile(user_id, profile)

    async def reset_profile(self, user_id: int) -> Dict[str, Any]:
        """Reset profile to defaults."""
        profile = get_default_profile()
        await self.save_profile(user_id, profile)
        logger.info(f"Reset profile for user {user_id}")
        return profile

    def profile_exists(self, user_id: int) -> bool:
        """Check if a profile file exists."""
        return self._get_profile_path(user_id).exists()


# Global instance
_service_instance: Optional[ProfileMarkdownService] = None


def get_profile_markdown_service() -> ProfileMarkdownService:
    """Get the global profile markdown service instance."""
    global _service_instance
    if _service_instance is None:
        _service_instance = ProfileMarkdownService()
    return _service_instance
