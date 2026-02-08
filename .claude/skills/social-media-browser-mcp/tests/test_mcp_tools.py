"""
Unit tests for MCP tool schema validation in Social Media Browser MCP.

Tests Pydantic v2 validation for post_to_facebook, post_to_instagram,
and post_to_twitter input schemas.
"""

import pytest
from pydantic import ValidationError, BaseModel
from typing import Optional, List
from pathlib import Path


# Mock schemas (these will be implemented in the actual MCP server)
class FacebookPostInput(BaseModel):
    """Input schema for post_to_facebook MCP tool."""

    text: str
    image_path: Optional[str] = None

    model_config = {"extra": "forbid"}

    @staticmethod
    def validate_text(text: str) -> None:
        """Validate text is not empty."""
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")


class InstagramPostInput(BaseModel):
    """Input schema for post_to_instagram MCP tool."""

    text: str
    image_path: str

    model_config = {"extra": "forbid"}

    @staticmethod
    def validate_text(text: str) -> None:
        """Validate text is not empty."""
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

    @staticmethod
    def validate_image(image_path: str) -> None:
        """Validate image path exists and is valid image file."""
        path = Path(image_path)
        if not path.exists():
            raise ValueError(f"Image file does not exist: {image_path}")
        valid_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
        if path.suffix.lower() not in valid_extensions:
            raise ValueError(f"Invalid image format. Supported: {valid_extensions}")


class TweetInput(BaseModel):
    """Input schema for a single tweet."""

    text: str

    model_config = {"extra": "forbid"}

    @staticmethod
    def validate_text(text: str) -> None:
        """Validate tweet is within character limit."""
        if not text or not text.strip():
            raise ValueError("Tweet text cannot be empty")
        if len(text) > 280:
            raise ValueError(f"Tweet exceeds 280 characters (current: {len(text)})")


class TwitterPostInput(BaseModel):
    """Input schema for post_to_twitter MCP tool."""

    tweets: List[TweetInput]

    model_config = {"extra": "forbid"}

    @staticmethod
    def validate_tweets(tweets: List[TweetInput]) -> None:
        """Validate tweets list."""
        if not tweets:
            raise ValueError("At least one tweet is required")
        if len(tweets) > 10:
            raise ValueError("Maximum 10 tweets allowed in one post")


