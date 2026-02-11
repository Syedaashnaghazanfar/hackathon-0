"""
Twitter/X Monitor for Gold Tier AI Employee.

Detects mentions, replies, and viral activity using browser automation.
Includes viral detection with rolling time window tracking.
"""

import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Dict
from collections import defaultdict
from playwright.async_api import async_playwright, Browser, Page, TimeoutError as PlaywrightTimeoutError

from .base_monitor import BaseSocialMonitor, SessionExpiredError, PlatformError
from ..models.social_interaction import SocialInteractionSchema


logger = logging.getLogger(__name__)


class TwitterMonitor(BaseSocialMonitor):
    """
    Monitor for Twitter/X notifications and interactions.

    Detects:
    - Mentions of user
    - Replies to user's tweets
    - Viral activity (10+ mentions in 1 hour)

    Uses existing Twitter session from .social_session/twitter/
    Includes rolling window tracking for viral detection.
    """

    PLATFORM = "twitter"

    # Twitter-specific selectors
    SELECTORS = {
        # Navigation
        "notifications_nav": "a[data-testid='AppTabBar_Notifications_Link']",

        # Mentions
        "mention_item": "div[data-testid='tweet']",
        "mention_text": "div[data-testid='tweetText']",
        "mention_author": "a[href*='/'][role='link']",  # Twitter username link
        "mention_link": "a[href*='/status/']",

        # Login check
        "login_form": "form[data-testid='loginForm']",

        # Notifications tabs
        "mentions_tab": "a[href='/notifications/mentions']",
    }

    def __init__(self, session_dir: Optional[Path] = None):
        """Initialize Twitter monitor."""
        super().__init__(session_dir)
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None

        # Rolling window for viral detection
        # Structure: {hour_str: mention_count}
        self.mention_history: Dict[str, int] = defaultdict(int)

    async def check_notifications(self) -> List[SocialInteractionSchema]:
        """
        Check for new Twitter notifications (mentions, replies).

        Returns:
            List of detected social interactions

        Raises:
            SessionExpiredError: If not logged in
            PlatformError: If navigation or detection fails
        """
        interactions = []
        start_time = datetime.now()

        async with async_playwright() as p:
            try:
                # Launch browser with persistent context
                self.browser = await p.chromium.launch_persistent_context(
                    user_data_dir=str(self.session_dir),
                    headless=False,
                    viewport={"width": 1280, "height": 720},
                )

                self.page = await self.browser.new_page()

                # Navigate to Twitter/X
                await self.page.goto("https://x.com/", wait_until="networkidle")

                # Check if logged in
                if await self.page.query_selector(self.SELECTORS["login_form"]):
                    raise SessionExpiredError("Not logged in - login form detected")

                # Navigate to notifications
                await self._navigate_to_notifications()

                # Extract mentions
                mentions = await self._extract_mentions(start_time)
                interactions.extend(mentions)

                # Check for viral activity
                viral_alerts = self._check_viral_activity(mentions, start_time)
                interactions.extend(viral_alerts)

                self.logger.info(f"Extracted {len(interactions)} Twitter interactions")

            except PlaywrightTimeoutError as e:
                self.logger.error(f"Timeout waiting for Twitter elements: {e}")
                raise PlatformError(f"Twitter navigation timeout: {e}")

            except Exception as e:
                self.logger.error(f"Error checking Twitter notifications: {e}")
                raise PlatformError(f"Twitter check failed: {e}")

            finally:
                # Always close browser
                if self.browser:
                    await self.browser.close()

        return interactions

    async def _navigate_to_notifications(self) -> None:
        """
        Navigate to Twitter notifications page.

        This method tries:
        1. Click notifications tab
        2. Navigate to mentions URL directly
        """
        try:
            # Try clicking notifications nav
            await self.page.wait_for_selector(self.SELECTORS["notifications_nav"], timeout=5000)
            await self.page.click(self.SELECTORS["notifications_nav"])
            await self.page.wait_for_timeout(2000)
            self.logger.info("Clicked notifications navigation")

            # Try to navigate to mentions tab
            mentions_tab = await self.page.query_selector(self.SELECTORS["mentions_tab"])
            if mentions_tab:
                await mentions_tab.click()
                await self.page.wait_for_timeout(2000)
                self.logger.info("Navigated to mentions tab")

        except PlaywrightTimeoutError:
            # Fallback: navigate directly to mentions URL
            self.logger.warning("Could not find notifications nav, navigating to mentions URL")
            await self.page.goto("https://x.com/notifications/mentions", wait_until="networkidle")

    async def _extract_mentions(self, start_time: datetime) -> List[SocialInteractionSchema]:
        """
        Extract mentions from Twitter notifications.

        Args:
            start_time: When this check started

        Returns:
            List of SocialInteractionSchema objects for mentions
        """
        interactions = []

        try:
            # Wait for tweet elements to load
            await self.page.wait_for_selector(self.SELECTORS["mention_item"], timeout=10000)

            # Get all mention elements
            mention_elements = await self.page.query_selector_all(self.SELECTORS["mention_item"])

            self.logger.info(f"Found {len(mention_elements)} mention elements")

            # Process mentions (limit to last 20)
            for i, tweet_el in enumerate(mention_elements[:20]):
                try:
                    # Extract tweet text
                    text_elem = await tweet_el.query_selector(self.SELECTORS["mention_text"])
                    tweet_text = await text_elem.inner_text() if text_elem else ""

                    # Extract author (first link usually is the author)
                    author_links = await tweet_el.query_selector_all(self.SELECTORS["mention_author"])
                    author = "Unknown"
                    if author_links:
                        # Get username from first link (handle format: @username)
                        author_handle = await author_links[0].get_attribute("href")
                        author = author_handle.split("/")[-1] if author_handle else "Unknown"

                    # Extract tweet URL
                    link_elem = await tweet_el.query_selector(self.SELECTORS["mention_link"])
                    tweet_url = await link_elem.get_attribute("href") if link_elem else None

                    # Create SocialInteractionSchema
                    interaction = SocialInteractionSchema(
                        platform="twitter",
                        interaction_type="mention",
                        author=author,
                        content=tweet_text,
                        post_url=f"https://x.com{tweet_url}" if tweet_url else None,
                        timestamp=start_time,
                        detected_at=start_time,
                        priority="LOW",  # Will be updated by keyword filter
                    )

                    interactions.append(interaction)

                    # Track for viral detection
                    hour_key = start_time.strftime("%Y-%m-%d-%H")
                    self.mention_history[hour_key] += 1

                    self.logger.debug(f"Extracted mention from @{author}: {tweet_text[:50]}")

                except Exception as e:
                    self.logger.error(f"Error extracting mention {i}: {e}")
                    continue

        except PlaywrightTimeoutError:
            self.logger.warning("No mentions found on Twitter notifications page")

        return interactions

    def _check_viral_activity(
        self,
        mentions: List[SocialInteractionSchema],
        current_time: datetime
    ) -> List[SocialInteractionSchema]:
        """
        Check for viral activity (exceeds mention threshold).

        Args:
            mentions: List of mentions detected in this check
            current_time: Current time

        Returns:
            List of viral alert SocialInteractionSchema objects (0 or 1)

        Viral detection logic:
        - Track mentions in rolling 1-hour window
        - If > threshold (default: 3), create viral alert
        - Aggregate top mentions in alert
        """
        from os import getenv

        # Get threshold from environment (default: 3)
        threshold = int(getenv("SOCIAL_TWITTER_MENTION_THRESHOLD", "3"))

        # Calculate mentions in last hour
        one_hour_ago = current_time - timedelta(hours=1)
        recent_mentions = 0

        # Sum mentions from last hour
        for hour_key, count in self.mention_history.items():
            hour_datetime = datetime.strptime(hour_key, "%Y-%m-%d-%H")
            if hour_datetime >= one_hour_ago:
                recent_mentions += count

        self.logger.info(f"Recent mentions (last hour): {recent_mentions}, threshold: {threshold}")

        # Check if exceeded threshold
        if recent_mentions > threshold:
            # Create viral alert
            viral_alert = SocialInteractionSchema(
                platform="twitter",
                interaction_type="mention",
                author="System",  # System-generated alert
                content=f"⚠️ VIRAL ALERT: {recent_mentions} mentions in the last hour (threshold: {threshold})\n\n" +
                       f"Top recent activity:\n" +
                       "\n".join([
                           f"- @{m.author}: {m.content[:50]}..."
                           for m in mentions[:5]  # Top 5 mentions
                       ]),
                timestamp=current_time,
                detected_at=current_time,
                priority="HIGH",
                priority_reason=f"Viral activity detected ({recent_mentions} mentions exceeds threshold of {threshold})",
                metadata={
                    "viral_type": "mention_spike",
                    "mention_count": recent_mentions,
                    "threshold": threshold,
                    "time_window": "1_hour",
                }
            )

            self.logger.warning(f"Viral alert created: {recent_mentions} mentions in last hour")
            return [viral_alert]

        return []

    def _cleanup_old_history(self, current_time: datetime) -> None:
        """
        Clean up mention history older than 1 hour.

        Args:
            current_time: Current time
        """
        one_hour_ago = current_time - timedelta(hours=1)

        # Remove old entries
        old_keys = [
            hour_key
            for hour_key in self.mention_history.keys()
            if datetime.strptime(hour_key, "%Y-%m-%d-%H") < one_hour_ago
        ]

        for key in old_keys:
            del self.mention_history[key]

        if old_keys:
            self.logger.debug(f"Cleaned up {len(old_keys)} old mention history entries")

    def extract_interactions(self, raw_data: dict) -> List[SocialInteractionSchema]:
        """
        Extract interactions from raw Twitter data.

        This method is used when we have JSON/API data instead of HTML.
        Currently not used but kept for future extensibility.

        Args:
            raw_data: Raw Twitter data (JSON, etc.)

        Returns:
            List of SocialInteractionSchema objects

        Raises:
            ValueError: If raw_data is malformed
        """
        # This would be used if we had Twitter API access
        # For browser automation, we use check_notifications() directly
        raise NotImplementedError("Use check_notifications() for browser automation")
