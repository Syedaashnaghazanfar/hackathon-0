"""
Facebook Monitor for Gold Tier AI Employee.

Detects comments and reactions on user's Facebook posts using browser automation.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from playwright.async_api import async_playwright, Browser, Page, TimeoutError as PlaywrightTimeoutError

from .base_monitor import BaseSocialMonitor, SessionExpiredError, PlatformError
from ..models.social_interaction import SocialInteractionSchema


logger = logging.getLogger(__name__)


class FacebookMonitor(BaseSocialMonitor):
    """
    Monitor for Facebook notifications and interactions.

    Detects:
    - Comments on user's posts
    - Reactions on user's posts
    - Replies to user's comments

    Uses existing Facebook session from .social_session/facebook/
    """

    PLATFORM = "facebook"

    # Facebook-specific selectors
    SELECTORS = {
        # Notification bell icon
        "notification_bell": "div[aria-label='Notifications'], div[aria-label='Account Services']",

        # Comments on posts
        "comment_text": "[data-testid='comment'] span[dir='auto']",
        "comment_author": "[data-testid='comment'] a[href*='/user/'], [data-testid='comment'] a[href*='/profile.php']",
        "comment_link": "a[href*='/posts/'], a[href*='/photos/'], a[href*='/permalink.php']",

        # Reactions
        "reaction_button": "[aria-label*='react'], [aria-label*='Like']",

        # Login check
        "login_form": "form[data-testid='royal_login_form']",

        # Page notifications (for business pages)
        "page_notifications": "a[href*='/pages/notifications']",
        "unread_notif": "span[data-overviewcontext='RefinedNotificationsContext'] div[class*='x1i10hfl']",
    }

    def __init__(self, session_dir: Optional[Path] = None):
        """Initialize Facebook monitor."""
        super().__init__(session_dir)
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None

    async def check_notifications(self) -> List[SocialInteractionSchema]:
        """
        Check for new Facebook notifications (comments, reactions).

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
                    headless=False,  # Facebook requires visible browser
                    viewport={"width": 1280, "height": 720},
                )

                self.page = await self.browser.new_page()

                # Navigate to Facebook
                await self.page.goto("https://www.facebook.com/", wait_until="networkidle")

                # Check if logged in
                if await self.page.query_selector(self.SELECTORS["login_form"]):
                    raise SessionExpiredError("Not logged in - login form detected")

                # Navigate to notifications
                await self._navigate_to_notifications()

                # Extract comments
                comments = await self._extract_comments()
                interactions.extend(comments)

                # Extract reactions (optional - can be resource intensive)
                # reactions = await self._extract_reactions()
                # interactions.extend(reactions)

                self.logger.info(f"Extracted {len(interactions)} Facebook interactions")

            except PlaywrightTimeoutError as e:
                self.logger.error(f"Timeout waiting for Facebook elements: {e}")
                raise PlatformError(f"Facebook navigation timeout: {e}")

            except Exception as e:
                self.logger.error(f"Error checking Facebook notifications: {e}")
                raise PlatformError(f"Facebook check failed: {e}")

            finally:
                # Always close browser
                if self.browser:
                    await self.browser.close()

        return interactions

    async def _navigate_to_notifications(self) -> None:
        """
        Navigate to Facebook notifications page.

        This method tries multiple approaches:
        1. Click notification bell icon
        2. Navigate to notifications URL directly
        3. Check page notifications (if business page)
        """
        # Try clicking notification bell
        try:
            await self.page.wait_for_selector(self.SELECTORS["notification_bell"], timeout=5000)
            await self.page.click(self.SELECTORS["notification_bell"])
            await self.page.wait_for_timeout(2000)  # Wait for menu to load
            self.logger.info("Clicked notification bell")
        except PlaywrightTimeoutError:
            # Fallback: navigate directly to notifications URL
            self.logger.warning("Could not find notification bell, navigating to notifications URL")
            await self.page.goto("https://www.facebook.com/notifications", wait_until="networkidle")

    async def _extract_comments(self) -> List[SocialInteractionSchema]:
        """
        Extract comments from Facebook notifications.

        Returns:
            List of SocialInteractionSchema objects for comments
        """
        interactions = []
        start_time = datetime.now()

        try:
            # Wait for comment elements to load
            await self.page.wait_for_selector(self.SELECTORS["comment_text"], timeout=10000)

            # Get all comment elements
            comment_elements = await self.page.query_selector_all(self.SELECTORS["comment_text"])

            self.logger.info(f"Found {len(comment_elements)} comment elements")

            # Process each comment (limit to last 10 to avoid processing too many)
            for i, comment_el in enumerate(comment_elements[:10]):
                try:
                    # Extract comment text
                    comment_text = await comment_el.inner_text()

                    # Find parent element to get author and post link
                    parent = await comment_el.evaluate_handle("el => el.closest('[data-testid=\"comment\"]')")
                    if not parent:
                        continue

                    # Extract author
                    author_elem = await parent.as_element().query_selector(self.SELECTORS["comment_author"])
                    author = await author_elem.inner_text() if author_elem else "Unknown"

                    # Extract post URL
                    link_elem = await parent.as_element().query_selector(self.SELECTORS["comment_link"])
                    post_url = await link_elem.get_attribute("href") if link_elem else None

                    # Create SocialInteractionSchema
                    interaction = SocialInteractionSchema(
                        platform="facebook",
                        interaction_type="comment",
                        author=author,
                        content=comment_text,
                        post_url=post_url if post_url else None,
                        timestamp=start_time,  # Facebook doesn't always show exact time in notifications
                        detected_at=start_time,
                        priority="LOW",  # Will be updated by keyword filter
                    )

                    interactions.append(interaction)
                    self.logger.debug(f"Extracted comment from {author}: {comment_text[:50]}")

                except Exception as e:
                    self.logger.error(f"Error extracting comment {i}: {e}")
                    continue

        except PlaywrightTimeoutError:
            self.logger.warning("No comments found on Facebook notifications page")

        return interactions

    async def _extract_reactions(self) -> List[SocialInteractionSchema]:
        """
        Extract reactions from Facebook posts.

        Note: This is more complex and may require navigating to individual posts.
        For now, we'll skip this and can implement later if needed.

        Returns:
            Empty list (placeholder)
        """
        # TODO: Implement reaction detection
        # This would require:
        # 1. Navigate to each post with new reactions
        # 2. Count reactions
        # 3. Extract reaction authors
        # 4. Create SocialInteractionSchema objects

        self.logger.info("Reaction extraction not yet implemented")
        return []

    def extract_interactions(self, raw_data: dict) -> List[SocialInteractionSchema]:
        """
        Extract interactions from raw Facebook data.

        This method is used when we have JSON/API data instead of HTML.
        Currently not used but kept for future extensibility.

        Args:
            raw_data: Raw Facebook data (JSON, etc.)

        Returns:
            List of SocialInteractionSchema objects

        Raises:
            ValueError: If raw_data is malformed
        """
        # This would be used if we had Facebook API access
        # For browser automation, we use check_notifications() directly
        raise NotImplementedError("Use check_notifications() for browser automation")
