"""Tests for hashnode_mcp.mcp_server tool functions."""
import json
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from hashnode_mcp.mcp_server import (
    _safe_get,
    _parse_tags,
    _get_user_publication_id,
    get_user_info,
    get_article_details,
    get_top_articles,
    get_articles_by_tag,
    toggle_follow_user,
    create_webhook,
    delete_article,
    publish_draft,
    get_publication_posts,
)

# Import test_api_connection with an alias to prevent pytest from collecting it
from hashnode_mcp.mcp_server import test_api_connection as _test_api_connection_tool


class TestSafeGet:
    def test_deep_path(self):
        data = {"a": {"b": {"c": "found"}}}
        assert _safe_get(data, "a", "b", "c") == "found"

    def test_missing_key(self):
        data = {"a": {"b": {}}}
        assert _safe_get(data, "a", "b", "c") is None

    def test_non_dict_intermediate(self):
        data = {"a": {"b": "string"}}
        assert _safe_get(data, "a", "b", "c") is None

    def test_with_default(self):
        assert _safe_get({}, "missing", default="fallback") == "fallback"

    def test_empty_data(self):
        assert _safe_get({}, "a", "b") is None
        assert _safe_get(None, "a", "b") is None


class TestParseTags:
    def test_single_tag(self):
        result = _parse_tags("python")
        assert len(result) == 1
        assert result[0]["name"] == "python"
        assert result[0]["slug"] == "python"

    def test_multiple_tags(self):
        result = _parse_tags("python, webdev, tutorial")
        assert len(result) == 3
        assert result[0]["slug"] == "python"
        assert result[2]["slug"] == "tutorial"

    def test_empty_string(self):
        assert _parse_tags("") == []
        assert _parse_tags(None) == []

    def test_trims_whitespace(self):
        result = _parse_tags("  python , webdev  ")
        assert result[0]["name"] == "python"
        assert result[1]["name"] == "webdev"

    def test_slug_generation(self):
        result = _parse_tags("Web Development")
        assert result[0]["slug"] == "web-development"


@pytest.fixture
def mock_publication():
    """Mock response for user publication lookup."""
    return {
        "data": {
            "me": {
                "publications": {
                    "edges": [
                        {
                            "node": {
                                "id": "pub123",
                                "title": "Test Blog",
                            }
                        }
                    ]
                }
            }
        }
    }


@pytest.fixture
def mock_fetch(mock_publication):
    """Patch fetch_from_api to return mock data."""
    with patch("hashnode_mcp.mcp_server.fetch_from_api", new_callable=AsyncMock) as mock:
        # Default: return publication for publication lookups
        mock.return_value = mock_publication
        yield mock


class TestTestApiConnection:
    @pytest.mark.asyncio
    async def test_success(self):
        with patch("hashnode_mcp.mcp_server.fetch_from_api", new_callable=AsyncMock) as mock:
            mock.return_value = {"data": {"__schema": {"queryType": {"name": "Query"}}}}
            result = await _test_api_connection_tool()
            assert "successful" in result

    @pytest.mark.asyncio
    async def test_failure(self):
        with patch("hashnode_mcp.mcp_server.fetch_from_api", new_callable=AsyncMock) as mock:
            mock.side_effect = Exception("Connection refused")
            result = await _test_api_connection_tool()
            assert "failed" in result


class TestGetUserInfo:
    @pytest.mark.asyncio
    async def test_success(self):
        mock_data = {
            "data": {
                "user": {
                    "id": "user1",
                    "name": "Test User",
                    "username": "testuser",
                    "bio": {"text": "Hello"},
                }
            }
        }
        with patch("hashnode_mcp.mcp_server.fetch_from_api", new_callable=AsyncMock) as mock:
            mock.return_value = mock_data
            result = await get_user_info("testuser")
            assert "Test User" in result

    @pytest.mark.asyncio
    async def test_user_not_found(self):
        with patch("hashnode_mcp.mcp_server.fetch_from_api", new_callable=AsyncMock) as mock:
            mock.return_value = {"data": {"user": None}}
            result = await get_user_info("nonexistent")
            assert "No user found" in result

    @pytest.mark.asyncio
    async def test_api_error(self):
        with patch("hashnode_mcp.mcp_server.fetch_from_api", new_callable=AsyncMock) as mock:
            mock.return_value = {"data": {"user": None}, "errors": [{"message": "Unauthorized"}]}
            result = await get_user_info("testuser")
            assert "API returned errors" in result


