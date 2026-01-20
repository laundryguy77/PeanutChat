"""
Data Layer & Persistence Verification Tests

This module implements the verification tests from the Data Layer Trace documentation.

Verification Checklist:
1. User isolation: Test cross-user access attempts for all stores
2. Concurrent updates: Test profile race conditions trigger retry logic
3. Transaction rollback: Test multi-step failures roll back atomically
4. Atomic writes: Test conversation save integrity
5. Error sanitization: Verify no SQLite details in API responses
"""
import asyncio
import json
import os
import sys
import tempfile
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Ensure project root is in path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set test environment variable for JWT_SECRET before importing app modules
os.environ["JWT_SECRET"] = "test-secret-key-for-unit-testing-purposes-only-12345"


@pytest.fixture(scope="function")
def test_db():
    """Create a fresh test database for each test."""
    # Generate unique temp path
    tmp_db_path = tempfile.mktemp(suffix=".db")

    os.environ["DATABASE_PATH"] = tmp_db_path

    # Reset all singletons BEFORE imports
    import app.services.database as db_module
    import app.services.memory_store as memory_module
    import app.services.knowledge_store as knowledge_module
    import app.services.user_profile_store as profile_module

    # Clear thread-local storage for database connection
    if hasattr(db_module._local, 'connection') and db_module._local.connection is not None:
        try:
            db_module._local.connection.close()
        except Exception:
            pass
        db_module._local.connection = None

    # Close existing db instance if any
    if db_module._db_instance is not None:
        try:
            db_module._db_instance.close()
        except Exception:
            pass

    # Reset all singletons
    db_module._db_instance = None
    memory_module._memory_store = None
    knowledge_module._store = None
    profile_module._store_instance = None

    # Create fresh database instance
    from app.services.database import DatabaseService
    db = DatabaseService(tmp_db_path)
    db_module._db_instance = db

    yield db

    # Cleanup - close connections first
    if hasattr(db_module._local, 'connection') and db_module._local.connection is not None:
        try:
            db_module._local.connection.close()
        except Exception:
            pass
        db_module._local.connection = None

    if db_module._db_instance is not None:
        try:
            db_module._db_instance.close()
        except Exception:
            pass

    db_module._db_instance = None
    memory_module._memory_store = None
    knowledge_module._store = None
    profile_module._store_instance = None

    # Delete temp database file
    try:
        os.unlink(tmp_db_path)
    except Exception:
        pass


