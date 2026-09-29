"""
Memory Manager for the Multi-Agent Research Platform.

Manages research sessions, user preferences, and context across sessions.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class ResearchSession:
    """Represents a research session."""

    def __init__(
        self,
        session_id: str,
        query: str,
        report: Optional[str] = None,
        quality_scores: Optional[Dict[str, float]] = None,
        citations: Optional[List[Dict[str, Any]]] = None,
        created_at: Optional[str] = None,
    ):
        """Initialize a research session."""
        self.id = session_id
        self.query = query
        self.report = report
        self.quality_scores = quality_scores or {}
        self.citations = citations or []
        self.created_at = created_at or datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary."""
        return {
            "id": self.id,
            "query": self.query,
            "report": self.report,
            "quality_scores": self.quality_scores,
            "citations": self.citations,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ResearchSession":
        """Create session from dictionary."""
        return cls(
            session_id=data["id"],
            query=data["query"],
            report=data.get("report"),
            quality_scores=data.get("quality_scores"),
            citations=data.get("citations", []),
            created_at=data.get("created_at"),
        )


class MemoryManager:
    """
    Manages research sessions and user preferences.

    Features:
    - Save and load research sessions
    - Track user preferences
    - Maintain context across sessions
    - Session history
    """

    def __init__(self, sessions_path: Optional[str] = None):
        """
        Initialize the memory manager.

        Args:
            sessions_path: Path to store sessions (default: data/sessions)
        """
        self.sessions_path = Path(sessions_path or "data/sessions")
        self.sessions_path.mkdir(parents=True, exist_ok=True)

        self.sessions: Dict[str, ResearchSession] = {}
        self.user_preferences: Dict[str, Any] = {}

        # Load existing sessions
        self._load_sessions()

    def create_session(self, query: str) -> ResearchSession:
        """
        Create a new research session.

        Args:
            query: Research query

        Returns:
            New ResearchSession object
        """
        session_id = str(uuid.uuid4())
        session = ResearchSession(session_id=session_id, query=query)
        self.sessions[session_id] = session
        return session

    def save_session(
        self,
        session: ResearchSession,
        report: Optional[str] = None,
        quality_scores: Optional[Dict[str, float]] = None,
        citations: Optional[List[Dict[str, Any]]] = None,
    ):
        """
        Save or update a research session.

        Args:
            session: ResearchSession object
            report: Optional research report
            quality_scores: Optional quality scores
            citations: Optional citations
        """
        if report:
            session.report = report
        if quality_scores:
            session.quality_scores = quality_scores
        if citations:
            session.citations = citations

        session.updated_at = datetime.now().isoformat()
        self.sessions[session.id] = session

        # Save to disk
        self._save_session_to_disk(session)

    def get_session(self, session_id: str) -> Optional[ResearchSession]:
        """
        Get a session by ID.

        Args:
            session_id: Session ID

        Returns:
            ResearchSession or None
        """
        return self.sessions.get(session_id)

    def get_all_sessions(self) -> List[ResearchSession]:
        """Get all sessions."""
        return list(self.sessions.values())

    def get_recent_sessions(self, limit: int = 10) -> List[ResearchSession]:
        """
        Get recent sessions.

        Args:
            limit: Maximum number of sessions to return

        Returns:
            List of recent sessions
        """
        sessions = sorted(
            self.sessions.values(), key=lambda s: s.created_at, reverse=True
        )
        return sessions[:limit]

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.

        Args:
            session_id: Session ID to delete

        Returns:
            True if deleted, False if not found
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            # Delete from disk
            session_file = self.sessions_path / f"{session_id}.json"
            if session_file.exists():
                session_file.unlink()
            return True
        return False

    def set_preference(self, key: str, value: Any):
        """
        Set a user preference.

        Args:
            key: Preference key
            value: Preference value
        """
        self.user_preferences[key] = value
        self._save_preferences()

    def get_preference(self, key: str, default: Any = None) -> Any:
        """
        Get a user preference.

        Args:
            key: Preference key
            default: Default value if not found

        Returns:
            Preference value or default
        """
        return self.user_preferences.get(key, default)

    def _save_session_to_disk(self, session: ResearchSession):
        """Save a session to disk."""
        session_file = self.sessions_path / f"{session.id}.json"
        with open(session_file, "w") as f:
            json.dump(session.to_dict(), f, indent=2)

    def _load_sessions(self):
        """Load all sessions from disk."""
        for session_file in self.sessions_path.glob("*.json"):
            try:
                with open(session_file, "r") as f:
                    data = json.load(f)
                    session = ResearchSession.from_dict(data)
                    self.sessions[session.id] = session
            except Exception as e:
                print(f"Error loading session {session_file}: {e}")

        # Load preferences
        preferences_file = self.sessions_path / "preferences.json"
        if preferences_file.exists():
            try:
                with open(preferences_file, "r") as f:
                    self.user_preferences = json.load(f)
            except Exception as e:
                print(f"Error loading preferences: {e}")

    def _save_preferences(self):
        """Save user preferences to disk."""
        preferences_file = self.sessions_path / "preferences.json"
        with open(preferences_file, "w") as f:
            json.dump(self.user_preferences, f, indent=2)
