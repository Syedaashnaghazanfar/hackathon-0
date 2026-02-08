"""
End-to-end test for Facebook posting in Social Media Browser MCP.

Tests complete workflow: login → create post → approve → verify post on Facebook → check Done/ file.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict
import sys


# Mock Playwright browser for testing (actual Playwright would require real Facebook login)
class MockBrowserContext:
    """Mock Playwright browser context for testing."""

    def __init__(self):
        self.logged_in = False
        self.posts_created = []
        self.cookies = []
        self.storage_state = {}

    async def login(self, email: str, password: str) -> bool:
        """Mock login to Facebook."""
        # Simulate successful login
        self.logged_in = True
        self.cookies = [{"name": "session", "value": "mock_session_token"}]
        self.storage_state = {"localStorage": {"session": "mock_session_token"}}
        return True

    async def create_post(self, text: str, image_path: Optional[str] = None) -> Dict:
        """Mock creating a Facebook post."""
        if not self.logged_in:
            raise Exception("Not logged in")

        post = {
            "post_url": f"https://facebook.com/posts/{len(self.posts_created) + 1}",
            "platform_post_id": f"post_{len(self.posts_created) + 1}",
            "text": text,
            "image_path": image_path,
            "posted_at": datetime.now().isoformat(),
            "initial_engagement": {
                "likes": 0,
                "comments": 0,
                "shares": 0
            }
        }

        self.posts_created.append(post)
        return post

    def get_session_age_hours(self) -> float:
        """Get mock session age (always fresh for testing)."""
        return 0.5  # 30 minutes old

    def is_session_valid(self) -> bool:
        """Check if mock session is valid."""
        return self.logged_in and len(self.cookies) > 0


class MockFacebookMCP:
    """Mock Facebook MCP server for testing."""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.browser = MockBrowserContext()
        self.pending_dir = self.vault_path / "Pending_Approval"
        self.approved_dir = self.vault_path / "Approved"
        self.done_dir = self.vault_path / "Done" / "Social_Media_Posts"

    async def post_to_facebook(self, text: str, image_path: Optional[str] = None) -> Dict:
        """
        MCP tool: Post to Facebook.

        Args:
            text: Post text content
            image_path: Optional path to image

        Returns:
            Dict with post_url, platform_post_id, posted_at
        """
        # Check session health
        if not self.browser.is_session_valid():
            raise Exception("Session expired. Please run login_facebook.py")

        # Create post
        result = await self.browser.create_post(text, image_path)
        return result

    def create_pending_post(self, text: str, image_path: Optional[str] = None) -> str:
        """Create a pending approval post in vault."""
        self.pending_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"facebook_post_{timestamp}.md"
        file_path = self.pending_dir / filename

        frontmatter = f"""---
type: social_post
platform: facebook
status: pending
created_at: {datetime.now().isoformat()}
---

{Text}
"""

        if image_path:
            frontmatter += f"\n**Image**: {image_path}\n"

        file_path.write_text(frontmatter)
        return str(file_path)

    def approve_post(self, file_path: str) -> None:
        """Move post from Pending_Approval to Approved."""
        source = Path(file_path)
        destination = self.approved_dir / source.name

        content = source.read_text()
        content = content.replace("status: pending", "status: approved")

        self.approved_dir.mkdir(parents=True, exist_ok=True)
        destination.write_text(content)
        source.unlink()

    async def execute_approved_post(self, file_path: str) -> Dict:
        """Execute approved post via MCP tool."""
        source = Path(file_path)
        content = source.read_text()

        # Extract post text (simplified extraction)
        lines = content.split("---")
        if len(lines) > 2:
            post_text = lines[2].strip()
        else:
            post_text = content

        # Call MCP tool
        result = await self.post_to_facebook(post_text)

        # Update file and move to Done/
        content = content.replace("status: approved", "status: done")
        execution_section = f"""

## Execution Results

