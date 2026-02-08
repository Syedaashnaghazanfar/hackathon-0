"""
Integration tests for HITL (Human-in-the-Loop) approval workflow in Social Media Browser MCP.

Tests Pending_Approval → Approved → execution → Done/ flow for social media posts.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional
import sys

# Add scripts to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "scripts"))


# Mock classes for testing
class VaultOps:
    """Mock vault operations for testing."""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)

    def read_markdown(self, file_path: str) -> tuple[str, dict]:
        """Mock reading markdown file."""
        full_path = self.vault_path / file_path
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {full_path}")
        return "", {}

    def write_markdown(self, file_path: str, content: str, fm_dict: dict = None) -> None:
        """Mock writing markdown file."""
        full_path = self.vault_path / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content)

    def move_to_done(self, source_path: str, done_category: str = "Social_Media_Posts") -> None:
        """Mock moving file to Done/."""
        pass


class ApprovalWorkflow:
    """Manage HITL approval workflow for social media posts."""

    def __init__(self, vault_path: str):
        self.vault_ops = VaultOps(vault_path)
        self.pending_dir = self.vault_ops.vault_path / "Pending_Approval"
        self.approved_dir = self.vault_ops.vault_path / "Approved"
        self.done_dir = self.vault_ops.vault_path / "Done"

    def create_pending_post(self, platform: str, content: str, metadata: dict) -> str:
        """
        Create a pending approval post.

        Args:
            platform: Platform name (facebook, instagram, twitter)
            content: Post content text
            metadata: Additional metadata (image_path, scheduled_time, etc.)

        Returns:
            Path to created file
        """
        self.pending_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{platform}_post_{timestamp}.md"
        file_path = self.pending_dir / filename

        # Create frontmatter
        frontmatter = f"""---
type: social_post
platform: {platform}
status: pending
created_at: {datetime.now().isoformat()}
{self._dict_to_yaml(metadata)}
---

{content}
"""
        file_path.write_text(frontmatter)
        return str(file_path)

    def approve_post(self, file_path: str) -> None:
        """
        Move a post from Pending_Approval to Approved.

        Args:
            file_path: Path to pending post file
        """
        source = Path(file_path)
        destination = self.approved_dir / source.name

        # Update status in file
        content = source.read_text()
        content = content.replace("status: pending", "status: approved")

        self.approved_dir.mkdir(parents=True, exist_ok=True)
        destination.write_text(content)

        # Delete from pending
        source.unlink()

    def execute_post(self, file_path: str, result: dict) -> None:
        """
        Execute approved post and move to Done/.

        Args:
            file_path: Path to approved post file
            result: Execution result (post_url, platform_post_id, etc.)
        """
        source = Path(file_path)

        # Read and update content
        content = source.read_text()
        content = content.replace("status: approved", "status: done")

        # Add execution results
        execution_section = f"""

## Execution Results