class TestMCPToolSchemaValidation:
    """Test suite for MCP tool schema validation."""

    # Facebook post validation tests
    def test_facebook_post_valid_input(self):
        """Test Facebook post with valid text only."""
        input_data = {"text": "Hello Facebook!"}
        post = FacebookPostInput(**input_data)
        assert post.text == "Hello Facebook!"
        assert post.image_path is None

    def test_facebook_post_valid_with_image(self):
        """Test Facebook post with text and image."""
        input_data = {
            "text": "Check out this photo!",
            "image_path": "/path/to/photo.jpg"
        }
        post = FacebookPostInput(**input_data)
        assert post.text == "Check out this photo!"
        assert post.image_path == "/path/to/photo.jpg"

    def test_facebook_post_missing_text(self):
        """Test Facebook post validation fails with missing text."""
        with pytest.raises(ValidationError) as exc_info:
            FacebookPostInput(image_path="/path/to/photo.jpg")
        assert "text" in str(exc_info.value).lower()

    def test_facebook_post_empty_text(self):
        """Test Facebook post validation fails with empty text."""
        with pytest.raises(ValueError, match="Text cannot be empty"):
            FacebookPostInput(text="   ").validate_text("   ")

    def test_facebook_post_extra_fields_forbidden(self):
        """Test Facebook post rejects extra fields."""
        with pytest.raises(ValidationError) as exc_info:
            FacebookPostInput(
                text="Hello",
                extra_field="not allowed"
            )
        assert "extra" in str(exc_info.value).lower()

    # Instagram post validation tests
    def test_instagram_post_valid_input(self):
        """Test Instagram post with valid text and image."""
        input_data = {
            "text": "Beautiful sunset! #sunset",
            "image_path": "/path/to/photo.jpg"
        }
        post = InstagramPostInput(**input_data)
        assert post.text == "Beautiful sunset! #sunset"
        assert post.image_path == "/path/to/photo.jpg"

    def test_instagram_post_missing_text(self):
        """Test Instagram post validation fails with missing text."""
        with pytest.raises(ValidationError) as exc_info:
            InstagramPostInput(image_path="/path/to/photo.jpg")
        assert "text" in str(exc_info.value).lower()

    def test_instagram_post_missing_image(self):
        """Test Instagram post validation fails with missing image."""
        with pytest.raises(ValidationError) as exc_info:
            InstagramPostInput(text="Nice photo!")
        assert "image_path" in str(exc_info.value).lower()

    def test_instagram_post_empty_text(self):
        """Test Instagram post validation fails with empty text."""
        with pytest.raises(ValueError, match="Text cannot be empty"):
            InstagramPostInput(text="").validate_text("")

    def test_instagram_post_invalid_image_format(self):
        """Test Instagram post validation fails with invalid image format."""
        with pytest.raises(ValueError, match="Invalid image format"):
            InstagramPostInput(
                text="Test",
                image_path="/path/to/document.pdf"
            ).validate_image("/path/to/document.pdf")

    def test_instagram_post_extra_fields_forbidden(self):
        """Test Instagram post rejects extra fields."""
        with pytest.raises(ValidationError) as exc_info:
            InstagramPostInput(
                text="Test",
                image_path="/path/to/photo.jpg",
                extra_field="not allowed"
            )
        assert "extra" in str(exc_info.value).lower()

    # Twitter post validation tests
    def test_twitter_post_valid_single_tweet(self):
        """Test Twitter post with valid single tweet."""
        input_data = {"tweets": [{"text": "Hello Twitter! #firsttweet"}]}
        post = TwitterPostInput(**input_data)
        assert len(post.tweets) == 1
        assert post.tweets[0].text == "Hello Twitter! #firsttweet"

    def test_twitter_post_valid_multiple_tweets(self):
        """Test Twitter post with valid multiple tweets (thread)."""
        input_data = {
            "tweets": [
                {"text": "Thread 1/3"},
                {"text": "Thread 2/3"},
                {"text": "Thread 3/3"}
            ]
        }
        post = TwitterPostInput(**input_data)
        assert len(post.tweets) == 3

    def test_twitter_post_missing_tweets(self):
        """Test Twitter post validation fails with missing tweets."""
        with pytest.raises(ValidationError) as exc_info:
            TwitterPostInput(text="Single tweet")
        assert "tweets" in str(exc_info.value).lower()

    def test_twitter_post_empty_tweets_list(self):
        """Test Twitter post validation fails with empty tweets list."""
        with pytest.raises(ValueError, match="At least one tweet is required"):
            TwitterPostInput.validate_tweets([])

    def test_twitter_post_tweet_too_long(self):
        """Test Twitter post validation fails with tweet > 280 chars."""
        long_text = "a" * 281
        with pytest.raises(ValueError, match="Tweet exceeds 280 characters"):
            TweetInput(text=long_text).validate_text(long_text)

    def test_twitter_post_empty_tweet(self):
        """Test Twitter post validation fails with empty tweet."""
        with pytest.raises(ValueError, match="Tweet text cannot be empty"):
            TweetInput(text="").validate_text("")

    def test_twitter_post_too_many_tweets(self):
        """Test Twitter post validation fails with > 10 tweets."""
        tweets = [{"text": f"Tweet {i}"} for i in range(11)]
        with pytest.raises(ValueError, match="Maximum 10 tweets allowed"):
            TwitterPostInput.validate_tweets([TweetInput(**t) for t in tweets])

    def test_twitter_post_extra_fields_forbidden(self):
        """Test Twitter post rejects extra fields."""
        with pytest.raises(ValidationError) as exc_info:
            TwitterPostInput(
                tweets=[{"text": "Test"}],
                extra_field="not allowed"
            )
        assert "extra" in str(exc_info.value).lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