class TestGetArticleDetails:
    @pytest.mark.asyncio
    async def test_success(self):
        mock_data = {
            "data": {
                "post": {
                    "id": "post1",
                    "title": "Test Article",
                    "slug": "test-article",
                }
            }
        }
        with patch("hashnode_mcp.mcp_server.fetch_from_api", new_callable=AsyncMock) as mock:
            mock.return_value = mock_data
            result = await get_article_details("post1")
            assert "Test Article" in result

    @pytest.mark.asyncio
    async def test_not_found(self):
        with patch("hashnode_mcp.mcp_server.fetch_from_api", new_callable=AsyncMock) as mock:
            mock.return_value = {"data": {"post": None}}
            result = await get_article_details("nonexistent")
            assert "No article found" in result


class TestGetTopArticles:
    @pytest.mark.asyncio
    async def test_success(self):
        mock_data = {
            "data": {
                "feed": {
                    "edges": [
                        {
                            "node": {
                                "id": "feed1",
                                "title": "Trending",
                                "url": "https://example.com/trending",
                                "author": {"name": "Author", "username": "author"},
                                "publishedAt": "2025-06-01T00:00:00Z",
                                "brief": "Trending article",
                            }
                        }
                    ]
                }
            }
        }
        with patch("hashnode_mcp.mcp_server.fetch_from_api", new_callable=AsyncMock) as mock:
            mock.return_value = mock_data
            result = await get_top_articles(5)
            assert "Top Articles" in result or "Trending" in result

    @pytest.mark.asyncio
    async def test_no_results(self):
        mock_data = {"data": {"feed": {"edges": []}}}
        with patch("hashnode_mcp.mcp_server.fetch_from_api", new_callable=AsyncMock) as mock:
            mock.return_value = mock_data
            result = await get_top_articles()
            assert "No top articles" in result


class TestGetArticlesByTag:
    @pytest.mark.asyncio
    async def test_success(self):
        mock_data = {
            "data": {
                "tag": {
                    "name": "Python",
                    "slug": "python",
                    "posts": {
                        "edges": [
                            {
                                "node": {
                                    "id": "t1",
                                    "title": "Python Guide",
                                }
                            }
                        ]
                    },
                }
            }
        }
        with patch("hashnode_mcp.mcp_server.fetch_from_api", new_callable=AsyncMock) as mock:
            mock.return_value = mock_data
            result = await get_articles_by_tag("python")
            assert "Python" in result

    @pytest.mark.asyncio
    async def test_no_results(self):
        mock_data = {"data": {"tag": {"name": "Rare", "slug": "rare", "posts": {"edges": []}}}}
        with patch("hashnode_mcp.mcp_server.fetch_from_api", new_callable=AsyncMock) as mock:
            mock.return_value = mock_data
            result = await get_articles_by_tag("rare")
            assert "No articles found" in result


class TestToggleFollowUser:
    @pytest.mark.asyncio
    async def test_follow(self):
        mock_data = {"data": {"toggleFollowUser": {"user": {"following": True}}}}
        with patch("hashnode_mcp.mcp_server.fetch_from_api", new_callable=AsyncMock) as mock:
            mock.return_value = mock_data
            result = await toggle_follow_user("testuser")
            assert "followed" in result.lower()

    @pytest.mark.asyncio
    async def test_unfollow(self):
        mock_data = {"data": {"toggleFollowUser": {"user": {"following": False}}}}
        with patch("hashnode_mcp.mcp_server.fetch_from_api", new_callable=AsyncMock) as mock:
            mock.return_value = mock_data
            result = await toggle_follow_user("testuser")
            assert "unfollowed" in result.lower()


