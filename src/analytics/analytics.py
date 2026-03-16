"""
Analytics

Analyzes user behavior, feedback, and conversation data.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import Counter, defaultdict


class Analytics:
    """Provides analytics on user behavior and feedback."""
    
    def __init__(
        self,
        conversations_dir: Optional[str] = None,
        feedback_dir: Optional[str] = None,
        users_dir: Optional[str] = None,
    ):
        base_dir = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        
        self.conversations_dir = Path(conversations_dir) if conversations_dir else base_dir / "memory" / "conversations"
        self.feedback_dir = Path(feedback_dir) if feedback_dir else base_dir / "memory" / "feedback"
        self.users_dir = Path(users_dir) if users_dir else base_dir / "memory" / "users"
    
    def _load_jsonl(self, filepath: Path) -> List[Dict]:
        """Load a JSONL file."""
        if not filepath.exists():
            return []
        
        data = []
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    data.append(json.loads(line))
        return data
    
    def _load_all_users(self) -> Dict[str, Dict]:
        """Load all user memory files."""
        users = {}
        if not self.users_dir.exists():
            return users
        
        for user_file in self.users_dir.glob("*.json"):
            if user_file.stem != "all_feedback":
                with open(user_file, "r", encoding="utf-8") as f:
                    users[user_file.stem] = json.load(f)
        return users
    
    # ==================== USER METRICS ====================
    
    def get_total_users(self) -> int:
        """Get total number of users."""
        return len(self._load_all_users())
    
    def get_active_users(self, days: int = 7) -> int:
        """Get users active in the last N days."""
        users = self._load_all_users()
        cutoff = datetime.now() - timedelta(days=days)
        
        active = 0
        for user_data in users.values():
            updated_at = user_data.get("updated_at")
            if updated_at:
                try:
                    last_active = datetime.fromisoformat(updated_at)
                    if last_active > cutoff:
                        active += 1
                except:
                    pass
        return active
    
    def get_user_level_distribution(self) -> Dict[str, int]:
        """Get distribution of users by level."""
        users = self._load_all_users()
        levels = Counter(user.get("level", "A1") for user in users.values())
        return dict(levels)
    
    def get_average_xp(self) -> float:
        """Get average XP across all users."""
        users = self._load_all_users()
        if not users:
            return 0.0
        
        total_xp = sum(user.get("xp", 0) for user in users.values())
        return total_xp / len(users)
    
    # ==================== ENGAGEMENT METRICS ====================
    
    def get_total_messages(self) -> int:
        """Get total messages sent."""
        users = self._load_all_users()
        return sum(user.get("total_messages", 0) for user in users.values())
    
    def get_total_voice_messages(self) -> int:
        """Get total voice messages sent."""
        users = self._load_all_users()
        return sum(user.get("voice_messages", 0) for user in users.values())
    
    def get_voice_percentage(self) -> float:
        """Get percentage of messages that are voice."""
        total = self.get_total_messages()
        if total == 0:
            return 0.0
        return (self.get_total_voice_messages() / total) * 100
    
    def get_scenario_completion_rates(self) -> Dict[str, Dict[str, Any]]:
        """Get completion rates for each scenario."""
        users = self._load_all_users()
        
        scenarios = ["fika", "grocery", "apartment"]
        stats = {}
        
        for scenario in scenarios:
            completed = 0
            for user in users.values():
                if scenario in user.get("completed_scenarios", []):
                    completed += 1
            
            stats[scenario] = {
                "completed": completed,
                "total_users": len(users),
                "completion_rate": (completed / len(users) * 100) if users else 0,
            }
        
        return stats
    
    def get_achievement_stats(self) -> Dict[str, int]:
        """Get achievement unlock statistics."""
        users = self._load_all_users()
        
        all_achievements = []
        for user in users.values():
            all_achievements.extend(user.get("achievements", []))
        
        return dict(Counter(all_achievements))
    
    # ==================== CONVERSATION ANALYTICS ====================
    
    def get_conversation_count(self) -> int:
        """Get total conversation turns."""
        conversations_file = self.conversations_dir / "all_conversations.jsonl"
        return len(self._load_jsonl(conversations_file))
    
    def get_average_message_length(self) -> Dict[str, float]:
        """Get average message length for users and Vera."""
        conversations_file = self.conversations_dir / "all_conversations.jsonl"
        conversations = self._load_jsonl(conversations_file)
        
        if not conversations:
            return {"user_avg": 0.0, "vera_avg": 0.0}
        
        user_lengths = [len(c.get("user_message", "")) for c in conversations]
        vera_lengths = [len(c.get("vera_response", "")) for c in conversations]
        
        return {
            "user_avg": sum(user_lengths) / len(user_lengths),
            "vera_avg": sum(vera_lengths) / len(vera_lengths),
        }
    
    def get_scenario_usage(self) -> Dict[str, int]:
        """Get usage count per scenario."""
        conversations_file = self.conversations_dir / "all_conversations.jsonl"
        conversations = self._load_jsonl(conversations_file)
        
        scenarios = Counter()
        for conv in conversations:
            scenario = conv.get("scenario")
            if scenario:
                scenarios[scenario] += 1
        
        return dict(scenarios)
    
    def get_peak_usage_hours(self) -> Dict[int, int]:
        """Get message count by hour of day."""
        conversations_file = self.conversations_dir / "all_conversations.jsonl"
        conversations = self._load_jsonl(conversations_file)
        
        hours = Counter()
        for conv in conversations:
            timestamp = conv.get("timestamp")
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp)
                    hours[dt.hour] += 1
                except:
                    pass
        
        return dict(sorted(hours.items()))
    
    # ==================== FEEDBACK ANALYTICS ====================
    
    def get_feedback_count(self) -> int:
        """Get total feedback entries."""
        feedback_file = self.feedback_dir / "all_feedback.jsonL"
        return len(self._load_jsonl(feedback_file))
    
    def get_recent_feedback(self, limit: int = 10) -> List[Dict]:
        """Get recent feedback entries."""
        feedback_file = self.feedback_dir / "all_feedback.jsonL"
        feedback = self._load_jsonl(feedback_file)
        return feedback[-limit:] if feedback else []
    
    # ==================== SUMMARY REPORT ====================
    
    def generate_report(self) -> str:
        """Generate a summary report."""
        report = []
        report.append("=" * 50)
        report.append("📊 OPENAURIO ANALYTICS REPORT")
        report.append("=" * 50)
        report.append("")
        
        # User metrics
        report.append("👥 USERS")
        report.append("-" * 30)
        report.append(f"Total Users: {self.get_total_users()}")
        report.append(f"Active (7 days): {self.get_active_users(7)}")
        report.append(f"Active (30 days): {self.get_active_users(30)}")
        report.append(f"Average XP: {self.get_average_xp():.1f}")
        report.append(f"Level Distribution: {self.get_user_level_distribution()}")
        report.append("")
        
        # Engagement metrics
        report.append("💬 ENGAGEMENT")
        report.append("-" * 30)
        report.append(f"Total Messages: {self.get_total_messages()}")
        report.append(f"Voice Messages: {self.get_total_voice_messages()} ({self.get_voice_percentage():.1f}%)")
        report.append(f"Conversation Turns: {self.get_conversation_count()}")
        report.append("")
        
        # Scenario completion
        report.append("📚 SCENARIO COMPLETION")
        report.append("-" * 30)
        for scenario, stats in self.get_scenario_completion_rates().items():
            report.append(f"  {scenario}: {stats['completed']}/{stats['total_users']} ({stats['completion_rate']:.1f}%)")
        report.append("")
        
        # Achievements
        report.append("🏆 ACHIEVEMENTS")
        report.append("-" * 30)
        achievement_stats = self.get_achievement_stats()
        if achievement_stats:
            for achievement, count in sorted(achievement_stats.items(), key=lambda x: -x[1]):
                report.append(f"  {achievement}: {count} users")
        else:
            report.append("  No achievements unlocked yet")
        report.append("")
        
        # Feedback
        report.append("📝 FEEDBACK")
        report.append("-" * 30)
        report.append(f"Total Feedback: {self.get_feedback_count()}")
        report.append("")
        
        # Peak hours
        peak_hours = self.get_peak_usage_hours()
        if peak_hours:
            report.append("⏰ PEAK USAGE HOURS")
            report.append("-" * 30)
            sorted_hours = sorted(peak_hours.items(), key=lambda x: -x[1])[:5]
            for hour, count in sorted_hours:
                report.append(f"  {hour:02d}:00 - {count} messages")
            report.append("")
        
        report.append("=" * 50)
        
        return "\n".join(report)


if __name__ == "__main__":
    # Run analytics report
    analytics = Analytics()
    print(analytics.generate_report())