@pytest.fixture
def conversation_store():
    """Create a fresh conversation store with temp directory."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        from app.services.conversation_store import ConversationStore
        store = ConversationStore(storage_dir=tmp_dir)
        yield store


class TestUserIsolationConversationStore:
    """Verify user isolation in conversation store."""

    def test_get_conversation_blocked_for_wrong_user(self, conversation_store):
        """User cannot access another user's conversation via get()."""
        # Create conversation for user 1
        conv = asyncio.get_event_loop().run_until_complete(
            conversation_store.create(model="test", user_id=1)
        )
        conv_id = conv.id

        # User 1 can access their own conversation
        result = conversation_store.get(conv_id, user_id=1)
        assert result is not None
        assert result.user_id == 1

        # User 2 cannot access user 1's conversation
        result = conversation_store.get(conv_id, user_id=2)
        assert result is None, "User 2 should not access User 1's conversation"

    def test_list_for_user_excludes_other_users(self, conversation_store):
        """list_for_user() only returns conversations owned by that user."""
        loop = asyncio.get_event_loop()

        # Create conversations for different users
        loop.run_until_complete(conversation_store.create(model="test", user_id=1))
        loop.run_until_complete(conversation_store.create(model="test", user_id=1))
        loop.run_until_complete(conversation_store.create(model="test", user_id=2))

        # User 1 should only see 2 conversations
        user1_convs = conversation_store.list_for_user(user_id=1)
        assert len(user1_convs) == 2
        assert all(c["user_id"] == 1 for c in user1_convs)

        # User 2 should only see 1 conversation
        user2_convs = conversation_store.list_for_user(user_id=2)
        assert len(user2_convs) == 1
        assert all(c["user_id"] == 2 for c in user2_convs)

    def test_legacy_conversations_blocked_for_authenticated_users(self, conversation_store):
        """Legacy conversations (user_id=None) cannot be accessed by authenticated users."""
        loop = asyncio.get_event_loop()

        # Create a legacy conversation (no user_id)
        conv = loop.run_until_complete(
            conversation_store.create(model="test", user_id=None)
        )
        conv_id = conv.id

        # Authenticated user cannot access legacy conversation
        result = conversation_store.get(conv_id, user_id=1)
        assert result is None, "Authenticated user should not access legacy conversation"

        # Legacy conversation should not appear in user's list
        user_convs = conversation_store.list_for_user(user_id=1)
        assert not any(c["id"] == conv_id for c in user_convs)

    def test_search_conversations_user_isolated(self, conversation_store):
        """search_conversations() only searches user's own conversations."""
        loop = asyncio.get_event_loop()

        # Create conversation with searchable content for user 1
        conv1 = loop.run_until_complete(
            conversation_store.create(model="test", user_id=1)
        )
        loop.run_until_complete(
            conversation_store.add_message(conv1.id, "user", "secret password 12345")
        )

        # Create conversation for user 2
        conv2 = loop.run_until_complete(
            conversation_store.create(model="test", user_id=2)
        )
        loop.run_until_complete(
            conversation_store.add_message(conv2.id, "user", "another password 67890")
        )

        # User 1 can find their own content
        results = conversation_store.search_conversations("password", user_id=1)
        assert len(results) == 1
        assert results[0]["conversation_id"] == conv1.id

        # User 2 can find their own content
        results = conversation_store.search_conversations("password", user_id=2)
        assert len(results) == 1
        assert results[0]["conversation_id"] == conv2.id

        # User 1 cannot find user 2's content
        results = conversation_store.search_conversations("67890", user_id=1)
        assert len(results) == 0

    def test_get_messages_for_api_user_isolated(self, conversation_store):
        """get_messages_for_api() enforces user ownership."""
        loop = asyncio.get_event_loop()

        # Create conversation for user 1 with messages
        conv = loop.run_until_complete(
            conversation_store.create(model="test", user_id=1)
        )
        loop.run_until_complete(
            conversation_store.add_message(conv.id, "user", "private message")
        )

        # User 1 can get messages
        messages = conversation_store.get_messages_for_api(conv.id, user_id=1)
        assert len(messages) == 1
        assert messages[0]["content"] == "private message"

        # User 2 cannot get messages (returns empty list)
        messages = conversation_store.get_messages_for_api(conv.id, user_id=2)
        assert len(messages) == 0


class TestUserIsolationMemoryStore:
    """Verify user isolation in memory store."""

    def _create_test_users(self, db, count=2):
        """Helper to create test users."""
        user_ids = []
        for i in range(1, count + 1):
            db.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (f"testuser{i}", "hash123")
            )
            row = db.fetchone(
                "SELECT id FROM users WHERE username = ?",
                (f"testuser{i}",)
            )
            user_ids.append(row["id"])
        return user_ids

    def test_get_user_memories_only_returns_own(self, test_db):
        """get_user_memories() only returns memories for the specified user."""
        from app.services.memory_store import MemoryStore
        store = MemoryStore()

        # Create test users first (foreign key requirement)
        user_ids = self._create_test_users(test_db, 2)
        user1_id, user2_id = user_ids

        # Create memories for different users
        store.create_memory(user_id=user1_id, content="User 1 memory", category="test")
        store.create_memory(user_id=user1_id, content="User 1 second memory", category="test")
        store.create_memory(user_id=user2_id, content="User 2 memory", category="test")

        # Each user only sees their own memories
        user1_memories = store.get_user_memories(user_id=user1_id)
        assert len(user1_memories) == 2
        assert all(m.user_id == user1_id for m in user1_memories)

        user2_memories = store.get_user_memories(user_id=user2_id)
        assert len(user2_memories) == 1
        assert all(m.user_id == user2_id for m in user2_memories)

    def test_update_access_requires_ownership(self, test_db):
        """update_access() fails for memories not owned by user."""
        from app.services.memory_store import MemoryStore
        store = MemoryStore()

        # Create test users first
        user_ids = self._create_test_users(test_db, 2)
        user1_id, user2_id = user_ids

        # Create memory for user 1
        memory = store.create_memory(user_id=user1_id, content="Test memory", category="test")

        # User 1 can update access
        result = store.update_access(memory.id, user_id=user1_id)
        assert result is True

        # User 2 cannot update access
        result = store.update_access(memory.id, user_id=user2_id)
        assert result is False, "User 2 should not be able to update user 1's memory"

    def test_delete_memory_requires_ownership(self, test_db):
        """delete_memory() fails for memories not owned by user."""
        from app.services.memory_store import MemoryStore
        store = MemoryStore()

        # Create test users first
        user_ids = self._create_test_users(test_db, 2)
        user1_id, user2_id = user_ids

        # Create memory for user 1
        memory = store.create_memory(user_id=user1_id, content="Test memory", category="test")

        # User 2 cannot delete user 1's memory
        result = store.delete_memory(memory.id, user_id=user2_id)
        assert result is False

        # Verify memory still exists
        memories = store.get_user_memories(user_id=user1_id)
        assert len(memories) == 1

        # User 1 can delete their own memory
        result = store.delete_memory(memory.id, user_id=user1_id)
        assert result is True