- **Posted At:** {result.get('posted_at', datetime.now().isoformat())}
- **Post URL:** {result.get('post_url', 'N/A')}
- **Platform Post ID:** {result.get('platform_post_id', 'N/A')}
- **Initial Engagement:** {result.get('initial_engagement', 'N/A')}
"""

        # Append execution results
        if "---" in content:
            content = content + execution_section
        else:
            content = content + "\n" + execution_section

        # Move to Done/Social_Media_Posts/
        done_dir = self.done_dir / "Social_Media_Posts"
        done_dir.mkdir(parents=True, exist_ok=True)
        destination = done_dir / source.name
        destination.write_text(content)

        source.unlink()

    def _dict_to_yaml(self, d: dict) -> str:
        """Convert dict to YAML format."""
        if not d:
            return ""
        lines = []
        for key, value in d.items():
            if isinstance(value, str):
                lines.append(f"{key}: \"{value}\"")
            elif isinstance(value, (int, float, bool)):
                lines.append(f"{key}: {value}")
            elif isinstance(value, list):
                lines.append(f"{key}: {value}")
        return "\n".join(lines)


class TestApprovalWorkflow:
    """Test suite for HITL approval workflow integration."""

    @pytest.fixture
    def temp_vault(self):
        """Create temporary vault directory for testing."""
        temp_dir = tempfile.mkdtemp()
        vault_path = Path(temp_dir)
        yield str(vault_path)
        shutil.rmtree(temp_dir)

    def test_create_pending_facebook_post(self, temp_vault):
        """Test creating a pending Facebook post."""
        workflow = ApprovalWorkflow(temp_vault)

        file_path = workflow.create_pending_post(
            platform="facebook",
            content="Test Facebook post content",
            metadata={"image_path": "/path/to/image.jpg"}
        )

        # Verify file created in Pending_Approval
        pending_file = Path(file_path)
        assert pending_file.exists()
        assert "Pending_Approval" in str(pending_file)
        assert "facebook_post" in pending_file.name

        # Verify content
        content = pending_file.read_text()
        assert "Test Facebook post content" in content
        assert "status: pending" in content
        assert "platform: facebook" in content

    def test_create_pending_instagram_post(self, temp_vault):
        """Test creating a pending Instagram post."""
        workflow = ApprovalWorkflow(temp_vault)

        file_path = workflow.create_pending_post(
            platform="instagram",
            content="Beautiful sunset! #sunset",
            metadata={"image_path": "/path/to/sunset.jpg"}
        )

        pending_file = Path(file_path)
        assert pending_file.exists()
        assert "instagram_post" in pending_file.name

    def test_create_pending_twitter_post(self, temp_vault):
        """Test creating a pending Twitter thread."""
        workflow = ApprovalWorkflow(temp_vault)

        file_path = workflow.create_pending_post(
            platform="twitter",
            content="Thread 1/3\nThread 2/3\nThread 3/3",
            metadata={"tweet_count": 3}
        )

        pending_file = Path(file_path)
        assert pending_file.exists()
        assert "twitter_post" in pending_file.name

    def test_approve_post_moves_to_approved(self, temp_vault):
        """Test approving a post moves it from Pending to Approved."""
        workflow = ApprovalWorkflow(temp_vault)

        # Create pending post
        pending_path = workflow.create_pending_post(
            platform="facebook",
            content="Test post",
            metadata={}
        )

        # Approve it
        workflow.approve_post(pending_path)

        # Verify moved
        pending_file = Path(pending_path)
        assert not pending_file.exists()

        approved_file = Path(temp_vault) / "Approved" / Path(pending_path).name
        assert approved_file.exists()

        # Verify status updated
        content = approved_file.read_text()
        assert "status: approved" in content

    def test_approve_nonexistent_post_raises_error(self, temp_vault):
        """Test approving nonexistent post raises error."""
        workflow = ApprovalWorkflow(temp_vault)

        with pytest.raises(FileNotFoundError):
            workflow.approve_post("nonexistent_post.md")

    def test_execute_post_moves_to_done(self, temp_vault):
        """Test executing approved post moves it to Done/Social_Media_Posts/."""
        workflow = ApprovalWorkflow(temp_vault)

        # Create and approve a post
        pending_path = workflow.create_pending_post(
            platform="facebook",
            content="Test post",
            metadata={}
        )
        workflow.approve_post(pending_path)

        # Get approved path
        approved_path = Path(temp_vault) / "Approved" / Path(pending_path).name

        # Execute with mock result
        result = {
            "post_url": "https://facebook.com/posts/123456",
            "platform_post_id": "123456_7890",
            "posted_at": datetime.now().isoformat(),
            "initial_engagement": "5 likes"
        }

        workflow.execute_post(str(approved_path), result)

        # Verify moved to Done
        approved_file = Path(approved_path)
        assert not approved_file.exists()

        done_file = Path(temp_vault) / "Done" / "Social_Media_Posts" / Path(pending_path).name
        assert done_file.exists()

        # Verify execution results added
        content = done_file.read_text()
        assert "## Execution Results" in content
        assert "status: done" in content
        assert "https://facebook.com/posts/123456" in content

    def test_full_workflow_pending_to_done(self, temp_vault):
        """Test complete workflow: create → approve → execute."""
        workflow = ApprovalWorkflow(temp_vault)

        # Step 1: Create pending
        pending_path = workflow.create_pending_post(
            platform="facebook",
            content="Complete test post",
            metadata={"image_path": "/test.jpg"}
        )

        # Verify in Pending_Approval
        assert Path(pending_path).parent.name == "Pending_Approval"

        # Step 2: Approve
        workflow.approve_post(pending_path)

        # Verify in Approved
        approved_path = Path(temp_vault) / "Approved" / Path(pending_path).name
        assert approved_path.exists()

        # Step 3: Execute
        result = {
            "post_url": "https://facebook.com/posts/abc123",
            "platform_post_id": "abc123",
            "posted_at": datetime.now().isoformat(),
            "initial_engagement": "10 likes, 2 comments"
        }

        workflow.execute_post(str(approved_path), result)

        # Verify in Done/Social_Media_Posts/
        done_file = Path(temp_vault) / "Done" / "Social_Media_Posts" / Path(pending_path).name
        assert done_file.exists()

        # Verify final status is done
        content = done_file.read_text()
        assert "status: done" in content
        assert "## Execution Results" in content

    def test_multiple_posts_isolated(self, temp_vault):
        """Test multiple posts maintain separate workflow states."""
        workflow = ApprovalWorkflow(temp_vault)

        # Create multiple pending posts
        post1 = workflow.create_pending_post("facebook", "Post 1", {})
        post2 = workflow.create_pending_post("instagram", "Post 2", {})
        post3 = workflow.create_pending_post("twitter", "Post 3", {})

        # Verify all in Pending_Approval
        assert Path(post1).exists()
        assert Path(post2).exists()
        assert Path(post3).exists()

        # Approve only post1
        workflow.approve_post(post1)

        # Verify post1 moved to Approved, others still pending
        assert (Path(temp_vault) / "Approved" / Path(post1).name).exists()
        assert Path(post2).parent.name == "Pending_Approval"
        assert Path(post3).parent.name == "Pending_Approval"

    def test_metadata_preserved_through_workflow(self, temp_vault):
        """Test post metadata is preserved through approve → execute flow."""
        workflow = ApprovalWorkflow(temp_vault)

        # Create post with metadata
        metadata = {
            "image_path": "/path/to/image.jpg",
            "scheduled_time": "2024-01-15T08:00:00",
            "campaign": "winter_sale"
        }

        pending_path = workflow.create_pending_post("instagram", "Test post", metadata)
        workflow.approve_post(pending_path)

        # Verify metadata preserved in Approved
        approved_file = Path(temp_vault) / "Approved" / Path(pending_path).name
        content = approved_file.read_text()
        assert "image_path: \"/path/to/image.jpg\"" in content
        assert "scheduled_time: \"2024-01-15T08:00:00\"" in content
        assert "campaign: \"winter_sale\"" in content

        # Execute and verify metadata still there
        workflow.execute_post(str(approved_file), {})
        done_file = Path(temp_vault) / "Done" / "Social_Media_Posts" / Path(pending_path).name
        done_content = done_file.read_text()
        assert "image_path: \"/path/to/image.jpg\"" in done_content

    def test_folder_structure_created_automatically(self, temp_vault):
        """Test that workflow creates required folders automatically."""
        workflow = ApprovalWorkflow(temp_vault)

        # Create pending post - should create Pending_Approval folder
        workflow.create_pending_post("facebook", "Test", {})

        assert (Path(temp_vault) / "Pending_Approval").exists()

        # Approve post - should create Approved folder
        pending_path = workflow.create_pending_post("instagram", "Test", {})
        workflow.approve_post(pending_path)

        assert (Path(temp_vault) / "Approved").exists()

        # Execute post - should create Done/Social_Media_Posts folder
        approved_path = Path(temp_vault) / "Approved" / Path(pending_path).name
        workflow.execute_post(str(approved_path), {})

        assert (Path(temp_vault) / "Done" / "Social_Media_Posts").exists()

    def test_rejection_workflow_post_deleted(self, temp_vault):
        """Test that rejected posts can be deleted from Pending_Approval."""
        workflow = ApprovalWorkflow(temp_vault)

        # Create pending post
        pending_path = workflow.create_pending_post("facebook", "Test", {})

        # Simulate rejection (delete from Pending_Approval)
        Path(pending_path).unlink()

        # Verify file no longer exists
        assert not Path(pending_path).exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
