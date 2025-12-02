"""Custom SQLite session service for ADK agent persistence.

Implements BaseSessionService interface to provide SQLite-backed session storage
for Alice's Companion agent, enabling session persistence across restarts.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from google.adk.sessions import BaseSessionService, Session, State


class SqliteSessionService(BaseSessionService):
    """SQLite-backed session service for persistent session storage.
    
    Stores session state in a local SQLite database file, enabling
    session persistence across agent restarts.
    """
    
    def __init__(self, db_path: str):
        """Initialize SQLite session service.
        
        Args:
            db_path: Path to SQLite database file (e.g., "companion_sessions.db")
        """
        self.db_path = Path(db_path)
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database with sessions table if it doesn't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                app_name TEXT NOT NULL,
                user_id TEXT NOT NULL,
                session_id TEXT NOT NULL,
                state TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (app_name, user_id, session_id)
            )
        """)
        conn.commit()
        conn.close()
    
    async def create_session(
        self,
        app_name: str,
        user_id: str,
        state: Optional[State] = None,
        session_id: Optional[str] = None
    ) -> Session:
        """Create a new session with optional initial state.
        
        Args:
            app_name: Application name
            user_id: User identifier
            state: Optional initial session state
            session_id: Optional session identifier (auto-generated if not provided)
            
        Returns:
            Created Session object
        """
        if session_id is None:
            import uuid
            session_id = str(uuid.uuid4())
        
        state_dict = state if isinstance(state, dict) else (state.__dict__ if state else {})
        state_json = json.dumps(state_dict)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO sessions (app_name, user_id, session_id, state, updated_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (app_name, user_id, session_id, state_json))
        conn.commit()
        conn.close()
        
        return Session(
            app_name=app_name,
            user_id=user_id,
            id=session_id,
            state=state_dict
        )
    
    async def get_session(
        self,
        app_name: str,
        user_id: str,
        session_id: str
    ) -> Optional[Session]:
        """Retrieve an existing session.
        
        Args:
            app_name: Application name
            user_id: User identifier
            session_id: Session identifier
            
        Returns:
            Session object if found, None otherwise
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT state FROM sessions
            WHERE app_name = ? AND user_id = ? AND session_id = ?
        """, (app_name, user_id, session_id))
        row = cursor.fetchone()
        conn.close()
        
        if row is None:
            return None
        
        state_dict = json.loads(row[0])
        return Session(
            app_name=app_name,
            user_id=user_id,
            id=session_id,
            state=state_dict
        )
    
    async def update_session_state(
        self,
        app_name: str,
        user_id: str,
        session_id: str,
        state: Optional[State] = None
    ) -> None:
        """Update session state.
        
        Args:
            app_name: Application name
            user_id: User identifier
            session_id: Session identifier
            state: New session state (optional, defaults to empty dict if None)
        """
        state_dict = state if isinstance(state, dict) else (state.__dict__ if state else {})
        state_json = json.dumps(state_dict)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE sessions
            SET state = ?, updated_at = CURRENT_TIMESTAMP
            WHERE app_name = ? AND user_id = ? AND session_id = ?
        """, (state_json, app_name, user_id, session_id))
        conn.commit()
        conn.close()
    
    async def list_sessions(
        self,
        app_name: str,
        user_id: str
    ) -> List[Session]:
        """List all sessions for a user.
        
        Args:
            app_name: Application name
            user_id: User identifier
            
        Returns:
            List of Session objects
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT session_id, state FROM sessions
            WHERE app_name = ? AND user_id = ?
        """, (app_name, user_id))
        rows = cursor.fetchall()
        conn.close()
        
        sessions = []
        for row in rows:
            session_id, state_json = row
            state_dict = json.loads(state_json)
            sessions.append(Session(
                app_name=app_name,
                user_id=user_id,
                id=session_id,
                state=state_dict
            ))
        return sessions
    
    async def delete_session(
        self,
        *,
        app_name: str,
        user_id: str,
        session_id: str
    ) -> None:
        """Delete a session.
        
        Args:
            app_name: Application name
            user_id: User identifier
            session_id: Session identifier
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM sessions
            WHERE app_name = ? AND user_id = ? AND session_id = ?
        """, (app_name, user_id, session_id))
        conn.commit()
        conn.close()
    
    async def append_event(
        self,
        session: Session,
        event: Any
    ) -> Any:
        """Append an event to a session.
        
        Note: This is a minimal implementation. For full event tracking,
        a separate events table would be needed.
        
        Args:
            session: Session object
            event: Event to append
            
        Returns:
            The appended event
        """
        # For MVP, we'll just update the session state with event metadata
        # A full implementation would store events in a separate table
        if isinstance(session.state, dict):
            if 'events' not in session.state:
                session.state['events'] = []
            # Store event with proper timestamp and serializable data
            event_data = {
                'type': type(event).__name__,
                'timestamp': datetime.now().isoformat(),
                'data': str(event) if isinstance(event, (str, int, float, bool, type(None))) else repr(event)
            }
            session.state['events'].append(event_data)
            await self.update_session_state(
                session.app_name,
                session.user_id,
                session.id,
                session.state
            )
        return event

