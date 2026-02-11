"""
Instagram Monitor for Gold Tier AI Employee.

Detects DMs and comments on user's Instagram posts using browser automation.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from playwright.async_api import async_playwright, Browser, Page, TimeoutError as PlaywrightTimeoutError

from .base_monitor import BaseSocialMonitor, SessionExpiredError, PlatformError
from ..models.social_interaction import SocialInteractionSchema


logger = logging.getLogger(__name__)


class InstagramMonitor(BaseSocialMonitor):
    """
    Monitor for Instagram notifications and interactions.

    Detects:
    - Direct Messages (DMs)
    - Comments on user's posts
    - Mentions in comments

    Uses existing Instagram session from .social_session/instagram/
    """

    PLATFORM = "instagram"

    # Instagram-specific selectors
    SELECTORS = {
        # DM icon
        "dm_icon": "svg[aria-label='Messenger'], a[href='/direct/inbox/']",

        # DM messages
        "dm_thread": "div[role='grid'] a[href*='/direct/t/']",
        "dm_sender": "span[class*='username']",
        "dm_content": "div[dir='auto']",

        # Comments
        "comment_text": "span[dir='auto']",
        "comment_author": "a[href*='/']",
        "comment_link": "a[href*='/p/']",

        # Login check
        "login_form": "form[data-testid='login-form']",

        # Notifications page
        "notifications": "a[href='/notifications/']",
        "notification_item": "div[class*='notification']",
    }

    def __init__(self, session_dir: Optional[Path] = None):
        """Initialize Instagram monitor."""
        super().__init__(session_dir)
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None

    async def check_notifications(self) -> List[SocialInteractionSchema]:
        """
        Check for new Instagram notifications (DMs, comments).

        Returns:
            List of detected social interactions

        Raises:
            SessionExpiredError: If not logged in
            PlatformError: If navigation or detection fails
        """
        interactions = []

        async with async_playwright() as p:
            try:
                # Launch browser with persistent context
                self.browser = await p.chromium.launch_persistent_context(
                    user_data_dir=str(self.session_dir),
                    headless=False,
                    viewport={"width": 1280, "height": 720},
                )

                self.page = await self.browser.new_page()

                # Navigate to Instagram
                await self.page.goto("https://www.instagram.com/", wait_until="networkidle")

                # Check if logged in
                if await self.page.query_selector(self.SELECTORS["login_form"]):
                    raise SessionExpiredError("Not logged in - login form detected")

                # Check DMs
                dms = await self._check_dms()
                interactions.extend(dms)

                # Check comments
                comments = await self._check_comments()
                interactions.extend(comments)

                self.logger.info(f"Extracted {len(interactions)} Instagram interactions")

            except PlaywrightTimeoutError as e:
                self.logger.error(f"Timeout waiting for Instagram elements: {e}")
                raise PlatformError(f"Instagram navigation timeout: {e}")

            except Exception as e:
                self.logger.error(f"Error checking Instagram notifications: {e}")
                raise PlatformError(f"Instagram check failed: {e}")

            finally:
                # Always close browser
                if self.browser:
                    await self.browser.close()

        return interactions

    async def _check_dms(self) -> List[SocialInteractionSchema]:
        """
        Check for new Direct Messages (DMs).

        Returns:
            List of SocialInteractionSchema objects for DMs
        """
        interactions = []
        start_time = datetime.now()

        try:
            # Navigate to DM inbox
            await self.page.goto("https://www.instagram.com/direct/inbox/", wait_until="networkidle")
            await self.page.wait_for_timeout(3000)  # Wait for DMs to load

            # Get DM thread elements
            dm_threads = await self.page.query_selector_all(self.SELECTORS["dm_thread"])

            self.logger.info(f"Found {len(dm_threads)} DM threads")

            # Process DM threads (limit to last 10)
            for i, thread_el in enumerate(dm_threads[:10]):
                try:
                    # Click on thread to open
                    await thread_el.click()
                    await self.page.wait_for_timeout(2000)

                    # Extract sender username
                    sender_elem = await self.page.query_selector(self.SELECTORS["dm_sender"])
                    sender = await sender_elem.inner_text() if sender_elem else "Unknown"

                    # Extract message content
                    content_elem = await self.page.query_selector(self.SELECTORS["dm_content"])
                    # Get the last message (most recent)
                    messages = await self.page.query_selector_all(self.SELECTORS["dm_content"])
                    if messages:
                        content = await messages[-1].inner_text()
                    else:
                        content = ""

                    # Create SocialInteractionSchema
                    interaction = SocialInteractionSchema(
                        platform="instagram",
                        interaction_type="dm",
                        author=sender,
                        content=content,
                        timestamp=start_time,
                        detected_at=start_time,
                        priority="MEDIUM",  # DMs are typically important
                        priority_reason="Direct Message from user"
                    )

                    interactions.append(interaction)
                    self.logger.debug(f"Extracted DM from {sender}: {content[:50]}")

                except Exception as e:
                    self.logger.error(f"Error extracting DM {i}: {e}")
                    continue

        except PlaywrightTimeoutError:
            self.logger.warning("No DMs found on Instagram")

        return interactions

    async def _check_comments(self) -> List[SocialInteractionSchema]:
        """
        Check for new comments on user's posts.

        Returns:
            List of SocialInteractionSchema objects for comments
        """
        interactions = []
        start_time = datetime.now()

        try:
            # Navigate to notifications page
            await self.page.goto("https://www.instagram.com/notifications/", wait_until="networkidle")
            await self.page.wait_for_timeout(3000)

            # Instagram notifications are harder to parse via selectors
            # We'll look for text that indicates comments
            # This is a simplified version - could be enhanced with more specific selectors

            # Look for notification elements
            notif_elements = await self.page.query_selector_all(self.SELECTORS["notification_item"])

            self.logger.info(f"Found {len(notif_elements)} notification elements")

            # Process notifications (limit to last 10)
            for i, notif_el in enumerate(notif_elements[:10]):
                try:
                    # Get notification text
                    notif_text = await notif_el.inner_text()

                    # Filter for comments (look for "commented on" text)
                    if "commented on" not in notif_text.lower() and "mentioned you in" not in notif_text.lower():
                        continue

                    # Extract username (simplified - would need better parsing)
                    # This is a placeholder - real implementation would need more robust parsing
                    author = "Instagram User"  # Would parse from notification text
                    content = notif_text  # Use full notification as content for now

                    # Try to find post URL
                    link_elem = await notif_el.query_selector("a[href*='/p/']")
                    post_url = await link_elem.get_attribute("href") if link_elem else None

                    # Create SocialInteractionSchema
                    interaction = SocialInteractionSchema(
                        platform="instagram",
                        interaction_type="comment",
                        author=author,
                        content=content,
                        post_url=f"https://www.instagram.com{post_url}" if post_url else None,
                        timestamp=start_time,
                        detected_at=start_time,
                        priority="LOW",  # Will be updated by keyword filter
                    )

                    interactions.append(interaction)
                    self.logger.debug(f"Extracted Instagram comment: {notif_text[:50]}")

                except Exception as e:
                    self.logger.error(f"Error extracting comment {i}: {e}")
                    continue

        except PlaywrightTimeoutError:
            self.logger.warning("No comments found on Instagram notifications")

        return interactions

    def extract_interactions(self, raw_data: dict) -> List[SocialInteractionSchema]:
        """
        Extract interactions from raw Instagram data.

        This method is used when we have JSON/API data instead of HTML.
        Currently not used but kept for future extensibility.

        Args:
            raw_data: Raw Instagram data (JSON, etc.)

        Returns:
            List of SocialInteractionSchema objects

        Raises:
            ValueError: If raw_data is malformed
        """
        # This would be used if we had Instagram API access
        # For browser automation, we use check_notifications() directly
        raise NotImplementedError("Use check_notifications() for browser automation")
