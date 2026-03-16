#!/usr/bin/env python3
"""
openaurio Analytics Plotting

Generate visualizations of user behavior and engagement.

Usage:
    uv run scripts/plot_analytics.py              # Generate all plots
    uv run scripts/plot_analytics.py --output-dir ./plots  # Custom output directory
"""

import sys
import os
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import seaborn as sns
from matplotlib.patches import Patch

from src.analytics import Analytics, ConversationLogger


def setup_style():
    """Set up seaborn style for beautiful plots."""
    # Use seaborn's modern style
    sns.set_theme(style="whitegrid", palette="muted", font_scale=1.1)
    
    # Custom color palette
    sns.set_palette("husl")
    
    # Set figure defaults
    plt.rcParams['figure.figsize'] = (10, 6)
    plt.rcParams['figure.dpi'] = 100
    plt.rcParams['savefig.dpi'] = 150
    plt.rcParams['font.size'] = 12
    plt.rcParams['axes.titlesize'] = 14
    plt.rcParams['axes.labelsize'] = 12
    plt.rcParams['axes.titleweight'] = 'bold'
    plt.rcParams['axes.labelweight'] = 'bold'
    plt.rcParams['figure.facecolor'] = 'white'
    plt.rcParams['axes.facecolor'] = '#f8f9fa'
    plt.rcParams['axes.edgecolor'] = '#dee2e6'
    plt.rcParams['grid.color'] = '#e9ecef'
    plt.rcParams['grid.linewidth'] = 0.5


def plot_level_distribution(analytics: Analytics, output_dir: Path):
    """Plot user level distribution as pie chart."""
    level_dist = analytics.get_user_level_distribution()
    
    if not level_dist:
        print("  ⚠️ No level data to plot")
        return
    
    fig, ax = plt.subplots(figsize=(8, 8))
    
    levels = ['A1', 'A2', 'B1', 'B2']
    colors = sns.color_palette("husl", len(levels))
    
    values = [level_dist.get(level, 0) for level in levels]
    labels = [f'{level}\n({count} users)' for level, count in zip(levels, values)]
    
    # Only show non-zero slices
    non_zero = [(v, l, c) for v, l, c in zip(values, labels, colors) if v > 0]
    if non_zero:
        values, labels, colors = zip(*non_zero)
        wedges, texts, autotexts = ax.pie(
            values, labels=labels, colors=colors,
            autopct='%1.1f%%', startangle=90,
            explode=[0.03] * len(values),
            shadow=True,
            textprops={'fontsize': 11, 'fontweight': 'bold'}
        )
        for autotext in autotexts:
            autotext.set_fontsize(12)
            autotext.set_fontweight('bold')
        ax.set_title('User Level Distribution', fontsize=16, fontweight='bold', pad=20)
    else:
        ax.text(0.5, 0.5, 'No users yet', ha='center', va='center', fontsize=14)
        ax.set_title('User Level Distribution', fontsize=16, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'level_distribution.png', dpi=150, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.close()
    print("  ✅ level_distribution.png")


def plot_xp_distribution(analytics: Analytics, output_dir: Path):
    """Plot XP distribution as histogram."""
    users = analytics._load_all_users()
    
    if not users:
        print("  ⚠️ No user data to plot")
        return
    
    xp_values = [user.get('xp', 0) for user in users.values()]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Create histogram with seaborn style
    max_xp = max(xp_values) if xp_values else 100
    bins = np.arange(0, max_xp + 50, 25)
    
    # Use seaborn's histogram
    sns.histplot(xp_values, bins=bins, color=sns.color_palette("husl")[0], 
                 edgecolor='white', alpha=0.8, ax=ax, kde=True)
    
    ax.set_xlabel('XP Points', fontsize=12, fontweight='bold')
    ax.set_ylabel('Number of Users', fontsize=12, fontweight='bold')
    ax.set_title('XP Distribution Across Users', fontsize=16, fontweight='bold', pad=15)
    
    # Add level thresholds with annotations
    level_thresholds = [(100, 'A2', '#e74c3c'), (300, 'B1', '#f39c12'), (600, 'B2', '#27ae60')]
    for threshold, level, color in level_thresholds:
        if threshold <= max_xp:
            ax.axvline(x=threshold, color=color, linestyle='--', alpha=0.8, linewidth=2)
            ax.annotate(f' {level}', xy=(threshold, ax.get_ylim()[1] * 0.95), 
                       color=color, fontsize=11, fontweight='bold', va='top')
    
    # Remove top and right spines for cleaner look
    sns.despine(ax=ax, top=True, right=True)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'xp_distribution.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print("  ✅ xp_distribution.png")


def plot_peak_usage_hours(analytics: Analytics, output_dir: Path):
    """Plot peak usage hours as bar chart."""
    peak_hours = analytics.get_peak_usage_hours()
    
    if not peak_hours:
        print("  ⚠️ No conversation data to plot peak hours")
        return
    
    fig, ax = plt.subplots(figsize=(14, 6))
    
    hours = list(range(24))
    counts = [peak_hours.get(h, 0) for h in hours]
    
    # Create color gradient based on activity
    colors = sns.color_palette("viridis", 24)
    bar_colors = [colors[h] if counts[h] > 0 else '#e0e0e0' for h in hours]
    
    bars = ax.bar(hours, counts, color=bar_colors, edgecolor='white', linewidth=0.5)
    
    ax.set_xlabel('Hour of Day (CET)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Number of Messages', fontsize=12, fontweight='bold')
    ax.set_title('Peak Usage Hours', fontsize=16, fontweight='bold', pad=15)
    ax.set_xticks(hours)
    ax.set_xticklabels([f'{h:02d}:00' for h in hours], rotation=45, ha='right')
    
    # Highlight peak hour
    if peak_hours:
        peak_hour = max(peak_hours, key=peak_hours.get)
        peak_count = peak_hours[peak_hour]
        ax.annotate(f'Peak: {peak_hour:02d}:00 ({peak_count} msgs)', 
                   xy=(peak_hour, peak_count),
                   xytext=(peak_hour + 2, peak_count + max(counts) * 0.1),
                   fontsize=11, fontweight='bold', color='#e74c3c',
                   arrowprops=dict(arrowstyle='->', color='#e74c3c', lw=2),
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='#e74c3c'))
    
    sns.despine(ax=ax, top=True, right=True)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'peak_usage_hours.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print("  ✅ peak_usage_hours.png")