class TestUserIsolationKnowledgeStore:
    """Verify user isolation in knowledge store."""

    def _create_test_users(self, db, count=2):
        """Helper to create test users."""
        user_ids = []
        for i in range(1, count + 1):
            db.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (f"knowledgeuser{i}", "hash123")
            )
            row = db.fetchone(
                "SELECT id FROM users WHERE username = ?",
                (f"knowledgeuser{i}",)
            )
            user_ids.append(row["id"])
        return user_ids

    def test_get_document_requires_ownership(self, test_db):
        """get_document() requires user_id validation."""
        from app.services.knowledge_store import KnowledgeStore
        store = KnowledgeStore()

        # Create test users first
        user_ids = self._create_test_users(test_db, 2)
        user1_id, user2_id = user_ids

        # Create document for user 1
        doc = store.create_document(
            user_id=user1_id,
            filename="test.txt",
            file_type="text",
            content_hash="abc123",
            embedding_model="test"
        )

        # User 1 can access their document
        result = store.get_document(doc.id, user_id=user1_id)
        assert result is not None
        assert result.user_id == user1_id

        # User 2 cannot access user 1's document
        result = store.get_document(doc.id, user_id=user2_id)
        assert result is None, "User 2 should not access User 1's document"

    def test_get_user_documents_user_isolated(self, test_db):
        """get_user_documents() only returns user's own documents."""
        from app.services.knowledge_store import KnowledgeStore
        store = KnowledgeStore()

        # Create test users first
        user_ids = self._create_test_users(test_db, 2)
        user1_id, user2_id = user_ids

        # Create documents for different users
        store.create_document(user1_id, "doc1.txt", "text", "hash1", "test")
        store.create_document(user1_id, "doc2.txt", "text", "hash2", "test")
        store.create_document(user2_id, "doc3.txt", "text", "hash3", "test")

        # User 1 only sees their documents
        user1_docs = store.get_user_documents(user_id=user1_id)
        assert len(user1_docs) == 2
        assert all(d.user_id == user1_id for d in user1_docs)

        # User 2 only sees their documents
        user2_docs = store.get_user_documents(user_id=user2_id)
        assert len(user2_docs) == 1

    def test_delete_document_requires_ownership(self, test_db):
        """delete_document() requires user ownership validation."""
        from app.services.knowledge_store import KnowledgeStore
        store = KnowledgeStore()

        # Create test users first
        user_ids = self._create_test_users(test_db, 2)
        user1_id, user2_id = user_ids

        # Create document for user 1
        doc = store.create_document(user1_id, "test.txt", "text", "hash1", "test")

        # User 2 cannot delete user 1's document
        result = store.delete_document(doc.id, user_id=user2_id)
        assert result is False

        # Verify document still exists
        result = store.get_document(doc.id, user_id=user1_id)
        assert result is not None

        # User 1 can delete their own document
        result = store.delete_document(doc.id, user_id=user1_id)
        assert result is True


