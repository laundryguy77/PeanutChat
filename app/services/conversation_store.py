"""Persistent Conversation Storage"""
import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import threading


@dataclass
class Message:
    id: str
    role: str
    content: str
    images: Optional[List[str]] = None
    tool_calls: Optional[List[Dict]] = None
    timestamp: str = None
    parent_id: Optional[str] = None  # For forking support

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


@dataclass
class Conversation:
    id: str
    title: str
    messages: List[Message]
    created_at: str
    updated_at: str
    model: str = ""
    forked_from: Optional[str] = None  # Parent conversation ID if forked
    fork_point: Optional[str] = None   # Message ID where fork occurred

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "messages": [asdict(m) for m in self.messages],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "model": self.model,
            "forked_from": self.forked_from,
            "fork_point": self.fork_point
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Conversation":
        messages = [Message(**m) for m in data.get("messages", [])]
        return cls(
            id=data["id"],
            title=data.get("title", "New Chat"),
            messages=messages,
            created_at=data.get("created_at", datetime.now().isoformat()),
            updated_at=data.get("updated_at", datetime.now().isoformat()),
            model=data.get("model", ""),
            forked_from=data.get("forked_from"),
            fork_point=data.get("fork_point")
        )


class ConversationStore:
    """Manages persistent conversation storage"""

    def __init__(self, storage_dir: str = "conversations"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        self._lock = threading.Lock()
        self._cache: Dict[str, Conversation] = {}
        self._load_all()

    def _load_all(self):
        """Load all conversations into cache"""
        for file_path in self.storage_dir.glob("*.json"):
            try:
                with open(file_path) as f:
                    data = json.load(f)
                    conv = Conversation.from_dict(data)
                    self._cache[conv.id] = conv
            except Exception as e:
                print(f"Error loading conversation {file_path}: {e}")

    def _save(self, conversation: Conversation):
        """Save a conversation to disk"""
        file_path = self.storage_dir / f"{conversation.id}.json"
        with open(file_path, "w") as f:
            json.dump(conversation.to_dict(), f, indent=2)

    def create(self, model: str = "") -> Conversation:
        """Create a new conversation"""
        with self._lock:
            conv_id = str(uuid.uuid4())[:8]
            now = datetime.now().isoformat()
            conv = Conversation(
                id=conv_id,
                title="New Chat",
                messages=[],
                created_at=now,
                updated_at=now,
                model=model
            )
            self._cache[conv_id] = conv
            self._save(conv)
            return conv

    def get(self, conv_id: str) -> Optional[Conversation]:
        """Get a conversation by ID"""
        return self._cache.get(conv_id)

    def list_all(self) -> List[Dict]:
        """List all conversations (metadata only)"""
        conversations = []
        for conv in sorted(
            self._cache.values(),
            key=lambda c: c.updated_at,
            reverse=True
        ):
            conversations.append({
                "id": conv.id,
                "title": conv.title,
                "created_at": conv.created_at,
                "updated_at": conv.updated_at,
                "message_count": len(conv.messages),
                "model": conv.model,
                "forked_from": conv.forked_from
            })
        return conversations

    def add_message(
        self,
        conv_id: str,
        role: str,
        content: str,
        images: Optional[List[str]] = None,
        tool_calls: Optional[List[Dict]] = None
    ) -> Optional[Message]:
        """Add a message to a conversation"""
        with self._lock:
            conv = self._cache.get(conv_id)
            if not conv:
                return None

            msg = Message(
                id=str(uuid.uuid4())[:8],
                role=role,
                content=content,
                images=images,
                tool_calls=tool_calls
            )
            conv.messages.append(msg)
            conv.updated_at = datetime.now().isoformat()

            # Auto-generate title from first user message
            if conv.title == "New Chat" and role == "user" and content:
                conv.title = content[:50] + ("..." if len(content) > 50 else "")

            self._save(conv)
            return msg

    def update_message(
        self,
        conv_id: str,
        msg_id: str,
        new_content: str
    ) -> Optional[Message]:
        """Update a message's content"""
        with self._lock:
            conv = self._cache.get(conv_id)
            if not conv:
                return None

            for msg in conv.messages:
                if msg.id == msg_id:
                    msg.content = new_content
                    conv.updated_at = datetime.now().isoformat()
                    self._save(conv)
                    return msg
            return None

    def fork_at_message(
        self,
        conv_id: str,
        msg_id: str,
        new_content: str
    ) -> Optional[Conversation]:
        """Fork a conversation at a specific message with new content"""
        with self._lock:
            original = self._cache.get(conv_id)
            if not original:
                return None

            # Find message index
            msg_index = None
            for i, msg in enumerate(original.messages):
                if msg.id == msg_id:
                    msg_index = i
                    break

            if msg_index is None:
                return None

            # Create new conversation with messages up to (not including) the edited message
            now = datetime.now().isoformat()
            new_id = str(uuid.uuid4())[:8]

            # Copy messages up to the fork point
            new_messages = []
            for msg in original.messages[:msg_index]:
                new_msg = Message(
                    id=str(uuid.uuid4())[:8],
                    role=msg.role,
                    content=msg.content,
                    images=msg.images,
                    tool_calls=msg.tool_calls,
                    parent_id=msg.id
                )
                new_messages.append(new_msg)

            # Add the edited message
            edited_msg = Message(
                id=str(uuid.uuid4())[:8],
                role=original.messages[msg_index].role,
                content=new_content,
                images=original.messages[msg_index].images,
                parent_id=msg_id
            )
            new_messages.append(edited_msg)

            new_conv = Conversation(
                id=new_id,
                title=f"Fork: {original.title[:40]}",
                messages=new_messages,
                created_at=now,
                updated_at=now,
                model=original.model,
                forked_from=conv_id,
                fork_point=msg_id
            )

            self._cache[new_id] = new_conv
            self._save(new_conv)
            return new_conv

    def delete(self, conv_id: str) -> bool:
        """Delete a conversation"""
        with self._lock:
            if conv_id not in self._cache:
                return False

            del self._cache[conv_id]
            file_path = self.storage_dir / f"{conv_id}.json"
            if file_path.exists():
                file_path.unlink()
            return True

    def rename(self, conv_id: str, new_title: str) -> bool:
        """Rename a conversation"""
        with self._lock:
            conv = self._cache.get(conv_id)
            if not conv:
                return False

            conv.title = new_title
            conv.updated_at = datetime.now().isoformat()
            self._save(conv)
            return True

    def get_messages_for_api(self, conv_id: str) -> List[Dict[str, Any]]:
        """Get messages in Ollama API format"""
        conv = self._cache.get(conv_id)
        if not conv:
            return []

        messages = []
        for msg in conv.messages:
            m = {"role": msg.role, "content": msg.content}
            if msg.images:
                m["images"] = msg.images
            if msg.tool_calls:
                m["tool_calls"] = msg.tool_calls
            messages.append(m)
        return messages

    def clear_messages(self, conv_id: str) -> bool:
        """Clear all messages from a conversation"""
        with self._lock:
            conv = self._cache.get(conv_id)
            if not conv:
                return False

            conv.messages = []
            conv.title = "New Chat"
            conv.updated_at = datetime.now().isoformat()
            self._save(conv)
            return True

    def search_conversations(self, query: str, exclude_conv_id: str = None, max_results: int = 10) -> List[Dict]:
        """
        Search through all conversations for matching content.
        Returns relevant message excerpts from past conversations.
        """
        results = []
        query_lower = query.lower()
        query_words = query_lower.split()

        for conv_id, conv in self._cache.items():
            # Skip the current conversation
            if conv_id == exclude_conv_id:
                continue

            # Search through messages
            for msg in conv.messages:
                content_lower = msg.content.lower()

                # Check if any query words are in the message
                matches = sum(1 for word in query_words if word in content_lower)

                if matches > 0:
                    # Calculate relevance score (simple word match ratio)
                    score = matches / len(query_words)

                    # Get a snippet around the first match
                    first_word = next((w for w in query_words if w in content_lower), query_words[0])
                    match_pos = content_lower.find(first_word)
                    start = max(0, match_pos - 100)
                    end = min(len(msg.content), match_pos + 200)
                    snippet = msg.content[start:end]
                    if start > 0:
                        snippet = "..." + snippet
                    if end < len(msg.content):
                        snippet = snippet + "..."

                    results.append({
                        "conversation_id": conv_id,
                        "conversation_title": conv.title,
                        "message_role": msg.role,
                        "snippet": snippet,
                        "score": score,
                        "timestamp": msg.timestamp
                    })

        # Sort by score (descending) and limit results
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:max_results]


# Global instance
conversation_store = ConversationStore()