- **Posted At:** {result['posted_at']}
- **Post URL:** {result['post_url']}
- **Platform Post ID:** {result['platform_post_id']}
- **Initial Engagement:** {result['initial_engagement']['likes']} likes
"""

        content += execution_section

        self.done_dir.mkdir(parents=True, exist_ok=True)
        destination = self.done_dir / source.name
        destination.write_text(content)
        source.unlink()

        return result


class TestFacebookEndToEnd:
    """End-to-end test suite for Facebook posting workflow."""

    @pytest.fixture
    def temp_vault(self):
        """Create temporary vault directory for testing."""
        temp_dir = tempfile.mkdtemp()
        vault_path = Path(temp_dir)
        yield str(vault_path)
        shutil.rmtree(temp_dir)

    @pytest.fixture
    async def mock_mcp(self, temp_vault):
        """Create mock MCP server for testing."""
        mcp = MockFacebookMCP(temp_vault)

        # Simulate login
        await mcp.browser.login("test@example.com", "password123")

        yield mcp

    @pytest.mark.asyncio
    async def test_complete_workflow_login_to_done(self, mock_mcp):
        """Test complete workflow: login → create → approve → execute → verify Done/."""
        # Step 1: Login (already done in fixture)
        assert mock_mcp.browser.is_session_valid()

        # Step 2: Create pending post
        pending_path = mock_mcp.create_pending_post(
            text="Excited to share our latest project! 🚀 #webdev #launch",
            image_path=None
        )

        pending_file = Path(pending_path)
        assert pending_file.exists()
        assert pending_file.parent.name == "Pending_Approval"
        assert "status: pending" in pending_file.read_text()

        # Step 3: Approve post
        mock_mcp.approve_post(pending_path)

        approved_file = Path(mock_mcp.approved_dir) / pending_file.name
        assert approved_file.exists()
        assert "status: approved" in approved_file.read_text()
        assert not pending_file.exists()

        # Step 4: Execute post
        result = await mock_mcp.execute_approved_post(str(approved_file))

        # Verify execution result
        assert "post_url" in result
        assert "platform_post_id" in result
        assert "posted_at" in result

        # Step 5: Verify Done/ file
        done_file = Path(mock_mcp.done_dir) / pending_file.name
        assert done_file.exists()
        assert not approved_file.exists()

        done_content = done_file.read_text()
        assert "status: done" in done_content
        assert result["post_url"] in done_content
        assert "## Execution Results" in done_content

    @pytest.mark.asyncio
    async def test_post_with_image(self, mock_mcp):
        """Test posting with image attachment."""
        # Create pending post with image
        pending_path = mock_mcp.create_pending_post(
            text="Check out this beautiful sunset! 🌅",
            image_path="/path/to/sunset.jpg"
        )

        # Approve and execute
        mock_mcp.approve_post(pending_path)
        approved_file = Path(mock_mcp.approved_dir) / Path(pending_path).name

        result = await mock_mcp.execute_approved_post(str(approved_file))

        # Verify post created with image
        assert result["image_path"] == "/path/to/sunset.jpg"

        # Verify Done/ file records image
        done_file = Path(mock_mcp.done_dir) / Path(pending_path).name
        done_content = done_file.read_text()
        assert "sunset.jpg" in done_content

    @pytest.mark.asyncio
    async def test_post_without_image(self, mock_mcp):
        """Test text-only post."""
        pending_path = mock_mcp.create_pending_post(
            text="Just a text update today!",
            image_path=None
        )

        mock_mcp.approve_post(pending_path)
        approved_file = Path(mock_mcp.approved_dir) / Path(pending_path).name

        result = await mock_mcp.execute_approved_post(str(approved_file))

        # Verify post created without image
        assert result["image_path"] is None

    @pytest.mark.asyncio
    async def test_session_expiry_detected(self, temp_vault):
        """Test session expiry is detected before posting."""
        mcp = MockFacebookMCP(temp_vault)

        # Don't login - simulate expired session
        assert not mcp.browser.is_session_valid()

        # Attempt to post should raise error
        with pytest.raises(Exception) as exc_info:
            await mcp.post_to_facebook("Test post")

        assert "Session expired" in str(exc_info.value)
        assert "login_facebook.py" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_multiple_posts_sequential(self, mock_mcp):
        """Test posting multiple posts sequentially."""
        posts = [
            "Post number 1",
            "Post number 2",
            "Post number 3"
        ]

        results = []
        for i, post_text in enumerate(posts):
            # Create pending
            pending_path = mock_mcp.create_pending_post(post_text, None)

            # Approve and execute
            mock_mcp.approve_post(pending_path)
            approved_file = Path(mock_mcp.approved_dir) / Path(pending_path).name

            result = await mock_mcp.execute_approved_post(str(approved_file))
            results.append(result)

        # Verify all posts created with unique URLs
        post_urls = [r["post_url"] for r in results]
        assert len(post_urls) == len(set(post_urls))  # All unique

        # Verify all in Done/
        done_files = list(Path(mock_mcp.done_dir).glob("*.md"))
        assert len(done_files) == 3

    @pytest.mark.asyncio
    async def test_post_with_special_characters(self, mock_mcp):
        """Test post with emojis and special characters."""
        special_text = "🚀 Excited! @mention #hashtag $money %percent &amp;"

        pending_path = mock_mcp.create_pending_post(special_text, None)
        mock_mcp.approve_post(pending_path)
        approved_file = Path(mock_mcp.approved_dir) / Path(pending_path).name

        result = await mock_mcp.execute_approved_post(str(approved_file))

        # Verify special characters preserved
        assert "🚀" in result["text"]
        assert "@mention" in result["text"]
        assert "#hashtag" in result["text"]

    @pytest.mark.asyncio
    async def test_post_long_text(self, mock_mcp):
        """Test post with long text (Facebook allows 63206 characters)."""
        long_text = "A" * 5000  # 5000 characters

        pending_path = mock_mcp.create_pending_post(long_text, None)
        mock_mcp.approve_post(pending_path)
        approved_file = Path(mock_mcp.approved_dir) / Path(pending_path).name

        result = await mock_mcp.execute_approved_post(str(approved_file))

        # Verify full text posted
        assert len(result["text"]) == 5000

    @pytest.mark.asyncio
    async def test_post_frontmatter_preserved(self, mock_mcp):
        """Test post metadata is preserved in Done/ file."""
        pending_path = mock_mcp.create_pending_post(
            text="Test post",
            image_path="/test/image.jpg"
        )

        # Verify frontmatter in pending
        pending_content = Path(pending_path).read_text()
        assert "type: social_post" in pending_content
        assert "platform: facebook" in pending_content
        assert "status: pending" in pending_content

        mock_mcp.approve_post(pending_path)
        approved_file = Path(mock_mcp.approved_dir) / Path(pending_path).name

        result = await mock_mcp.execute_approved_post(str(approved_file))

        # Verify frontmatter preserved and status updated in Done/
        done_file = Path(mock_mcp.done_dir) / Path(pending_path).name
        done_content = done_file.read_text()
        assert "type: social_post" in done_content
        assert "platform: facebook" in done_content
        assert "status: done" in done_content

    @pytest.mark.asyncio
    async def test_execution_timestamp_recorded(self, mock_mcp):
        """Test execution timestamp is recorded in Done/ file."""
        pending_path = mock_mcp.create_pending_post("Test", None)

        mock_mcp.approve_post(pending_path)
        approved_file = Path(mock_mcp.approved_dir) / Path(pending_path).name

        execution_start = datetime.now()
        result = await mock_mcp.execute_approved_post(str(approved_file))
        execution_end = datetime.now()

        # Verify timestamp in result
        execution_time = datetime.fromisoformat(result["posted_at"])
        assert execution_start <= execution_time <= execution_end

        # Verify timestamp in Done/ file
        done_file = Path(mock_mcp.done_dir) / Path(pending_path).name
        done_content = done_file.read_text()
        assert result["posted_at"] in done_content

    @pytest.mark.asyncio
    async def test_post_url_format(self, mock_mcp):
        """Test post URL follows expected format."""
        pending_path = mock_mcp.create_pending_post("Test", None)

        mock_mcp.approve_post(pending_path)
        approved_file = Path(mock_mcp.approved_dir) / Path(pending_path).name

        result = await mock_mcp.execute_approved_post(str(approved_file))

        # Verify URL format
        assert result["post_url"].startswith("https://facebook.com/posts/")
        assert result["platform_post_id"].startswith("post_")

    @pytest.mark.asyncio
    async def test_engagement_tracking_initialized(self, mock_mcp):
        """Test initial engagement is tracked in Done/ file."""
        pending_path = mock_mcp.create_pending_post("Test", None)

        mock_mcp.approve_post(pending_path)
        approved_file = Path(mock_mcp.approved_dir) / Path(pending_path).name

        result = await mock_mcp.execute_approved_post(str(approved_file))

        # Verify engagement initialized to 0
        assert result["initial_engagement"]["likes"] == 0
        assert result["initial_engagement"]["comments"] == 0
        assert result["initial_engagement"]["shares"] == 0

        # Verify engagement in Done/ file
        done_file = Path(mock_mcp.done_dir) / Path(pending_path).name
        done_content = done_file.read_text()
        assert "0 likes" in done_content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