def plot_scenario_completion(analytics: Analytics, output_dir: Path):
    """Plot scenario completion rates as horizontal bar chart."""
    scenario_stats = analytics.get_scenario_completion_rates()
    
    if not scenario_stats:
        print("  ⚠️ No scenario data to plot")
        return
    
    fig, ax = plt.subplots(figsize=(10, 5))
    
    scenarios = list(scenario_stats.keys())
    completion_rates = [stats['completion_rate'] for stats in scenario_stats.values()]
    
    # Use seaborn color palette
    colors = sns.color_palette("husl", len(scenarios))
    
    # Create horizontal bar chart
    bars = ax.barh(scenarios, completion_rates, color=colors, edgecolor='white', height=0.6)
    
    ax.set_xlabel('Completion Rate (%)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Scenario', fontsize=12, fontweight='bold')
    ax.set_title('Scenario Completion Rates', fontsize=16, fontweight='bold', pad=15)
    ax.set_xlim(0, 100)
    
    # Add percentage labels with nice formatting
    for bar, rate in zip(bars, completion_rates):
        width = bar.get_width()
        ax.text(width + 2, bar.get_y() + bar.get_height()/2, 
               f'{rate:.1f}%', va='center', fontsize=11, fontweight='bold')
    
    # Add gridlines
    ax.xaxis.grid(True, alpha=0.3)
    ax.yaxis.grid(False)
    
    sns.despine(ax=ax, top=True, right=True)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'scenario_completion.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print("  ✅ scenario_completion.png")


