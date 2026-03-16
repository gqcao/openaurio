"""
Conversation Logger

Logs all conversations for analytics and user behavior analysis.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class ConversationEntry:
    """A single conversation turn."""
    timestamp: str
    user_id: str
    user_name: str
    user_message: str
    vera_response: str
    is_voice: bool
    scenario: Optional[str]
    level: str
    xp: int
    achievements_unlocked: list
    session_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ConversationLogger:
    """Logs conversations to JSONL files for analytics."""
    
    def __init__(self, base_dir: Optional[str] = None):
        if base_dir is None:
            # Default to memory/conversations directory
            base_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                "memory",
                "conversations"
            )
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Main conversation file (all conversations)
        self.conversations_file = self.base_dir / "all_conversations.jsonl"
        
    def log_conversation(
        self,
        user_id: str,
        user_name: str,
        user_message: str,
        vera_response: str,
        is_voice: bool = False,
        scenario: Optional[str] = None,
        level: str = "A1",
        xp: int = 0,
        achievements_unlocked: Optional[list] = None,
        session_id: Optional[str] = None,
    ) -> bool:
        """
        Log a conversation turn.
        
        Args:
            user_id: Telegram chat ID
            user_name: User's name
            user_message: What the user said
            vera_response: Vera's response
            is_voice: Whether user message was voice
            scenario: Current scenario (if any)
            level: User's current level
            xp: User's current XP
            achievements_unlocked: List of achievements unlocked
            session_id: Session identifier
            
        Returns:
            True if logged successfully
        """
        entry = ConversationEntry(
            timestamp=datetime.now().isoformat(),
            user_id=user_id,
            user_name=user_name,
            user_message=user_message,
            vera_response=vera_response,
            is_voice=is_voice,
            scenario=scenario,
            level=level,
            xp=xp,
            achievements_unlocked=achievements_unlocked or [],
            session_id=session_id,
        )
        
        try:
            # Append to main file
            with open(self.conversations_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry.to_dict(), ensure_ascii=False) + "\n")
            
            # Also write to user-specific file
            user_file = self.base_dir / f"user_{user_id}.jsonl"
            with open(user_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry.to_dict(), ensure_ascii=False) + "\n")
            
            return True
        except Exception as e:
            print(f"Error logging conversation: {e}")
            return False
    
    def get_all_conversations(self) -> list:
        """Get all conversation entries."""
        if not self.conversations_file.exists():
            return []
        
        conversations = []
        with open(self.conversations_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    conversations.append(json.loads(line))
        return conversations
    
    def get_user_conversations(self, user_id: str) -> list:
        """Get conversations from a specific user."""
        user_file = self.base_dir / f"user_{user_id}.jsonl"
        if not user_file.exists():
            return []
        
        conversations = []
        with open(user_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    conversations.append(json.loads(line))
        return conversations
    
    def get_conversation_count(self) -> int:
        """Get total number of conversation turns."""
        return len(self.get_all_conversations())
    
    def get_recent_conversations(self, limit: int = 20) -> list:
        """Get most recent conversation entries."""
        all_conversations = self.get_all_conversations()
        return all_conversations[-limit:] if all_conversations else []