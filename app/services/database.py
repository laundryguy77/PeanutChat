import sqlite3
import logging
from pathlib import Path
from contextlib import contextmanager
from typing import Optional, Generator
import threading

logger = logging.getLogger(__name__)

# Thread-local storage for connections
_local = threading.local()


class DatabaseService:
    """SQLite database service with connection management and migrations"""

    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self._ensure_db_directory()
        self._run_migrations()

    def _ensure_db_directory(self):
        """Ensure the database directory exists"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def _get_connection(self) -> sqlite3.Connection:
        """Get a thread-local database connection"""
        if not hasattr(_local, 'connection') or _local.connection is None:
            _local.connection = sqlite3.connect(
                str(self.db_path),
                check_same_thread=False
            )
            _local.connection.row_factory = sqlite3.Row
            # Enable foreign keys
            _local.connection.execute("PRAGMA foreign_keys = ON")
        return _local.connection

    @contextmanager
    def get_cursor(self) -> Generator[sqlite3.Cursor, None, None]:
        """Context manager for database cursor with automatic commit/rollback"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            cursor.close()

    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """Execute a query and return the cursor"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor

    def executemany(self, query: str, params_list: list) -> sqlite3.Cursor:
        """Execute a query with multiple parameter sets"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.executemany(query, params_list)
        conn.commit()
        return cursor

    def fetchone(self, query: str, params: tuple = ()) -> Optional[sqlite3.Row]:
        """Execute query and fetch one result"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchone()

    def fetchall(self, query: str, params: tuple = ()) -> list:
        """Execute query and fetch all results"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()

    def _run_migrations(self):
        """Run database migrations"""
        logger.info(f"Running database migrations on {self.db_path}")

        # Create migrations table if it doesn't exist
        self.execute("""
            CREATE TABLE IF NOT EXISTS migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Define migrations
        migrations = [
            ("001_create_users", self._migration_001_create_users),
            ("002_create_user_settings", self._migration_002_create_user_settings),
            ("003_create_conversations", self._migration_003_create_conversations),
            ("004_create_documents", self._migration_004_create_documents),
            ("005_create_chunks", self._migration_005_create_chunks),
            ("006_remove_tts_columns", self._migration_006_remove_tts_columns),
            ("007_create_memories", self._migration_007_create_memories),
            ("008_create_mcp_servers", self._migration_008_create_mcp_servers),
            ("009_create_user_profiles", self._migration_009_create_user_profiles),
            ("010_add_full_unlock_columns", self._migration_010_add_full_unlock_columns),
        ]

        # Run pending migrations
        for name, migration_func in migrations:
            if not self._migration_applied(name):
                logger.info(f"Applying migration: {name}")
                try:
                    migration_func()
                    self._mark_migration_applied(name)
                    logger.info(f"Migration {name} applied successfully")
                except Exception as e:
                    logger.error(f"Migration {name} failed: {e}")
                    raise

    def _migration_applied(self, name: str) -> bool:
        """Check if a migration has been applied"""
        result = self.fetchone(
            "SELECT 1 FROM migrations WHERE name = ?",
            (name,)
        )
        return result is not None

    def _mark_migration_applied(self, name: str):
        """Mark a migration as applied"""
        self.execute(
            "INSERT INTO migrations (name) VALUES (?)",
            (name,)
        )

    def _migration_001_create_users(self):
        """Create users table"""
        self.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.execute("CREATE INDEX idx_users_username ON users(username)")
        self.execute("CREATE INDEX idx_users_email ON users(email)")

    def _migration_002_create_user_settings(self):
        """Create user_settings table.

        NOTE: This migration creates TTS columns that are no longer used.
        Migration 006 (_migration_006_remove_tts_columns) removes them.
        """
        self.execute("""
            CREATE TABLE user_settings (
                user_id INTEGER PRIMARY KEY,
                model TEXT,
                temperature REAL,
                top_p REAL,
                top_k INTEGER,
                num_ctx INTEGER,
                repeat_penalty REAL,
                persona TEXT,
                tts_enabled INTEGER DEFAULT 0,
                tts_speaker INTEGER DEFAULT 0,
                tts_temperature REAL DEFAULT 0.9,
                tts_topk INTEGER DEFAULT 50,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

    def _migration_003_create_conversations(self):
        """Create conversations table"""
        self.execute("""
            CREATE TABLE conversations (
                id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                title TEXT,
                model TEXT,
                created_at TEXT,
                updated_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        self.execute("CREATE INDEX idx_conversations_user_id ON conversations(user_id)")
        self.execute("CREATE INDEX idx_conversations_updated_at ON conversations(updated_at)")

    def _migration_004_create_documents(self):
        """Create documents table for knowledge base"""
        self.execute("""
            CREATE TABLE documents (
                id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                filename TEXT NOT NULL,
                file_type TEXT,
                file_hash TEXT,
                chunk_count INTEGER DEFAULT 0,
                embedding_model TEXT,
                created_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        self.execute("CREATE INDEX idx_documents_user_id ON documents(user_id)")
        self.execute("CREATE INDEX idx_documents_file_hash ON documents(file_hash)")

    def _migration_005_create_chunks(self):
        """Create chunks table for document embeddings"""
        self.execute("""
            CREATE TABLE chunks (
                id TEXT PRIMARY KEY,
                document_id TEXT NOT NULL,
                chunk_index INTEGER NOT NULL,
                content TEXT NOT NULL,
                embedding TEXT,
                FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
            )
        """)
        self.execute("CREATE INDEX idx_chunks_document_id ON chunks(document_id)")

    def _migration_006_remove_tts_columns(self):
        """Remove deprecated TTS columns from user_settings"""
        # SQLite doesn't support DROP COLUMN directly, recreate the table
        self.execute("""
            CREATE TABLE user_settings_new (
                user_id INTEGER PRIMARY KEY,
                model TEXT,
                temperature REAL,
                top_p REAL,
                top_k INTEGER,
                num_ctx INTEGER,
                repeat_penalty REAL,
                persona TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        # Copy data (excluding TTS columns)
        self.execute("""
            INSERT INTO user_settings_new (user_id, model, temperature, top_p, top_k, num_ctx, repeat_penalty, persona)
            SELECT user_id, model, temperature, top_p, top_k, num_ctx, repeat_penalty, persona
            FROM user_settings
        """)

        # Drop old table and rename
        self.execute("DROP TABLE user_settings")
        self.execute("ALTER TABLE user_settings_new RENAME TO user_settings")

    def _migration_007_create_memories(self):
        """Create memories table for user memory storage."""
        self.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                category TEXT DEFAULT 'general',
                importance INTEGER DEFAULT 5,
                embedding TEXT,
                source TEXT DEFAULT 'inferred',
                created_at TEXT,
                last_accessed TEXT,
                access_count INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        self.execute("CREATE INDEX IF NOT EXISTS idx_memories_user_id ON memories(user_id)")
        self.execute("CREATE INDEX IF NOT EXISTS idx_memories_category ON memories(category)")

    def _migration_008_create_mcp_servers(self):
        """Create mcp_servers table for MCP server configurations."""
        self.execute("""
            CREATE TABLE IF NOT EXISTS mcp_servers (
                id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                transport TEXT NOT NULL,
                command TEXT,
                args TEXT,
                url TEXT,
                env TEXT,
                enabled INTEGER DEFAULT 1,
                created_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        self.execute("CREATE INDEX IF NOT EXISTS idx_mcp_servers_user_id ON mcp_servers(user_id)")

    def _migration_009_create_user_profiles(self):
        """Create user_profiles table for user profile system."""
        self.execute("""
            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id INTEGER PRIMARY KEY,
                profile_data TEXT NOT NULL DEFAULT '{}',
                adult_mode_enabled INTEGER DEFAULT 0,
                adult_mode_unlocked_at TEXT,
                created_at TEXT,
                updated_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        self.execute("CREATE INDEX IF NOT EXISTS idx_user_profiles_user_id ON user_profiles(user_id)")

    def _migration_010_add_full_unlock_columns(self):
        """Add full_unlock_enabled and full_unlock_at columns to user_profiles.

        This enforces the two-tier unlock system:
        - Tier 1 (adult_mode_enabled): Unlocked via passcode 6060 in Settings
        - Tier 2 (full_unlock_enabled): Unlocked via /full_unlock command in chat

        Migration also auto-enables full_unlock for existing users who already have
        all sensitive sections enabled AND adult_mode_enabled=True.
        """
        # Add the new columns
        self.execute("""
            ALTER TABLE user_profiles
            ADD COLUMN full_unlock_enabled INTEGER DEFAULT 0
        """)
        self.execute("""
            ALTER TABLE user_profiles
            ADD COLUMN full_unlock_at TEXT
        """)

        # Auto-migrate existing users who have adult_mode + all sensitive sections enabled
        rows = self.fetchall("""
            SELECT user_id, profile_data, adult_mode_enabled
            FROM user_profiles
            WHERE adult_mode_enabled = 1
        """)

        import json
        from datetime import datetime

        for row in rows:
            try:
                profile_data = json.loads(row["profile_data"])
                sensitive_sections = ["sexual_romantic", "dark_content", "private_self", "substances_health"]
                all_enabled = all(
                    profile_data.get(section, {}).get("enabled", False)
                    for section in sensitive_sections
                )

                if all_enabled:
                    now = datetime.utcnow().isoformat() + "Z"
                    self.execute(
                        """UPDATE user_profiles
                           SET full_unlock_enabled = 1, full_unlock_at = ?
                           WHERE user_id = ?""",
                        (now, row["user_id"])
                    )
                    logger.info(f"Auto-migrated full_unlock for user {row['user_id']}")
            except Exception as e:
                logger.warning(f"Failed to check user {row['user_id']} for full_unlock migration: {e}")

    def close(self):
        """Close the database connection"""
        if hasattr(_local, 'connection') and _local.connection is not None:
            _local.connection.close()
            _local.connection = None


# Global database instance (initialized lazily)
_db_instance: Optional[DatabaseService] = None


def get_database() -> DatabaseService:
    """Get the global database instance"""
    global _db_instance
    if _db_instance is None:
        from app.config import DATABASE_PATH
        _db_instance = DatabaseService(DATABASE_PATH)
    return _db_instance


def init_database(db_path: str) -> DatabaseService:
    """Initialize the database with a specific path"""
    global _db_instance
    _db_instance = DatabaseService(db_path)
    return _db_instance
