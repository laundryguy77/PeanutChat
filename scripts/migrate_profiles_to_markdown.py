#!/usr/bin/env python3
"""Migrate user profiles from SQLite to markdown files.

This script reads existing profiles from the SQLite database and creates
markdown files in data/profiles/ with the essential fields.
"""
import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.database import get_database
from app.services.profile_markdown_service import (
    get_profile_markdown_service,
    PROFILES_DIR
)


def migrate_profiles():
    """Migrate all profiles from SQLite to markdown."""
    db = get_database()
    service = get_profile_markdown_service()

    # Ensure target directory exists
    PROFILES_DIR.mkdir(parents=True, exist_ok=True)

    # Get all profiles from SQLite
    rows = db.fetchall("SELECT user_id, profile_data FROM user_profiles")

    if not rows:
        print("No profiles found in database.")
        return

    print(f"Found {len(rows)} profile(s) to migrate.")

    migrated = 0
    skipped = 0
    errors = 0

    for row in rows:
        user_id = row["user_id"]
        try:
            profile_data = json.loads(row["profile_data"])

            # Extract essential fields from complex structure
            identity = profile_data.get("identity", {})
            communication = profile_data.get("communication", {})
            persona = profile_data.get("persona_preferences", {})

            # Build simplified profile
            simple_profile = {
                "name": identity.get("preferred_name"),
                "timezone": identity.get("timezone"),
                "assistant_name": persona.get("assistant_name"),
                "communication_style": communication.get("conversation_style", "casual"),
                "response_length": communication.get("response_length", "adaptive"),
                "pronouns": identity.get("pronouns"),
                "notes": ""
            }

            # Check if markdown file already exists
            profile_path = PROFILES_DIR / f"{user_id}.md"
            if profile_path.exists():
                print(f"  User {user_id}: Markdown file already exists, skipping")
                skipped += 1
                continue

            # Save as markdown
            import asyncio
            asyncio.run(service.save_profile(user_id, simple_profile))
            print(f"  User {user_id}: Migrated successfully")
            migrated += 1

        except Exception as e:
            print(f"  User {user_id}: ERROR - {e}")
            errors += 1

    print(f"\nMigration complete:")
    print(f"  Migrated: {migrated}")
    print(f"  Skipped:  {skipped}")
    print(f"  Errors:   {errors}")


if __name__ == "__main__":
    migrate_profiles()