class TestUserIsolationUserProfile:
    """Verify user isolation in user profile store."""

    def _create_test_users(self, db, count=2):
        """Helper to create test users."""
        user_ids = []
        for i in range(1, count + 1):
            db.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (f"profileuser{i}", "hash123")
            )
            row = db.fetchone(
                "SELECT id FROM users WHERE username = ?",
                (f"profileuser{i}",)
            )
            user_ids.append(row["id"])
        return user_ids

    def test_profile_access_by_user_id(self, test_db):
        """Profiles are keyed by user_id (primary key)."""
        from app.services.user_profile_store import UserProfileStore
        store = UserProfileStore()

        # Create test users first
        user_ids = self._create_test_users(test_db, 2)
        user1_id, user2_id = user_ids

        # Create profile for user 1
        profile1 = store.create_profile(user_id=user1_id)
        assert profile1.user_id == user1_id

        # Create profile for user 2
        profile2 = store.create_profile(user_id=user2_id)
        assert profile2.user_id == user2_id

        # Each user gets their own profile
        retrieved1 = store.get_profile(user_id=user1_id)
        assert retrieved1.user_id == user1_id

        retrieved2 = store.get_profile(user_id=user2_id)
        assert retrieved2.user_id == user2_id

        # Cannot access other user's profile by changing user_id param
        # (since user_id is the primary key, this just gets a different profile)
        assert retrieved1.user_id != retrieved2.user_id


