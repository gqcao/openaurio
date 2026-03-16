"""
Feedback Logger

Collects and stores user feedback from the Telegram bot.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class FeedbackEntry:
    """A single feedback entry."""
    timestamp: str
    user_id: str
    user_name: str
    feedback_text: str
    level: str
    xp: int
    scenario: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class FeedbackLogger:
    """Logs user feedback to JSONL files."""
    
    def __init__(self, base_dir: Optional[str] = None):
        if base_dir is None:
            # Default to memory/feedback directory
            base_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                "memory",
                "feedback"
            )
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Main feedback file (all feedback)
        self.feedback_file = self.base_dir / "all_feedback.jsonL"
        
    def log_feedback(
        self,
        user_id: str,
        user_name: str,
        feedback_text: str,
        level: str = "A1",
        xp: int = 0,
        scenario: Optional[str] = None,
    ) -> bool:
        """
        Log user feedback.
        
        Args:
            user_id: Telegram chat ID
            user_name: User's name
            feedback_text: The feedback message
            level: User's current level
            xp: User's current XP
            scenario: Current scenario (if any)
            
        Returns:
            True if logged successfully
        """
        entry = FeedbackEntry(
            timestamp=datetime.now().isoformat(),
            user_id=user_id,
            user_name=user_name,
            feedback_text=feedback_text,
            level=level,
            xp=xp,
            scenario=scenario,
        )
        
        try:
            # Append to main file
            with open(self.feedback_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry.to_dict(), ensure_ascii=False) + "\n")
            
            # Also write to user-specific file
            user_file = self.base_dir / f"user_{user_id}.jsonl"
            with open(user_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry.to_dict(), ensure_ascii=False) + "\n")
            
            return True
        except Exception as e:
            print(f"Error logging feedback: {e}")
            return False
    
    def get_all_feedback(self) -> list:
        """Get all feedback entries."""
        if not self.feedback_file.exists():
            return []
        
        feedback = []
        with open(self.feedback_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    feedback.append(json.loads(line))
        return feedback
    
    def get_user_feedback(self, user_id: str) -> list:
        """Get feedback from a specific user."""
        user_file = self.base_dir / f"user_{user_id}.jsonl"
        if not user_file.exists():
            return []
        
        feedback = []
        with open(user_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    feedback.append(json.loads(line))
        return feedback
    
    def get_feedback_count(self) -> int:
        """Get total number of feedback entries."""
        return len(self.get_all_feedback())
    
    def get_recent_feedback(self, limit: int = 10) -> list:
        """Get most recent feedback entries."""
        all_feedback = self.get_all_feedback()
        return all_feedback[-limit:] if all_feedback else []