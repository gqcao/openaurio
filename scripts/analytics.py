#!/usr/bin/env python3
"""
openaurio Analytics CLI

Run analytics reports on user behavior and feedback.

Usage:
    uv run scripts/analytics.py
    uv run scripts/analytics.py --feedback
    uv run scripts/analytics.py --conversations
"""

import sys
import os
import argparse

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.analytics import Analytics, FeedbackLogger, ConversationLogger


def main():
    parser = argparse.ArgumentParser(description="openaurio Analytics")
    parser.add_argument("--feedback", action="store_true", help="Show recent feedback")
    parser.add_argument("--conversations", action="store_true", help="Show recent conversations")
    parser.add_argument("--users", action="store_true", help="Show user statistics")
    parser.add_argument("--all", action="store_true", help="Show full report")
    
    args = parser.parse_args()
    
    analytics = Analytics()
    
    if args.feedback:
        print("\n📝 RECENT FEEDBACK")
        print("-" * 50)
        feedback_logger = FeedbackLogger()
        recent = feedback_logger.get_recent_feedback(10)
        if recent:
            for fb in recent:
                print(f"\n[{fb['timestamp']}]")
                print(f"User: {fb['user_name']} (Level: {fb['level']}, XP: {fb['xp']})")
                print(f"Feedback: {fb['feedback_text']}")
        else:
            print("No feedback yet.")
    
    elif args.conversations:
        print("\n💬 RECENT CONVERSATIONS")
        print("-" * 50)
        conv_logger = ConversationLogger()
        recent = conv_logger.get_recent_conversations(10)
        if recent:
            for conv in recent:
                print(f"\n[{conv['timestamp']}]")
                print(f"User: {conv['user_name']} (Voice: {conv['is_voice']})")
                print(f"User: {conv['user_message'][:100]}...")
                print(f"Vera: {conv['vera_response'][:100]}...")
        else:
            print("No conversations logged yet.")
    
    elif args.users:
        print("\n👥 USER STATISTICS")
        print("-" * 50)
        print(f"Total Users: {analytics.get_total_users()}")
        print(f"Active (7 days): {analytics.get_active_users(7)}")
        print(f"Active (30 days): {analytics.get_active_users(30)}")
        print(f"Average XP: {analytics.get_average_xp():.1f}")
        print(f"Level Distribution: {analytics.get_user_level_distribution()}")
    
    elif args.all:
        print(analytics.generate_report())
    
    else:
        # Default: show summary report
        print(analytics.generate_report())


if __name__ == "__main__":
    main()