class TestCreateWebhook:
    @pytest.mark.asyncio
    async def test_success(self):
        mock_data = {
            "data": {
                "createWebhook": {
                    "webhook": {
                        "id": "wh1",
                        "url": "https://example.com/hook",
                        "events": ["POST_PUBLISHED"],
                        "createdAt": "2025-01-01T00:00:00Z",
                    }
                }
            }
        }
        with patch("hashnode_mcp.mcp_server.fetch_from_api", new_callable=AsyncMock) as mock:
            mock.return_value = mock_data
            result = await create_webhook("pub1", "https://example.com/hook", "POST_PUBLISHED", "secret123")
            assert "Webhook Created Successfully" in result

    @pytest.mark.asyncio
    async def test_multiple_events(self):
        mock_data = {
            "data": {
                "createWebhook": {
                    "webhook": {
                        "id": "wh2",
                        "url": "https://example.com/hook",
                        "events": ["POST_PUBLISHED", "POST_UPDATED"],
                    }
                }
            }
        }
        with patch("hashnode_mcp.mcp_server.fetch_from_api", new_callable=AsyncMock) as mock:
            mock.return_value = mock_data
            result = await create_webhook("pub1", "https://example.com/hook", "POST_PUBLISHED, POST_UPDATED", "secret")
            assert "Webhook Created Successfully" in result


class TestDeleteArticle:
    @pytest.mark.asyncio
    async def test_success(self):
        mock_data = {"data": {"deletePost": {"success": True}}}
        with patch("hashnode_mcp.mcp_server.fetch_from_api", new_callable=AsyncMock) as mock:
            mock.return_value = mock_data
            result = await delete_article("post123")
            assert "deleted successfully" in result

    @pytest.mark.asyncio
    async def test_failure(self):
        mock_data = {"data": {"deletePost": {"success": False}}}
        with patch("hashnode_mcp.mcp_server.fetch_from_api", new_callable=AsyncMock) as mock:
            mock.return_value = mock_data
            result = await delete_article("post123")
            assert "Failed to delete" in result


class TestPublishDraft:
    @pytest.mark.asyncio
    async def test_success(self):
        mock_data = {
            "data": {
                "publishDraft": {
                    "post": {
                        "id": "draft1",
                        "title": "Published Draft",
                        "url": "https://blog.example.com/draft",
                    }
                }
            }
        }
        with patch("hashnode_mcp.mcp_server.fetch_from_api", new_callable=AsyncMock) as mock:
            mock.return_value = mock_data
            result = await publish_draft("draft1")
            assert "Draft Published Successfully" in result
            assert "Published Draft" in result


class TestGetPublicationPosts:
    @pytest.mark.asyncio
    async def test_success(self):
        mock_data = {
            "data": {
                "publication": {
                    "title": "Test Blog",
                    "isTeam": False,
                    "posts": {
                        "edges": [
                            {
                                "node": {
                                    "title": "Blog Post",
                                    "url": "https://blog.example.com/post",
                                }
                            }
                        ]
                    },
                }
            }
        }
        with patch("hashnode_mcp.mcp_server.fetch_from_api", new_callable=AsyncMock) as mock:
            mock.return_value = mock_data
            result = await get_publication_posts("blog.example.com", 10)
            assert "Test Blog" in result
            assert "Blog Post" in result

    @pytest.mark.asyncio
    async def test_api_error(self):
        mock_data = {"errors": [{"message": "Not found"}]}
        with patch("hashnode_mcp.mcp_server.fetch_from_api", new_callable=AsyncMock) as mock:
            mock.return_value = mock_data
            result = await get_publication_posts("nonexistent.example.com")
            assert "API returned errors" in result