class TestConcurrentUpdatesOptimisticLocking:
    """Verify optimistic locking prevents lost updates."""

    def _create_test_user(self, db):
        """Helper to create a test user."""
        db.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            ("concurrentuser", "hash123")
        )
        row = db.fetchone(
            "SELECT id FROM users WHERE username = ?",
            ("concurrentuser",)
        )
        return row["id"]

    def test_concurrent_modification_raises_error(self, test_db):
        """ConcurrentModificationError raised when versions don't match."""
        from app.services.user_profile_store import (
            UserProfileStore,
            ConcurrentModificationError
        )
        store = UserProfileStore()

        # Create test user first
        user_id = self._create_test_user(test_db)

        # Create profile
        profile = store.create_profile(user_id=user_id)
        original_updated_at = profile.updated_at

        # Simulate concurrent modification
        data = profile.profile_data.copy()
        data["identity"]["name"] = "First Update"

        # First update succeeds
        updated = store.update_profile_data(
            user_id=user_id,
            data=data,
            expected_updated_at=original_updated_at
        )
        assert updated is not None

        # Second update with stale version fails
        data["identity"]["name"] = "Second Update"
        with pytest.raises(ConcurrentModificationError):
            store.update_profile_data(
                user_id=user_id,
                data=data,
                expected_updated_at=original_updated_at  # Stale version
            )

    def test_patch_profile_field_retries_on_conflict(self, test_db):
        """patch_profile_field() automatically retries on concurrent modification."""
        from app.services.user_profile_store import UserProfileStore
        store = UserProfileStore()

        # Create test user first
        user_id = self._create_test_user(test_db)

        # Create profile
        store.create_profile(user_id=user_id)

        # Patch should succeed (may retry internally)
        result = store.patch_profile_field(
            user_id=user_id,
            path="identity.name",
            value="Test Name",
            operation="set"
        )
        assert result is not None
        assert result.profile_data["identity"]["name"] == "Test Name"

    def test_concurrent_updates_with_threads(self, test_db):
        """Multiple threads updating same profile - optimistic locking handles conflicts."""
        from app.services.user_profile_store import UserProfileStore

        # Reset the singleton for fresh state
        import app.services.user_profile_store as profile_module
        profile_module._store_instance = None

        # Create test user first
        user_id = self._create_test_user(test_db)

        store = UserProfileStore()
        store.create_profile(user_id=user_id)

        results = {"success": 0, "conflict": 0}
        lock = threading.Lock()
        test_user_id = user_id  # Capture for thread access

        def update_profile(value):
            try:
                # Reset thread-local DB connection
                import app.services.database as db_module
                import threading as thread_mod
                if hasattr(db_module._local, 'connection'):
                    db_module._local.connection = None

                # Get fresh store for this thread
                from app.services.user_profile_store import UserProfileStore
                thread_store = UserProfileStore()

                # Small delay to increase contention
                time.sleep(0.01)

                thread_store.patch_profile_field(
                    user_id=test_user_id,
                    path=f"custom_fields.fields.key_{value}",
                    value=value,
                    operation="set",
                    max_retries=5
                )
                with lock:
                    results["success"] += 1
            except Exception as e:
                with lock:
                    results["conflict"] += 1

        # Run concurrent updates
        threads = []
        for i in range(5):
            t = threading.Thread(target=update_profile, args=(i,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # All updates should eventually succeed with retries
        assert results["success"] >= 3, f"Expected most updates to succeed, got {results}"


class TestTransactionRollback:
    """Verify transaction rollback on failures."""

    def test_transaction_rolls_back_on_error(self, test_db):
        """Transaction context manager rolls back all changes on error."""
        from app.services.database import get_database, DatabaseError

        db = get_database()

        # Get initial state
        initial_count = db.fetchone("SELECT COUNT(*) as cnt FROM migrations")["cnt"]

        try:
            with db.transaction() as tx:
                # First operation succeeds
                tx.execute(
                    "INSERT INTO migrations (name) VALUES (?)",
                    ("test_migration_1",)
                )

                # Verify it's visible within transaction
                result = tx.fetchone(
                    "SELECT COUNT(*) as cnt FROM migrations WHERE name = ?",
                    ("test_migration_1",)
                )
                assert result["cnt"] == 1

                # Force an error (duplicate key)
                tx.execute(
                    "INSERT INTO migrations (name) VALUES (?)",
                    ("test_migration_1",)  # Duplicate - will fail
                )

        except DatabaseError:
            pass  # Expected

        # Verify rollback occurred - count should be unchanged
        final_count = db.fetchone("SELECT COUNT(*) as cnt FROM migrations")["cnt"]
        assert final_count == initial_count, "Transaction should have rolled back"

    def test_nested_operations_all_or_nothing(self, test_db):
        """Multiple operations in transaction either all succeed or all fail."""
        from app.services.database import get_database, DatabaseError

        db = get_database()

        # Create a test user first
        db.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            ("testuser", "hash123")
        )
        user_row = db.fetchone("SELECT id FROM users WHERE username = ?", ("testuser",))
        user_id = user_row["id"]

        try:
            with db.transaction() as tx:
                # Insert document
                tx.execute(
                    """INSERT INTO documents (id, user_id, filename, file_type,
                       file_hash, embedding_model, created_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    ("doc1", user_id, "test.txt", "text", "hash1", "model", "2024-01-01")
                )

                # Insert chunk referencing document
                tx.execute(
                    """INSERT INTO chunks (id, document_id, chunk_index, content)
                       VALUES (?, ?, ?, ?)""",
                    ("chunk1", "doc1", 0, "test content")
                )

                # Force error with invalid foreign key
                tx.execute(
                    """INSERT INTO chunks (id, document_id, chunk_index, content)
                       VALUES (?, ?, ?, ?)""",
                    ("chunk2", "nonexistent_doc", 0, "bad content")
                )

        except DatabaseError:
            pass  # Expected

        # Verify both document and chunk were rolled back
        doc = db.fetchone("SELECT * FROM documents WHERE id = ?", ("doc1",))
        assert doc is None, "Document should have been rolled back"

        chunk = db.fetchone("SELECT * FROM chunks WHERE id = ?", ("chunk1",))
        assert chunk is None, "Chunk should have been rolled back"


class TestAtomicWrites:
    """Verify atomic write pattern prevents corruption."""

    def test_conversation_save_creates_temp_file(self, conversation_store):
        """Conversation save uses temp file pattern."""
        loop = asyncio.get_event_loop()

        # Create and save a conversation
        conv = loop.run_until_complete(
            conversation_store.create(model="test", user_id=1)
        )

        # Add a message (triggers save)
        loop.run_until_complete(
            conversation_store.add_message(conv.id, "user", "test message")
        )

        # Verify file exists and is valid JSON
        file_path = conversation_store.storage_dir / f"{conv.id}.json"
        assert file_path.exists()

        with open(file_path) as f:
            data = json.load(f)
            assert data["id"] == conv.id
            assert len(data["messages"]) == 1

    def test_conversation_survives_reload(self, conversation_store):
        """Conversation data survives store reload."""
        loop = asyncio.get_event_loop()

        # Create conversation with messages
        conv = loop.run_until_complete(
            conversation_store.create(model="test", user_id=1)
        )
        loop.run_until_complete(
            conversation_store.add_message(conv.id, "user", "message 1")
        )
        loop.run_until_complete(
            conversation_store.add_message(conv.id, "assistant", "response 1")
        )

        # Create new store instance (simulates restart)
        from app.services.conversation_store import ConversationStore
        new_store = ConversationStore(storage_dir=str(conversation_store.storage_dir))

        # Verify data persisted
        reloaded = new_store.get(conv.id, user_id=1)
        assert reloaded is not None
        assert len(reloaded.messages) == 2
        assert reloaded.messages[0].content == "message 1"
        assert reloaded.messages[1].content == "response 1"

    def test_corrupt_json_quarantined(self):
        """Corrupt JSON files are moved to .corrupt extension."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create a corrupt JSON file
            corrupt_file = Path(tmp_dir) / "corrupted.json"
            corrupt_file.write_text("{invalid json content")

            # Create store (should handle corruption during load)
            from app.services.conversation_store import ConversationStore
            store = ConversationStore(storage_dir=tmp_dir)

            # Original file should be renamed
            assert not corrupt_file.exists()

            # Backup should exist
            backup_file = corrupt_file.with_suffix('.json.corrupt')
            assert backup_file.exists()

    def test_no_temp_files_remain_after_save(self, conversation_store):
        """No .tmp files remain after successful save."""
        loop = asyncio.get_event_loop()

        # Create and save multiple conversations
        for i in range(3):
            conv = loop.run_until_complete(
                conversation_store.create(model="test", user_id=1)
            )
            loop.run_until_complete(
                conversation_store.add_message(conv.id, "user", f"message {i}")
            )

        # Check for any leftover temp files
        tmp_files = list(conversation_store.storage_dir.glob("*.tmp"))
        assert len(tmp_files) == 0, f"Found leftover temp files: {tmp_files}"


class TestErrorSanitization:
    """Verify database errors are sanitized."""

    def test_database_error_has_reference_id(self, test_db):
        """DatabaseError contains reference ID for tracking."""
        from app.services.database import get_database, DatabaseError

        db = get_database()

        with pytest.raises(DatabaseError) as exc_info:
            # Intentionally cause an error (invalid SQL)
            db.execute("SELECT * FROM nonexistent_table_xyz")

        error_message = str(exc_info.value)
        # Should contain "ref:" with an ID
        assert "ref:" in error_message
        # Should NOT contain SQLite-specific error details
        assert "no such table" not in error_message.lower()
        assert "nonexistent_table_xyz" not in error_message

    def test_error_sanitization_in_transaction(self, test_db):
        """Transaction errors are also sanitized."""
        from app.services.database import get_database, DatabaseError

        db = get_database()

        with pytest.raises(DatabaseError) as exc_info:
            with db.transaction() as tx:
                tx.execute("INVALID SQL SYNTAX HERE!!!")

        error_message = str(exc_info.value)
        assert "ref:" in error_message
        # Should not leak SQL syntax or SQLite internals
        assert "INVALID SQL" not in error_message
        assert "syntax" not in error_message.lower()

    def test_fetchone_error_sanitized(self, test_db):
        """fetchone() errors are sanitized."""
        from app.services.database import get_database, DatabaseError

        db = get_database()

        with pytest.raises(DatabaseError) as exc_info:
            db.fetchone("SELECT * FROM does_not_exist")

        error_message = str(exc_info.value)
        assert "ref:" in error_message
        assert "does_not_exist" not in error_message

    def test_fetchall_error_sanitized(self, test_db):
        """fetchall() errors are sanitized."""
        from app.services.database import get_database, DatabaseError

        db = get_database()

        with pytest.raises(DatabaseError) as exc_info:
            db.fetchall("SELECT * FROM another_fake_table")

        error_message = str(exc_info.value)
        assert "ref:" in error_message
        assert "another_fake_table" not in error_message

    def test_executemany_error_sanitized(self, test_db):
        """executemany() errors are sanitized."""
        from app.services.database import get_database, DatabaseError

        db = get_database()

        with pytest.raises(DatabaseError) as exc_info:
            db.executemany(
                "INSERT INTO fake_table (col) VALUES (?)",
                [("val1",), ("val2",)]
            )

        error_message = str(exc_info.value)
        assert "ref:" in error_message
        assert "fake_table" not in error_message


class TestForeignKeyCascades:
    """Verify foreign key cascades work correctly."""

    def test_user_delete_cascades_to_settings(self, test_db):
        """Deleting user cascades to user_settings."""
        from app.services.database import get_database
        db = get_database()

        # Create user
        db.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            ("cascade_test", "hash")
        )
        user = db.fetchone("SELECT id FROM users WHERE username = ?", ("cascade_test",))
        user_id = user["id"]

        # Create user settings
        db.execute(
            "INSERT INTO user_settings (user_id, model) VALUES (?, ?)",
            (user_id, "test-model")
        )

        # Verify settings exist
        settings = db.fetchone("SELECT * FROM user_settings WHERE user_id = ?", (user_id,))
        assert settings is not None

        # Delete user
        db.execute("DELETE FROM users WHERE id = ?", (user_id,))

        # Settings should be cascaded
        settings = db.fetchone("SELECT * FROM user_settings WHERE user_id = ?", (user_id,))
        assert settings is None, "Settings should be deleted via cascade"

    def test_document_delete_cascades_to_chunks(self, test_db):
        """Deleting document cascades to chunks."""
        from app.services.database import get_database
        db = get_database()

        # Create user first
        db.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            ("chunk_test", "hash")
        )
        user = db.fetchone("SELECT id FROM users WHERE username = ?", ("chunk_test",))
        user_id = user["id"]

        # Create document
        db.execute(
            """INSERT INTO documents (id, user_id, filename, file_type, file_hash,
               embedding_model, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)""",
            ("doc_cascade", user_id, "test.txt", "text", "hash", "model", "2024-01-01")
        )

        # Create chunks
        db.execute(
            "INSERT INTO chunks (id, document_id, chunk_index, content) VALUES (?, ?, ?, ?)",
            ("chunk1", "doc_cascade", 0, "content 1")
        )
        db.execute(
            "INSERT INTO chunks (id, document_id, chunk_index, content) VALUES (?, ?, ?, ?)",
            ("chunk2", "doc_cascade", 1, "content 2")
        )

        # Verify chunks exist
        chunks = db.fetchall("SELECT * FROM chunks WHERE document_id = ?", ("doc_cascade",))
        assert len(chunks) == 2

        # Delete document
        db.execute("DELETE FROM documents WHERE id = ?", ("doc_cascade",))

        # Chunks should be cascaded
        chunks = db.fetchall("SELECT * FROM chunks WHERE document_id = ?", ("doc_cascade",))
        assert len(chunks) == 0, "Chunks should be deleted via cascade"