def plot_voice_vs_text(analytics: Analytics, output_dir: Path):
    """Plot voice vs text messages as pie chart."""
    total_messages = analytics.get_total_messages()
    voice_messages = analytics.get_total_voice_messages()
    text_messages = total_messages - voice_messages
    
    if total_messages == 0:
        print("  ⚠️ No message data to plot")
        return
    
    fig, ax = plt.subplots(figsize=(8, 8))
    
    values = [text_messages, voice_messages]
    labels = [f'Text\n({text_messages:,} msgs)', f'Voice\n({voice_messages:,} msgs)']
    colors = [sns.color_palette("husl")[0], sns.color_palette("husl")[3]]
    
    wedges, texts, autotexts = ax.pie(
        values, labels=labels, colors=colors,
        autopct='%1.1f%%', startangle=90,
        explode=[0, 0.05],
        shadow=True,
        textprops={'fontsize': 12, 'fontweight': 'bold'}
    )
    
    for autotext in autotexts:
        autotext.set_fontsize(14)
        autotext.set_fontweight('bold')
        autotext.set_color('white')
    
    ax.set_title('Voice vs Text Messages', fontsize=16, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'voice_vs_text.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print("  ✅ voice_vs_text.png")


def plot_achievements(analytics: Analytics, output_dir: Path):
    """Plot achievement unlock statistics as horizontal bar chart."""
    achievement_stats = analytics.get_achievement_stats()
    
    if not achievement_stats:
        print("  ⚠️ No achievement data to plot")
        return
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Achievement display names (without emojis for font compatibility)
    achievement_names = {
        'first_message': 'Forsta steget (First Step)',
        'fika_master': 'Fika Master',
        'grocery_expert': 'Matvaruexpert (Grocery Expert)',
        'apartment_hunter': 'Lagenhetsjagaren (Apartment Hunter)',
        'voice_pro': 'Rostproffs (Voice Pro)',
        'week_streak': 'Veckostreak (7-Day Streak)',
        'month_master': 'Manadsmastare (Month Master)',
        'conversation_starter': 'Samtalsstartaren (Conversation Starter)',
        'polyglot': 'Polyglotten (Polyglot)',
    }
    
    achievements = list(achievement_stats.keys())
    counts = list(achievement_stats.values())
    
    # Sort by count
    sorted_data = sorted(zip(achievements, counts), key=lambda x: x[1], reverse=True)
    achievements, counts = zip(*sorted_data) if sorted_data else ([], [])
    
    labels = [achievement_names.get(a, a) for a in achievements]
    
    # Create gradient colors
    colors = sns.color_palette("viridis", len(achievements))
    
    bars = ax.barh(labels, counts, color=colors, edgecolor='white', height=0.7)
    
    ax.set_xlabel('Number of Users', fontsize=12, fontweight='bold')
    ax.set_title('Achievement Unlocks', fontsize=16, fontweight='bold', pad=15)
    
    # Add count labels
    for bar, count in zip(bars, counts):
        width = bar.get_width()
        ax.text(width + 0.1, bar.get_y() + bar.get_height()/2, 
               str(count), va='center', fontsize=11, fontweight='bold')
    
    ax.xaxis.grid(True, alpha=0.3)
    ax.yaxis.grid(False)
    
    sns.despine(ax=ax, top=True, right=True)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'achievements.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print("  ✅ achievements.png")


def plot_user_growth(analytics: Analytics, output_dir: Path):
    """Plot user growth over time."""
    users = analytics._load_all_users()
    
    if not users:
        print("  ⚠️ No user data to plot growth")
        return
    
    # Extract creation dates
    dates = []
    for user_data in users.values():
        created_at = user_data.get('created_at')
        if created_at:
            try:
                dt = datetime.fromisoformat(created_at)
                dates.append(dt.date())
            except:
                pass
    
    if not dates:
        print("  ⚠️ No creation dates found")
        return
    
    # Count users per day
    date_counts = Counter(dates)
    sorted_dates = sorted(date_counts.items())
    
    # Calculate cumulative users
    cumulative = []
    total = 0
    for date, count in sorted_dates:
        total += count
        cumulative.append((date, total))
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    dates_plot = [d[0] for d in cumulative]
    counts_plot = [d[1] for d in cumulative]
    
    # Create area plot with seaborn style
    ax.fill_between(dates_plot, counts_plot, alpha=0.3, color=sns.color_palette("husl")[0])
    ax.plot(dates_plot, counts_plot, marker='o', color=sns.color_palette("husl")[0], 
            linewidth=2.5, markersize=10, markeredgecolor='white', markeredgewidth=2)
    
    ax.set_xlabel('Date', fontsize=12, fontweight='bold')
    ax.set_ylabel('Total Users', fontsize=12, fontweight='bold')
    ax.set_title('User Growth Over Time', fontsize=16, fontweight='bold', pad=15)
    
    # Format x-axis
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    plt.xticks(rotation=45, ha='right')
    
    # Add data labels
    for date, count in cumulative:
        ax.annotate(str(count), xy=(date, count), xytext=(0, 10),
                   textcoords='offset points', ha='center', fontsize=10, fontweight='bold')
    
    sns.despine(ax=ax, top=True, right=True)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'user_growth.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print("  ✅ user_growth.png")


def plot_daily_activity(analytics: Analytics, output_dir: Path):
    """Plot daily activity (messages per day)."""
    conv_logger = ConversationLogger()
    conversations = conv_logger.get_all_conversations()
    
    if not conversations:
        print("  ⚠️ No conversation data to plot daily activity")
        return
    
    # Extract dates
    dates = []
    for conv in conversations:
        timestamp = conv.get('timestamp')
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp)
                dates.append(dt.date())
            except:
                pass
    
    if not dates:
        print("  ⚠️ No timestamps found")
        return
    
    # Count messages per day
    date_counts = Counter(dates)
    sorted_dates = sorted(date_counts.items())
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    dates_plot = [d[0] for d in sorted_dates]
    counts_plot = [d[1] for d in sorted_dates]
    
    # Create bar chart with seaborn style
    colors = sns.color_palette("husl", len(dates_plot))
    bars = ax.bar(dates_plot, counts_plot, color=colors, edgecolor='white', linewidth=0.5)
    
    ax.set_xlabel('Date', fontsize=12, fontweight='bold')
    ax.set_ylabel('Number of Messages', fontsize=12, fontweight='bold')
    ax.set_title('Daily Activity', fontsize=16, fontweight='bold', pad=15)
    
    # Format x-axis
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    plt.xticks(rotation=45, ha='right')
    
    # Add value labels on bars
    for bar, count in zip(bars, counts_plot):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
               str(count), ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    sns.despine(ax=ax, top=True, right=True)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'daily_activity.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print("  ✅ daily_activity.png")


