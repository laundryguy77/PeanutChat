"""
Voice Settings Service - Manages per-user voice preferences.

Stores settings in user_profiles table within the profile_data JSON.

Usage:
    service = get_voice_settings_service()
    settings = await service.get_settings(user_id)
    await service.update_settings(user_id, {"voice_mode": "tts_only"})
"""

import json
import logging
from typing import Dict, Any, Optional

from app.services.database import get_database

logger = logging.getLogger(__name__)

DEFAULT_VOICE_SETTINGS = {
    "voice_mode": "disabled",  # disabled, transcribe_only, tts_only, conversation
    "tts_voice": "default",
    "tts_speed": 1.0,
    "tts_format": "mp3",
    "auto_play": True,
    "stt_language": "auto"
}


class VoiceSettingsService:
    """Manages voice settings stored in user profiles."""

    async def get_settings(self, user_id: int) -> Dict[str, Any]:
        """Get user's voice settings."""
        db = get_database()

        row = db.fetchone(
            "SELECT profile_data FROM user_profiles WHERE user_id = ?",
            (user_id,)
        )

        if not row or not row[0]:
            return DEFAULT_VOICE_SETTINGS.copy()

        try:
            profile = json.loads(row[0])
            voice_settings = profile.get("voice_settings", {})

            # Merge with defaults
            return {**DEFAULT_VOICE_SETTINGS, **voice_settings}
        except json.JSONDecodeError:
            logger.warning(f"Invalid profile JSON for user {user_id}")
            return DEFAULT_VOICE_SETTINGS.copy()

    async def update_settings(
        self,
        user_id: int,
        settings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update user's voice settings."""
        db = get_database()

        # Get current profile
        row = db.fetchone(
            "SELECT profile_data FROM user_profiles WHERE user_id = ?",
            (user_id,)
        )

        if row and row[0]:
            try:
                profile = json.loads(row[0])
            except json.JSONDecodeError:
                profile = {}
        else:
            profile = {}

        # Update voice settings
        current_voice = profile.get("voice_settings", {})
        current_voice.update(settings)
        profile["voice_settings"] = current_voice

        # Upsert profile
        db.execute(
            """
            INSERT INTO user_profiles (user_id, profile_data, updated_at)
            VALUES (?, ?, datetime('now'))
            ON CONFLICT(user_id) DO UPDATE SET
                profile_data = excluded.profile_data,
                updated_at = excluded.updated_at
            """,
            (user_id, json.dumps(profile))
        )

        return {**DEFAULT_VOICE_SETTINGS, **current_voice}

    async def is_voice_enabled_for_user(self, user_id: int) -> bool:
        """Check if voice features are enabled for this user (admin control)."""
        db = get_database()

        row = db.fetchone(
            "SELECT voice_enabled FROM users WHERE id = ?",
            (user_id,)
        )

        if row is None:
            return False

        # Default to enabled if column doesn't exist (migration not run yet)
        return bool(row[0]) if row[0] is not None else True


# Singleton
_voice_settings_service: Optional[VoiceSettingsService] = None


def get_voice_settings_service() -> VoiceSettingsService:
    """Get voice settings service singleton."""
    global _voice_settings_service
    if _voice_settings_service is None:
        _voice_settings_service = VoiceSettingsService()
    return _voice_settings_service
