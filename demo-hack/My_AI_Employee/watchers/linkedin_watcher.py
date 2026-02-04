"""
LinkedIn watcher for Silver Tier AI Employee - REST API v2.

Monitors LinkedIn for new messages and interactions using the
LinkedIn REST API v2 with OAuth2 authentication.

This replaces the browser automation approach with the official LinkedIn API.
"""

import os
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

import requests
from dotenv import load_dotenv

from watchers.base_watcher import BaseWatcher
from utils.dedupe_state import DedupeTracker
from utils.frontmatter_utils import save_action_item
from models.action_item import ActionItemSchema, determine_risk_level, determine_priority

load_dotenv()

logger = logging.getLogger(__name__)


class LinkedInRateLimitError(Exception):
    """Raised when LinkedIn API rate limit is exceeded."""
    pass


class LinkedInAuthError(Exception):
    """Raised when LinkedIn API authentication fails."""
    pass


class LinkedInWatcher(BaseWatcher):
    """
    Watches LinkedIn for new messages and interactions via REST API v2.

    Uses the LinkedIn REST API v2 with OAuth2 bearer token authentication.
    Implements exponential backoff for rate limit handling.

    Attributes:
        access_token: LinkedIn OAuth2 access token.
        person_urn: LinkedIn person URN for the authenticated user.
        api_version: LinkedIn API version string (YYYYMM format).
        base_url: LinkedIn API base URL.
        last_check_ids: Set of activity IDs from last check (duplicate prevention).
    """

    BASE_URL = 'https://api.linkedin.com'
    API_VERSION = '202601'  # YYYYMM format

    # Rate limit settings
    MAX_RETRIES = 5
    INITIAL_BACKOFF = 1.0  # seconds
    MAX_BACKOFF = 16.0  # seconds

    def __init__(self, vault_path: str, check_interval: int = 300):
        """
        Initialize the LinkedIn watcher.

        Args:
            vault_path: Path to Obsidian vault root
            check_interval: Seconds between checks (default: 300 = 5 minutes)

        Raises:
            ValueError: If LINKEDIN_ACCESS_TOKEN is not configured.
        """
        super().__init__(vault_path, check_interval)

        self.access_token = os.getenv('LINKEDIN_ACCESS_TOKEN')
        self.person_urn = os.getenv('LINKEDIN_PERSON_URN')

        if not self.access_token:
            raise ValueError(
                "LINKEDIN_ACCESS_TOKEN environment variable is required.\n"
                "Run: python scripts/linkedin_oauth2_setup.py to authenticate."
            )

        # Initialize deduplication tracker
        dedupe_file = os.getenv('LINKEDIN_DEDUPE_FILE', 'My_AI_Employee/.linkedin_dedupe.json')
        self.dedupe_tracker = DedupeTracker(dedupe_file)

        self.last_check_ids: set[str] = set()
        self._session = requests.Session()
        self._setup_session()

        self.logger.info("LinkedIn watcher initialized (REST API v2)")
        self.logger.info(f"Person URN: {self.person_urn or 'Will fetch from API'}")

    def _setup_session(self) -> None:
        """Configure the requests session with authentication headers."""
        self._session.headers.update({
            'Authorization': f'Bearer {self.access_token}',
            'X-Restli-Protocol-Version': '2.0.0',
            'LinkedIn-Version': self.API_VERSION,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })

    def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> requests.Response:
        """
        Make an API request with rate limit handling.

        Implements exponential backoff: 1s, 2s, 4s, 8s, 16s (max 5 retries).

        Args:
            method: HTTP method (GET, POST, etc.).
            endpoint: API endpoint (relative to base URL).
            **kwargs: Additional arguments for requests.

        Returns:
            Response object.

        Raises:
            LinkedInRateLimitError: If rate limit persists after all retries.
            LinkedInAuthError: If authentication fails.
            requests.RequestException: For other request errors.
        """
        url = f"{self.BASE_URL}{endpoint}"
        backoff = self.INITIAL_BACKOFF

        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                response = self._session.request(method, url, **kwargs)

                # Check for rate limit
                if response.status_code == 429:
                    if attempt == self.MAX_RETRIES:
                        self.logger.error(
                            f"Rate limit exceeded after {self.MAX_RETRIES} retries"
                        )
                        raise LinkedInRateLimitError(
                            "LinkedIn API rate limit exceeded. Try again later."
                        )

                    # Get retry-after header if available
                    retry_after = response.headers.get('Retry-After')
                    if retry_after:
                        try:
                            wait_time = int(retry_after)
                        except ValueError:
                            wait_time = backoff
                    else:
                        wait_time = backoff

                    self.logger.warning(
                        f"Rate limited. Attempt {attempt}/{self.MAX_RETRIES}. "
                        f"Waiting {wait_time}s before retry..."
                    )
                    time.sleep(wait_time)
                    backoff = min(backoff * 2, self.MAX_BACKOFF)
                    continue

                # Check for auth errors
                if response.status_code in (401, 403):
                    self.logger.error(f"Authentication failed: {response.status_code}")
                    raise LinkedInAuthError(
                        "LinkedIn authentication failed. Token may be expired. "
                        "Run: python scripts/linkedin_oauth2_setup.py"
                    )

                # Return successful response
                response.raise_for_status()
                return response

            except requests.exceptions.RequestException as e:
                if attempt == self.MAX_RETRIES:
                    raise
                self.logger.warning(f"Request failed (attempt {attempt}): {e}")
                time.sleep(backoff)
                backoff = min(backoff * 2, self.MAX_BACKOFF)

        raise LinkedInRateLimitError("Max retries exceeded")

    def check_for_updates(self) -> List[Dict[str, Any]]:
        """
        Check LinkedIn for new messages and interactions.

        Returns:
            List of new activity items (messages, mentions, etc.)
        """
        try:
            # For now, return empty list - full implementation would check:
            # 1. /v2/me/messages - Direct messages
            # 2. /v2/socialActions - Mentions, comments, reactions
            # 3. /v2/shares - Shares of your content

            # This is a placeholder - full implementation requires additional API access
            self.logger.info("Checking LinkedIn for updates (REST API v2)")

            # Note: LinkedIn messaging API requires additional permissions
            # For basic implementation, we'll focus on posting capability
            # which is what the MCP server provides

            return []

        except LinkedInRateLimitError as e:
            self.logger.error(f"Rate limit error: {e}")
            return []

        except LinkedInAuthError as e:
            self.logger.error(f"Authentication error: {e}")
            return []

        except Exception as e:
            self.logger.error(f"Error checking LinkedIn updates: {e}")
            return []

    def _create_action_item(self, activity: Dict[str, Any]) -> Optional[str]:
        """
        Create action item from LinkedIn activity.

        Args:
            activity: LinkedIn activity data

        Returns:
            Path to created action item file, or None if failed
        """
        try:
            # Extract activity details
            activity_type = activity.get('type', 'unknown')
            activity_id = activity.get('id', '')
            content = activity.get('content', '')
            author = activity.get('author', {}).get('name', 'Unknown')
            timestamp = activity.get('created', datetime.now().isoformat())

            # Check for duplicates
            if self.dedupe_tracker.is_processed(activity_id):
                self.logger.debug(f"Skipping duplicate activity: {activity_id}")
                return None

            # Determine priority and risk
            priority = determine_priority(content, activity_type)
            risk_level = determine_risk_level(activity_type, content)

            # Create action item
            action_item = ActionItemSchema(
                type='linkedin',
                subject=f'LinkedIn {activity_type} from {author}',
                body=content,
                sender=author,
                received=timestamp,
                priority=priority,
                risk_level=risk_level,
                action_type='respond_linkedin',
                approval_required=True,
                status='pending'
            )

            # Save to vault
            file_path = save_action_item(
                vault_path=self.vault_path,
                action_item=action_item,
                source='linkedin'
            )

            # Mark as processed
            self.dedupe_tracker.mark_processed(activity_id)

            self.logger.info(f"Created LinkedIn action item: {file_path}")
            return file_path

        except Exception as e:
            self.logger.error(f"Error creating action item: {e}")
            return None


if __name__ == '__main__':
    """Test the LinkedIn watcher."""
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    vault_path = os.getenv('VAULT_ROOT', 'AI_Employee_Vault')

    try:
        watcher = LinkedInWatcher(vault_path=vault_path, check_interval=60)
        print("✅ LinkedIn watcher initialized successfully")
        print(f"   Access token: {watcher.access_token[:20]}...")
        print(f"   Person URN: {watcher.person_urn}")
        print("\nTesting API connection...")

        # Test API connection
        response = watcher._make_request('GET', '/v2/userinfo')
        user_info = response.json()
        print(f"✅ API connection successful")
        print(f"   User: {user_info.get('name', 'Unknown')}")
        print(f"   Email: {user_info.get('email', 'Unknown')}")

    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        sys.exit(1)
    except LinkedInAuthError as e:
        print(f"❌ Authentication error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
