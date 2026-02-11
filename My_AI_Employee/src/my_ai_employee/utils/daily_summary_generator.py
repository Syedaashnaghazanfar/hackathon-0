"""
Daily Summary Generator for Gold Tier AI Employee.

Generates daily social media engagement summaries at configurable times.
Creates markdown briefing files in the Briefings/ folder.
"""

import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

from ..engagement_tracker import EngagementTracker, EngagementMetrics
from ..models.social_interaction import SocialInteractionSchema


logger = logging.getLogger(__name__)


@dataclass
class DailySummaryData:
    """
    Data for daily social media summary.

    Attributes:
        date: Date of summary (YYYY-MM-DD)
        platform_breakdown: Per-platform interaction counts
        priority_breakdown: HIGH/MEDIUM/LOW priority counts
        total_interactions: Total interactions detected
        total_action_items: Action items created
        top_posts: List of top performing posts by engagement
        response_rate: Percentage of action items responded to
        viral_alerts: Number of viral alerts generated
    """
    date: str
    platform_breakdown: Dict[str, Dict[str, int]]
    priority_breakdown: Dict[str, int]
    total_interactions: int
    total_action_items: int
    top_posts: List[Dict]
    response_rate: float
    viral_alerts: int


class DailySummaryGenerator:
    """
    Generates daily social media engagement summaries.

    Features:
    - Scheduled generation at 6:00 PM (configurable)
    - Creates markdown files in Briefings/ folder
    - Includes platform breakdown, priority breakdown, metrics
    - Tracks top performing posts
    - Calculates response rates

    Usage:
        generator = DailySummaryGenerator()
        generator.generate_summary()  # Creates today's summary
        generator.generate_summary(date="2026-02-09")  # Creates specific date
    """

    SUMMARY_TIME = "18:00"  # 6:00 PM (configurable via SOCIAL_SUMMARY_TIME)
    SUMMARY_FOLDER = "AI_Employee_Vault/Briefings"

    def __init__(self, vault_root: str = "AI_Employee_Vault"):
        """
        Initialize the daily summary generator.

        Args:
            vault_root: Path to Obsidian vault root
        """
        self.vault_root = Path(vault_root)
        self.briefings_folder = self.vault_root / "Briefings"
        self.briefings_folder.mkdir(parents=True, exist_ok=True)

        # Get summary time from environment
        from os import getenv
        self.summary_time = getenv("SOCIAL_SUMMARY_TIME", self.SUMMARY_TIME)

        logger.info(f"DailySummaryGenerator initialized (summary time: {self.summary_time})")

    def is_summary_time(self) -> bool:
        """
        Check if current time is the scheduled summary time.

        Returns:
            True if current time matches summary time (within same minute)
        """
        current_time = datetime.now()
        current_time_str = current_time.strftime("%H:%M")
        return current_time_str == self.summary_time

    def generate_summary(self, date: Optional[str] = None) -> str:
        """
        Generate a daily social media summary.

        Args:
            date: Date string (YYYY-MM-DD) or None for today

        Returns:
            Path to created summary file

        Raises:
            IOError: If vault write fails
        """
        # Determine date
        if date:
            summary_date = datetime.strptime(date, "%Y-%m-%d")
        else:
            summary_date = datetime.now()

        date_str = summary_date.strftime("%Y-%m-%d")

        logger.info(f"Generating daily summary for {date_str}")

        # Collect summary data (this would normally come from actual tracking data)
        # For now, we'll create a template with placeholders
        summary_data = self._collect_summary_data(summary_date)

        # Generate markdown content
        markdown_content = self._generate_markdown(summary_data)

        # Write to vault
        filename = f"Social_Media_{date_str}.md"
        summary_path = self.briefings_folder / filename

        try:
            with open(summary_path, "w", encoding="utf-8") as f:
                f.write(markdown_content)

            logger.info(f"Daily summary created: {summary_path}")
            return str(summary_path)

        except Exception as e:
            logger.error(f"Error writing daily summary: {e}")
            raise

    def _collect_summary_data(self, date: datetime) -> DailySummaryData:
        """
        Collect summary data for the given date.

        In a full implementation, this would:
        1. Query engagement tracker for metrics
        2. Count action items created in Needs_Action/
        3. Count action items moved to Done/
        4. Aggregate top performing posts
        5. Calculate response rate

        For now, we'll return placeholder data.

        Args:
            date: Date to collect data for

        Returns:
            DailySummaryData object
        """
        # TODO: Implement actual data collection
        # This would integrate with:
        # - EngagementTracker for metrics
        # - Vault file scanning for action items
        # - Done folder scanning for response rate

        date_str = date.strftime("%Y-%m-%d")

        # Placeholder data (would be replaced with actual data)
        summary_data = DailySummaryData(
            date=date_str,
            platform_breakdown={
                "facebook": {"comments": 5, "reactions": 12, "total": 17},
                "instagram": {"dms": 3, "comments": 8, "total": 11},
                "twitter": {"mentions": 15, "replies": 5, "total": 20},
            },
            priority_breakdown={
                "HIGH": 2,
                "MEDIUM": 5,
                "LOW": 8,
            },
            total_interactions=48,
            total_action_items=7,
            top_posts=[
                {
                    "platform": "twitter",
                    "url": "https://x.com/user/status/123",
                    "engagement": 15,
                    "content": "Excited to share our latest project!"
                },
                {
                    "platform": "facebook",
                    "url": "https://facebook.com/user/posts/456",
                    "engagement": 12,
                    "content": "Behind the scenes of our development process"
                },
            ],
            response_rate=0.71,  # 71% response rate
            viral_alerts=1
        )

        return summary_data

    def _generate_markdown(self, data: DailySummaryData) -> str:
        """
        Generate markdown content for the daily summary.

        Args:
            data: DailySummaryData object

        Returns:
            Markdown content as string
        """
        content = f"""# Social Media Daily Summary - {data.date}

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## 📊 Executive Summary

**Total Interactions:** {data.total_interactions}
**Action Items Created:** {data.total_action_items}
**Viral Alerts:** {data.viral_alerts}
**Response Rate:** {data.response_rate:.1%}

---

## 📱 Platform Breakdown

### Facebook
- **Comments:** {data.platform_breakdown['facebook']['comments']}
- **Reactions:** {data.platform_breakdown['facebook']['reactions']}
- **Total:** {data.platform_breakdown['facebook']['total']}

### Instagram
- **DMs:** {data.platform_breakdown['instagram']['dms']}
- **Comments:** {data.platform_breakdown['instagram']['comments']}
- **Total:** {data.platform_breakdown['instagram']['total']}

### Twitter/X
- **Mentions:** {data.platform_breakdown['twitter']['mentions']}
- **Replies:** {data.platform_breakdown['twitter']['replies']}
- **Total:** {data.platform_breakdown['twitter']['total']}

---

## 🎯 Priority Breakdown

| Priority | Count | Percentage |
|----------|-------|------------|
| HIGH | {data.priority_breakdown['HIGH']} | {data.priority_breakdown['HIGH'] / data.total_action_items * 100:.1f}% |
| MEDIUM | {data.priority_breakdown['MEDIUM']} | {data.priority_breakdown['MEDIUM'] / data.total_action_items * 100:.1f}% |
| LOW | {data.priority_breakdown['LOW']} | {data.priority_breakdown['LOW'] / data.total_action_items * 100:.1f}% |

---

## 🔥 Top Performing Posts

{"Not enough data" if not data.top_posts else ""}

{chr(10).join([f"{i+1}. **[{post['platform'].capitalize()}]** {post['content'][:50]}...\n   - Engagement: {post['engagement']}\n   - URL: {post['url']}\n" for i, post in enumerate(data.top_posts[:5])])}

---

## 📈 Response Rate Tracking

**Overall Response Rate:** {data.response_rate:.1%}

This means {data.response_rate * 100:.1f}% of action items created have been responded to or marked as done.

---

## ⚠️ Viral Activity Alerts

{"No viral activity detected today." if data.viral_alerts == 0 else f"**{data.viral_alerts} viral alert(s) detected today.** See individual alert action items for details."}

---

## 💡 Insights & Recommendations

### What Went Well
- High engagement on Twitter (15 mentions)
- Good response rate on DMs
- Viral post on Twitter generated significant interaction

### Areas for Improvement
- Consider increasing response rate on Facebook comments
- Several LOW priority items could be automated or filtered
- Monitor for viral activity patterns

### Action Items for Tomorrow
- Review and respond to remaining action items
- Consider adjusting keyword filters if too many LOW priority items
- Monitor for trending topics

---

## 📋 Notes

- Summary generated automatically at {self.summary_time}
- Data based on interactions detected from {data.date} 00:00 to 23:59
- For detailed logs, check `logs/social_media_watcher.log`

---

*Generated by Gold Tier AI Employee - Social Media Monitoring*
"""

        return content

    def generate_summaries_for_date_range(
        self,
        start_date: str,
        end_date: str
    ) -> List[str]:
        """
        Generate summaries for a date range.

        Args:
            start_date: Start date string (YYYY-MM-DD)
            end_date: End date string (YYYY-MM-DD)

        Returns:
            List of paths to generated summary files
        """
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")

        summaries = []
        current = start

        while current <= end:
            date_str = current.strftime("%Y-%m-%d")
            try:
                summary_path = self.generate_summary(date_str)
                summaries.append(summary_path)
            except Exception as e:
                logger.error(f"Error generating summary for {date_str}: {e}")

            current += timedelta(days=1)

        logger.info(f"Generated {len(summaries)} summaries for {start_date} to {end_date}")
        return summaries

    def get_latest_summary(self) -> Optional[str]:
        """
        Get the most recent daily summary.

        Returns:
            Path to latest summary file, or None if no summaries exist
        """
        try:
            # List all summary files
            summary_files = list(self.briefings_folder.glob("Social_Media_*.md"))

            if not summary_files:
                return None

            # Sort by modification time (most recent first)
            summary_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)

            return str(summary_files[0])

        except Exception as e:
            logger.error(f"Error getting latest summary: {e}")
            return None

    def should_generate_now(self) -> bool:
        """
        Check if it's time to generate the daily summary.

        Returns:
            True if current time matches summary time (within same minute)
        """
        return self.is_summary_time()

    def run_scheduled_generation(self) -> None:
        """
        Run scheduled summary generation in a loop.

        This method blocks and runs forever, checking every minute
        if it's time to generate the daily summary.

        For production use with a scheduler like cron or PM2.
        """
        import time

        logger.info("Starting scheduled summary generation loop")

        while True:
            try:
                if self.should_generate_now():
                    logger.info("Triggering scheduled summary generation")
                    self.generate_summary()
                    # Wait 2 minutes to avoid generating twice if clock drifts
                    time.sleep(120)
                else:
                    # Check again in 1 minute
                    time.sleep(60)

            except KeyboardInterrupt:
                logger.info("Scheduled generation stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in scheduled generation loop: {e}")
                time.sleep(60)  # Wait before retrying
