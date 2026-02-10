"""User profile database operations."""
import json
import logging
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, Dict, Any
from app.services.database import get_database

logger = logging.getLogger(__name__)


class ConcurrentModificationError(Exception):
    """Raised when optimistic locking detects a concurrent modification."""
    pass


def get_default_profile_template() -> Dict[str, Any]:
    """Get the default profile template with all sections."""
    now = datetime.utcnow().isoformat() + "Z"
    return {
        "identity": {
            "user_id": None,
            "name": None,
            "preferred_name": None,
            "birth_date": None,
            "gender": None,
            "pronouns": None,
            "email": None,
            "city": None,
            "state": None,
            "country": None,
            "timezone": None
        },
        "technical": {
            "os_preference": None,
            "skill_level": None,
            "primary_languages": [],
            "frameworks": [],
            "tools": [],
            "use_cases": [],
            "device_types": []
        },
        "communication": {
            "conversation_style": "candid_direct",
            "response_length": "adaptive",
            "formatting_preference": "minimal",
            "vocabulary_level": "conversational",
            "humor_tolerance": "moderate",
            "profanity_comfort": "none",
            "emoji_preference": "minimal",
            "example_preference": "concrete",
            "explanation_depth": "adaptive"
        },
        "persona_preferences": {
            "assistant_name": None,
            "assistant_gender_presentation": "neutral",
            "assistant_age_range": None,
            "assistant_personality_archetype": "competent_peer",
            "formality_level": "casual",
            "emotional_availability": "moderate",
            "personality_notes": None
        },
        "interaction": {
            "proactivity_level": "moderate",
            "correction_style": "direct",
            "followup_question_tolerance": "moderate",
            "clarification_approach": "ask_when_unclear",
            "task_handoff_style": "complete_then_confirm",
            "availability_hours": None,
            "response_urgency_default": "normal",
            "multi_step_approach": "execute_then_summarize"
        },
        "preferences": {
            "general": {},
            "code": {},
            "writing": {},
            "research": {},
            "communication": {},
            "lifestyle": {},
            "entertainment": {},
            "custom": {}
        },
        "pet_peeves": {
            "responses": [],
            "formatting": [],
            "behavior": [],
            "language": [],
            "assumptions": [],
            "custom": {}
        },
        "boundaries": {
            "hard_boundaries": [],
            "soft_boundaries": {},
            "sensitive_topics": {},
            "trigger_warnings_requested": False,
            "topics_requiring_care": []
        },
        "values_beliefs": {
            "core_values": [],
            "political_leaning": None,
            "political_detail": {
                "fiscal": None,
                "social": None,
                "hot_topics": {},
                "discuss_politics": False,
                "debate_welcome": False
            },
            "spiritual_context": {
                "identity": None,
                "background": None,
                "practice_level": None,
                "discuss_spirituality": False,
                "sensitivity": "moderate"
            },
            "alternative_beliefs": [],
            "worldview_notes": None
        },
        "relationship_metrics": {
            "satisfaction_level": 50,
            "trust_level": 50,
            "interaction_count": 0,
            "relationship_stage": "new",
            "first_interaction": now,
            "last_interaction": now,
            "consecutive_positive_sessions": 0,
            "consecutive_negative_sessions": 0,
            "total_sessions": 0,
            "average_session_length_messages": 0
        },
        "goals_aspirations": {
            "short_term": [],
            "long_term": [],
            "abandoned": [],
            "secret_goals": [],
            "accountability_wanted": False,
            "progress_tracking_interest": False,
            "motivation_style": "intrinsic"
        },
        "social_context": {
            "living_situation": None,
            "household_members": [],
            "relationship_context": None,
            "children": {
                "has_children": False,
                "ages": [],
                "custody_situation": None
            },
            "pets": [],
            "close_relationships": [],
            "social_energy": None,
            "loneliness_factor": None,
            "support_system_strength": None
        },
        "work_context": {
            "employment_status": None,
            "industry": None,
            "role": None,
            "company_type": None,
            "work_style": None,
            "work_stress_level": None,
            "career_satisfaction": None,
            "professional_goals": [],
            "work_boundaries": {
                "discuss_work": True,
                "work_life_separation": "moderate"
            }
        },
        "learning_context": {
            "learning_style": None,
            "attention_span": None,
            "current_learning": [],
            "interests_to_explore": [],
            "expertise_areas": [],
            "knowledge_gaps_acknowledged": [],
            "feedback_reception": "direct",
            "challenge_tolerance": "moderate"
        },
        "meta_system": {
            "profile_created": now,
            "profile_last_updated": now,
            "profile_version": "1.0.0",
            "data_sharing_consent": {
                "analytics": False,
                "model_training": False,
                "profile_export": True,
                "third_party": False
            },
            "visibility_tiers": {
                "public": ["preferred_name", "city", "os_preference", "conversation_style"],
                "model_only": [],
                "exportable": ["identity", "communication", "preferences", "persona_preferences", "interaction", "technical"]
            },
            "encryption_enabled": False,
            "backup_frequency": "weekly",
            "retention_policy": "indefinite",
            "deletion_requested": False
        },
        "interaction_log": {
            "current_session_events": [],
            "pending_evaluation": False,
            "last_evaluation": None,
            "evaluation_frequency_messages": 10
        },
        "custom_fields": {
            "fields": {}
        }
    }