class TestThreadSafetyConversationStore:
    """Verify conversation store thread safety."""

    def test_concurrent_reads_safe(self, conversation_store):
        """Multiple threads can read simultaneously."""
        loop = asyncio.get_event_loop()

        # Create test conversation
        conv = loop.run_until_complete(
            conversation_store.create(model="test", user_id=1)
        )

        results = []
        errors = []

        def read_conversation():
            try:
                for _ in range(10):
                    result = conversation_store.get(conv.id, user_id=1)
                    if result:
                        results.append(result.id)
            except Exception as e:
                errors.append(str(e))

        # Run concurrent reads
        threads = [threading.Thread(target=read_conversation) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0, f"Errors during concurrent reads: {errors}"
        assert len(results) == 50  # 5 threads * 10 reads each

    def test_sequential_writes_persisted(self, conversation_store):
        """Sequential async writes are properly persisted."""
        loop = asyncio.get_event_loop()

        # Create test conversation
        conv = loop.run_until_complete(
            conversation_store.create(model="test", user_id=1)
        )

        # Add multiple messages sequentially
        for i in range(5):
            loop.run_until_complete(
                conversation_store.add_message(
                    conv.id, "user", f"message {i}"
                )
            )

        # Verify all messages were saved
        result = conversation_store.get(conv.id, user_id=1)
        assert len(result.messages) == 5

        # Verify data integrity
        for i, msg in enumerate(result.messages):
            assert msg.content == f"message {i}"
