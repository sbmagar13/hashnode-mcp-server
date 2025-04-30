"""
Tests for the Hashnode MCP server.
"""

import os
import json
import pytest
import asyncio
from unittest.mock import patch, MagicMock
from hashnode_mcp.mcp_server import (
    test_api_connection,
    get_publication_posts,
    get_publication_id,
    search_posts_by_hostname,
    search_posts_of_publication,
    fetch_from_api
)

# Sample test data
SAMPLE_PUBLICATION_DATA = {
    "data": {
        "publication": {
            "id": "test-publication-id",
            "title": "Test Publication",
            "isTeam": False,
            "posts": {
                "edges": [
                    {
                        "node": {
                            "title": "Test Post 1",
                            "brief": "This is a test post",
                            "url": "https://blog.example.com/test-post-1"
                        }
                    },
                    {
                        "node": {
                            "title": "Test Post 2",
                            "brief": "This is another test post",
                            "url": "https://blog.example.com/test-post-2"
                        }
                    }
                ]
            }
        }
    }
}

SAMPLE_SEARCH_DATA = {
    "data": {
        "searchPostsOfPublication": {
            "edges": [
                {
                    "node": {
                        "title": "Test Search Result 1",
                        "brief": "This is a test search result",
                        "url": "https://blog.example.com/test-search-1",
                        "slug": "test-search-1",
                        "publishedAt": "2023-01-01",
                        "author": {
                            "name": "Test Author",
                            "username": "testauthor",
                            "profilePicture": "https://example.com/profile.jpg"
                        },
                        "coverImage": {
                            "url": "https://example.com/cover.jpg"
                        }
                    },
                    "cursor": "cursor1"
                }
            ],
            "pageInfo": {
                "hasNextPage": True,
                "endCursor": "cursor1"
            }
        }
    }
}

@pytest.fixture
def mock_env_vars():
    """Set up environment variables for testing."""
    with patch.dict(os.environ, {
        "HASHNODE_API_URL": "https://test-api.hashnode.com",
        "HASHNODE_PERSONAL_ACCESS_TOKEN": "test-token"
    }):
        yield

@pytest.fixture
async def mock_fetch_from_api():
    """Mock the fetch_from_api function."""
    async def mock_fetch(*args, **kwargs):
        query = args[0]
        if "GetPublicationByHost" in query:
            return SAMPLE_PUBLICATION_DATA
        elif "SearchPostsOfPublication" in query:
            return SAMPLE_SEARCH_DATA
        else:
            return {"data": {"__schema": {"queryType": {"name": "Query"}}}}
    
    with patch("hashnode_mcp.mcp_server.fetch_from_api", side_effect=mock_fetch):
        yield

@pytest.mark.asyncio
async def test_test_api_connection(mock_env_vars, mock_fetch_from_api):
    """Test the test_api_connection function."""
    result = await test_api_connection()
    assert "API connection successful" in result

@pytest.mark.asyncio
async def test_get_publication_posts(mock_env_vars, mock_fetch_from_api):
    """Test the get_publication_posts function."""
    result = await get_publication_posts("blog.example.com", 2)
    assert "Test Publication" in result
    assert "Test Post 1" in result
    assert "Test Post 2" in result

@pytest.mark.asyncio
async def test_get_publication_id(mock_env_vars, mock_fetch_from_api):
    """Test the get_publication_id function."""
    result = await get_publication_id("blog.example.com")
    assert "Test Publication" in result
    assert "test-publication-id" in result

@pytest.mark.asyncio
async def test_search_posts_by_hostname(mock_env_vars, mock_fetch_from_api):
    """Test the search_posts_by_hostname function."""
    result = await search_posts_by_hostname("blog.example.com", "test", 1)
    assert "Test Search Result 1" in result

@pytest.mark.asyncio
async def test_search_posts_of_publication(mock_env_vars, mock_fetch_from_api):
    """Test the search_posts_of_publication function."""
    result = await search_posts_of_publication("test-publication-id", "test", 1)
    assert "Test Search Result 1" in result
    assert "Test Author" in result