def plot_summary_dashboard(analytics: Analytics, output_dir: Path):
    """Create a summary dashboard with key metrics."""
    fig = plt.figure(figsize=(16, 12))
    
    # Create grid for subplots
    gs = fig.add_gridspec(2, 3, hspace=0.3, wspace=0.3)
    
    # 1. Level Distribution (top left)
    ax1 = fig.add_subplot(gs[0, 0])
    level_dist = analytics.get_user_level_distribution()
    if level_dist:
        levels = ['A1', 'A2', 'B1', 'B2']
        colors = sns.color_palette("husl", len(levels))
        values = [level_dist.get(level, 0) for level in levels]
        non_zero = [(v, l, c) for v, l, c in zip(values, levels, colors) if v > 0]
        if non_zero:
            values, labels, colors = zip(*non_zero)
            wedges, texts, autotexts = ax1.pie(values, labels=labels, colors=colors, 
                                               autopct='%1.0f%%', startangle=90,
                                               textprops={'fontweight': 'bold'})
            for autotext in autotexts:
                autotext.set_fontsize(12)
                autotext.set_fontweight('bold')
    ax1.set_title('Level Distribution', fontweight='bold', fontsize=14, pad=10)
    
    # 2. Voice vs Text (top middle)
    ax2 = fig.add_subplot(gs[0, 1])
    total_messages = analytics.get_total_messages()
    voice_messages = analytics.get_total_voice_messages()
    text_messages = total_messages - voice_messages
    if total_messages > 0:
        colors = [sns.color_palette("husl")[0], sns.color_palette("husl")[3]]
        wedges, texts, autotexts = ax2.pie([text_messages, voice_messages], 
                                           labels=['Text', 'Voice'], colors=colors,
                                           autopct='%1.0f%%', startangle=90,
                                           textprops={'fontweight': 'bold'})
        for autotext in autotexts:
            autotext.set_fontsize(12)
            autotext.set_fontweight('bold')
    ax2.set_title('Voice vs Text', fontweight='bold', fontsize=14, pad=10)
    
    # 3. Scenario Completion (top right)
    ax3 = fig.add_subplot(gs[0, 2])
    scenario_stats = analytics.get_scenario_completion_rates()
    if scenario_stats:
        scenarios = list(scenario_stats.keys())
        rates = [stats['completion_rate'] for stats in scenario_stats.values()]
        colors = sns.color_palette("husl", len(scenarios))
        bars = ax3.bar(scenarios, rates, color=colors, edgecolor='white')
        ax3.set_ylabel('Completion %', fontweight='bold')
        ax3.set_ylim(0, 100)
        for bar, rate in zip(bars, rates):
            ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                    f'{rate:.0f}%', ha='center', fontsize=10, fontweight='bold')
    ax3.set_title('Scenario Completion', fontweight='bold', fontsize=14, pad=10)
    sns.despine(ax=ax3, top=True, right=True)
    
    # 4. Key Metrics (bottom left - spans 2 columns)
    ax4 = fig.add_subplot(gs[1, :2])
    ax4.axis('off')
    
    # Create a nice metrics box
    metrics_text = f"""
    KEY METRICS
    ─────────────────────────────
    
    Total Users: {analytics.get_total_users()}
    Active (7 days): {analytics.get_active_users(7)}
    Active (30 days): {analytics.get_active_users(30)}
    
    Total Messages: {analytics.get_total_messages()}
    Voice Messages: {analytics.get_total_voice_messages()}
    
    Average XP: {analytics.get_average_xp():.1f}
    Feedback Count: {analytics.get_feedback_count()}
    """
    
    ax4.text(0.05, 0.5, metrics_text, transform=ax4.transAxes, 
            fontsize=13, verticalalignment='center',
            fontfamily='monospace',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='#f8f9fa', 
                     edgecolor='#dee2e6', linewidth=2))
    
    # 5. Achievements (bottom right)
    ax5 = fig.add_subplot(gs[1, 2])
    achievement_stats = analytics.get_achievement_stats()
    if achievement_stats:
        achievements = list(achievement_stats.keys())[:5]  # Top 5
        counts = [achievement_stats[a] for a in achievements]
        
        # Short names
        short_names = {
            'first_message': 'First Step',
            'fika_master': 'Fika Master',
            'grocery_expert': 'Grocery',
            'apartment_hunter': 'Apartment',
            'voice_pro': 'Voice Pro',
        }
        labels = [short_names.get(a, a) for a in achievements]
        
        colors = sns.color_palette("viridis", len(achievements))
        bars = ax5.barh(labels, counts, color=colors, edgecolor='white')
        ax5.set_xlabel('Users', fontweight='bold')
        for bar, count in zip(bars, counts):
            ax5.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
                    str(count), va='center', fontsize=10, fontweight='bold')
    ax5.set_title('Top Achievements', fontweight='bold', fontsize=14, pad=10)
    sns.despine(ax=ax5, top=True, right=True)
    
    plt.suptitle('openaurio Analytics Dashboard', fontsize=18, fontweight='bold', y=0.98)
    plt.tight_layout()
    plt.savefig(output_dir / 'dashboard.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print("  ✅ dashboard.png")


def main():
    parser = argparse.ArgumentParser(description="Generate openaurio analytics plots")
    parser.add_argument("--output-dir", "-o", default="plots", 
                       help="Output directory for plots (default: plots)")
    parser.add_argument("--dashboard", "-d", action="store_true",
                       help="Only generate summary dashboard")
    
    args = parser.parse_args()
    
    # Set up output directory
    project_root = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    output_dir = project_root / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Set up matplotlib style
    setup_style()
    
    # Initialize analytics
    analytics = Analytics()
    
    print("\n📊 Generating openaurio analytics plots...")
    print(f"📁 Output directory: {output_dir}\n")
    
    if args.dashboard:
        plot_summary_dashboard(analytics, output_dir)
    else:
        # Generate all plots
        plot_level_distribution(analytics, output_dir)
        plot_xp_distribution(analytics, output_dir)
        plot_peak_usage_hours(analytics, output_dir)
        plot_scenario_completion(analytics, output_dir)
        plot_voice_vs_text(analytics, output_dir)
        plot_achievements(analytics, output_dir)
        plot_user_growth(analytics, output_dir)
        plot_daily_activity(analytics, output_dir)
        plot_summary_dashboard(analytics, output_dir)
    
    print(f"\n✅ Done! Plots saved to {output_dir}\n")


if __name__ == "__main__":
    main()