@dataclass
class UserProfile:
    """User profile data structure."""
    user_id: int
    profile_data: Dict[str, Any]
    created_at: str
    updated_at: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class UserProfileStore:
    """Handles user profile database operations."""

    def __init__(self):
        self.db = get_database()

    def get_profile(self, user_id: int) -> Optional[UserProfile]:
        """Get a user's profile, creating default if doesn't exist."""
        row = self.db.fetchone(
            "SELECT * FROM user_profiles WHERE user_id = ?",
            (user_id,)
        )

        if not row:
            return self.create_profile(user_id)

        return UserProfile(
            user_id=row["user_id"],
            profile_data=json.loads(row["profile_data"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"]
        )

    def create_profile(self, user_id: int) -> UserProfile:
        """Create a new profile with default template."""
        now = datetime.utcnow().isoformat() + "Z"
        profile_data = get_default_profile_template()

        # Set user_id in identity section
        profile_data["identity"]["user_id"] = f"usr_{user_id}"

        self.db.execute(
            """INSERT INTO user_profiles
               (user_id, profile_data, created_at, updated_at)
               VALUES (?, ?, ?, ?)""",
            (user_id, json.dumps(profile_data), now, now)
        )

        logger.info(f"Created default profile for user {user_id}")

        return UserProfile(
            user_id=user_id,
            profile_data=profile_data,
            created_at=now,
            updated_at=now
        )

    def update_profile_data(
        self,
        user_id: int,
        data: Dict[str, Any],
        expected_updated_at: Optional[str] = None
    ) -> Optional[UserProfile]:
        """Replace entire profile data.

        Args:
            user_id: The user's ID
            data: The new profile data to save
            expected_updated_at: If provided, uses optimistic locking - update only
                                 succeeds if current updated_at matches this value.
                                 Raises ConcurrentModificationError on mismatch.

        Returns:
            The updated UserProfile, or None if user not found

        Raises:
            ConcurrentModificationError: If expected_updated_at doesn't match (concurrent edit)
        """
        now = datetime.utcnow().isoformat() + "Z"

        # Update meta timestamp
        if "meta_system" in data:
            data["meta_system"]["profile_last_updated"] = now

        if expected_updated_at:
            # Optimistic locking: only update if version matches
            result = self.db.execute(
                """UPDATE user_profiles
                   SET profile_data = ?, updated_at = ?
                   WHERE user_id = ? AND updated_at = ?""",
                (json.dumps(data), now, user_id, expected_updated_at)
            )
            if result.rowcount == 0:
                # Check if profile exists or was concurrently modified
                existing = self.db.fetchone(
                    "SELECT updated_at FROM user_profiles WHERE user_id = ?",
                    (user_id,)
                )
                if existing:
                    raise ConcurrentModificationError(
                        f"Profile was modified by another request. "
                        f"Expected version {expected_updated_at}, found {existing['updated_at']}"
                    )
                return None
        else:
            self.db.execute(
                """UPDATE user_profiles
                   SET profile_data = ?, updated_at = ?
                   WHERE user_id = ?""",
                (json.dumps(data), now, user_id)
            )

        return self.get_profile(user_id)

    def patch_profile_field(
        self,
        user_id: int,
        path: str,
        value: Any,
        operation: str = "set",
        max_retries: int = 3
    ) -> Optional[UserProfile]:
        """Update a specific field using dot notation with optimistic locking.

        Uses optimistic locking to prevent lost updates from concurrent modifications.
        Automatically retries on conflict up to max_retries times.

        Operations:
        - set: Replace value
        - append: Add to array
        - remove: Remove from array
        - increment: Add to number
        - decrement: Subtract from number
        - toggle: Flip boolean

        Args:
            user_id: The user's ID
            path: Dot-notation path to the field (e.g., "identity.name")
            value: The value to set/append/remove/etc
            operation: The operation to perform
            max_retries: Maximum retry attempts on concurrent modification

        Returns:
            The updated UserProfile, or None if user not found

        Raises:
            ConcurrentModificationError: If max retries exceeded due to concurrent edits
        """
        for attempt in range(max_retries):
            profile = self.get_profile(user_id)
            if not profile:
                return None

            data = profile.profile_data
            expected_version = profile.updated_at

            # Navigate to parent and get key
            parts = path.split(".")
            parent = data
            for part in parts[:-1]:
                if part not in parent:
                    parent[part] = {}
                parent = parent[part]

            key = parts[-1]
            current = parent.get(key)

            # Apply operation
            if operation == "set":
                parent[key] = value
            elif operation == "append":
                if not isinstance(current, list):
                    parent[key] = []
                if value not in parent[key]:
                    parent[key].append(value)
            elif operation == "remove":
                if isinstance(current, list) and value in current:
                    parent[key].remove(value)
            elif operation == "increment":
                if isinstance(current, (int, float)):
                    parent[key] = current + (value if isinstance(value, (int, float)) else 1)
                else:
                    parent[key] = value if isinstance(value, (int, float)) else 1
            elif operation == "decrement":
                if isinstance(current, (int, float)):
                    parent[key] = current - (value if isinstance(value, (int, float)) else 1)
                else:
                    parent[key] = -(value if isinstance(value, (int, float)) else 1)
            elif operation == "toggle":
                parent[key] = not bool(current)

            try:
                return self.update_profile_data(user_id, data, expected_updated_at=expected_version)
            except ConcurrentModificationError:
                if attempt < max_retries - 1:
                    logger.warning(
                        f"Concurrent modification detected for user {user_id}, "
                        f"retrying ({attempt + 1}/{max_retries})"
                    )
                    continue
                raise

    def delete_profile(self, user_id: int) -> bool:
        """Delete a user's profile."""
        cursor = self.db.execute(
            "DELETE FROM user_profiles WHERE user_id = ?",
            (user_id,)
        )
        deleted = cursor.rowcount > 0
        if deleted:
            logger.info(f"Deleted profile for user {user_id}")
        return deleted


# Global instance
_store_instance: Optional[UserProfileStore] = None


def get_user_profile_store() -> UserProfileStore:
    """Get the global user profile store instance."""
    global _store_instance
    if _store_instance is None:
        _store_instance = UserProfileStore()
    return _store_instance
