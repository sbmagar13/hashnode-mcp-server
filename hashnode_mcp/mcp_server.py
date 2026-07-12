"""
Hashnode MCP Server - A Model Context Protocol server for interacting with the Hashnode API.

This is the canonical server implementation. The root mcp_server.py is a thin
shim that re-exports everything from here for backwards compatibility.
"""
import logging
import os
from datetime import datetime, timezone
from typing import Optional

import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from hashnode_mcp.utils import (
    format_article_creation,
    format_article_update,
    format_search_results,
    format_post_details,
    format_user_info,
    format_top_articles,
    format_articles_by_tag,
    format_toggle_follow_result,
    format_publish_draft_result,
    format_create_webhook_result,
    format_posts,
    TEST_QUERY,
    CREATE_ARTICLE_MUTATION,
    UPDATE_ARTICLE_MUTATION,
    SEARCH_POSTS_OF_PUBLICATION_QUERY,
    GET_PUBLICATION_ID_QUERY,
    GET_POST_BY_ID_QUERY,
    GET_PUBLICATION_POSTS_QUERY,
    GET_ARTICLES_BY_USERNAME_QUERY,
    GET_USER_INFO_QUERY,
    GET_TOP_ARTICLES_QUERY,
    GET_ARTICLES_BY_TAG_QUERY,
    TOGGLE_FOLLOW_MUTATION,
    PUBLISH_DRAFT_MUTATION,
    CREATE_WEBHOOK_MUTATION,
)

load_dotenv()

# Configure logging to stderr so it doesn't corrupt MCP stdio transport
logger = logging.getLogger("hashnode_mcp")
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
logger.addHandler(handler)
logger.setLevel(logging.INFO)

HASHNODE_API_URL = os.getenv("HASHNODE_API_URL", "https://gql.hashnode.com")
logger.info("Using Hashnode API URL: %s", HASHNODE_API_URL)

mcp = FastMCP(
    "Hashnode API",
    instructions="""
    # Hashnode API Server

    This server provides access to Hashnode content through several tools.

    ## Available Tools
    - `test_api_connection()` - Test the connection to the Hashnode API
    - `create_article(title, body_markdown, tags="", published=False)` - Create and publish a new article on Hashnode
    - `update_article(article_id, title=None, body_markdown=None, tags=None, published=None)` - Update an existing article on Hashnode
    - `delete_article(article_id)` - Delete an article on Hashnode
    - `publish_draft(draft_id)` - Publish an existing draft article
    - `get_latest_articles(hostname, limit=10)` - Get the latest articles from a Hashnode publication by hostname
    - `search_articles(query, page=1)` - Search for articles on Hashnode
    - `get_article_details(article_id)` - Get detailed information about a specific article
    - `get_user_info(username)` - Get information about a Hashnode user
    - `get_articles_by_username(username, limit=10)` - Get articles by a specific user
    - `get_top_articles(limit=10)` - Get top/trending articles from Hashnode global feed
    - `get_articles_by_tag(tag, limit=10)` - Get articles filtered by tag
    - `toggle_follow_user(username)` - Follow or unfollow a Hashnode user
    - `create_webhook(publication_id, url, events, secret)` - Create a webhook for a publication
    - `get_publication_posts(hostname, limit=10)` - Get posts from a publication by hostname

    ## When to use what
    - For testing API connection: Use `test_api_connection()`
    - For creating a new article: Use `create_article(title, body_markdown, tags, published)`
    - For updating an existing article: Use `update_article(article_id, title, body_markdown, tags, published)`
    - For deleting an article: Use `delete_article(article_id)`
    - For publishing a draft: Use `publish_draft(draft_id)`
    - For getting latest articles: Use `get_latest_articles(hostname, limit)`
    - For searching articles: Use `search_articles(query, page)`
    - For getting a specific article: Use `get_article_details(article_id)` for detailed information
    - For getting user profile information: Use `get_user_info(username)`
    - For getting articles by user: Use `get_articles_by_username(username, limit)`
    - For trending articles: Use `get_top_articles(limit)`
    - For articles by tag: Use `get_articles_by_tag(tag, limit)`
    - For follow/unfollow: Use `toggle_follow_user(username)`
    - For webhooks: Use `create_webhook(publication_id, url, events, secret)`
    - For publication posts: Use `get_publication_posts(hostname, limit)`
    """
)


def _safe_get(data: dict, *keys: str, default=None):
    """Safely traverse nested dicts without deeply nested if-chains.

    Example: _safe_get(data, "data", "me", "publications", "edges")
    """
    current = data
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key, default)
        if current is None:
            return default
    return current


def _parse_tags(tags: Optional[str]) -> list:
    """Parse a comma-separated tag string into a list of tag dicts."""
    if not tags:
        return []
    tag_list = []
    for tag in tags.split(","):
        tag = tag.strip()
        if tag:
            tag_list.append({
                "name": tag,
                "slug": tag.lower().replace(" ", "-"),
            })
    return tag_list


async def fetch_from_api(query: str, variables: Optional[dict] = None) -> dict:
    """Send a GraphQL request to the Hashnode API."""
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Hashnode MCP Server/1.0",
    }

    token = os.getenv("HASHNODE_PERSONAL_ACCESS_TOKEN")
    if token:
        headers["Authorization"] = token

    request_data = {"query": query, "variables": variables}
    logger.debug("Sending request to %s", HASHNODE_API_URL)

    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            response = await client.post(
                HASHNODE_API_URL,
                json=request_data,
                headers=headers,
            )
            response.raise_for_status()
            result = response.json()
            logger.debug("Response received successfully")
            return result
        except httpx.TimeoutException:
            logger.error("Request timed out after 120 seconds")
            raise Exception(
                "API request timed out after 120 seconds. "
                "The Hashnode API might be experiencing high load."
            )
        except httpx.HTTPStatusError as e:
            logger.error("HTTP error: %s", e)
            raise Exception(f"API returned HTTP {e.response.status_code}: {e.response.text}")
        except Exception as e:
            logger.error("Error in API request: %s", e)
            raise


async def _get_user_publication_id() -> Optional[str]:
    """Fetch the first publication ID for the authenticated user."""
    query = """
    query {
      me {
        publications(first: 1) {
          edges {
            node {
              id
              title
            }
          }
        }
      }
    }
    """
    user_data = await fetch_from_api(query)
    edges = _safe_get(user_data, "data", "me", "publications", "edges")
    if edges:
        pub = edges[0].get("node", {})
        logger.info("Found publication: %s (ID: %s)", pub.get("title"), pub.get("id"))
        return pub.get("id")
    return None


# ---------------------------------------------------------------------------
# MCP Tools
# ---------------------------------------------------------------------------


@mcp.tool()
async def test_api_connection() -> str:
    """Test the connection to the Hashnode API."""
    try:
        data = await fetch_from_api(TEST_QUERY)
        return "API connection successful!"
    except Exception as e:
        return f"API connection failed: {e}"


@mcp.tool()
async def create_article(
    title: str,
    body_markdown: str,
    tags: str = "",
    published: bool = False,
) -> str:
    """
    Create and publish a new article on Hashnode.

    Args:
        title: The title of the article
        body_markdown: The content of the article in markdown format
        tags: Comma-separated list of tags (e.g., "python,tutorial,webdev")
        published: Whether to publish immediately (True) or save as draft (False)
    """
    try:
        logger.info("Creating article: '%s'", title)

        publication_id = await _get_user_publication_id()
        if not publication_id:
            return "Could not find your publications. Please make sure you have a publication set up on Hashnode."

        input_vars = {
            "title": title,
            "contentMarkdown": body_markdown,
            "publicationId": publication_id,
        }

        if published:
            input_vars["publishedAt"] = datetime.now(timezone.utc).isoformat()

        variables = {"input": input_vars}

        tag_list = _parse_tags(tags)
        if tag_list:
            variables["input"]["tags"] = tag_list

        data = await fetch_from_api(CREATE_ARTICLE_MUTATION, variables)

        if _safe_get(data, "errors"):
            return f"API returned errors: {data['errors']}"

        if not _safe_get(data, "data", "publishPost", "post"):
            return f"Error: No data returned from API. Full response: {data}"

        return format_article_creation(data)
    except Exception as e:
        logger.error("Error creating article '%s': %s", title, e)
        return f"Error creating article '{title}': {e}"


@mcp.tool()
async def update_article(
    article_id: str,
    title: Optional[str] = None,
    body_markdown: Optional[str] = None,
    tags: Optional[str] = None,
    published: Optional[bool] = None,
) -> str:
    """
    Update an existing article on Hashnode.

    Args:
        article_id: The ID of the article to update
        title: New title for the article (optional)
        body_markdown: New content in markdown format (optional)
        tags: New comma-separated list of tags (optional)
        published: Change publish status (optional)
    """
    try:
        logger.info("Updating article '%s'", article_id)

        input_vars: dict = {"id": article_id}

        if title is not None:
            input_vars["title"] = title
        if body_markdown is not None:
            input_vars["contentMarkdown"] = body_markdown
        if published is not None and published:
            input_vars["publishedAt"] = datetime.now(timezone.utc).isoformat()

        tag_list = _parse_tags(tags)
        if tag_list:
            input_vars["tags"] = tag_list

        data = await fetch_from_api(UPDATE_ARTICLE_MUTATION, {"input": input_vars})

        if _safe_get(data, "errors"):
            return f"API returned errors: {data['errors']}"

        if not _safe_get(data, "data", "updatePost", "post"):
            return f"Error: No data returned from API. Full response: {data}"

        return format_article_update(data)
    except Exception as e:
        logger.error("Error updating article '%s': %s", article_id, e)
        return f"Error updating article '{article_id}': {e}"


@mcp.tool()
async def delete_article(article_id: str) -> str:
    """
    Delete an article on Hashnode.

    Args:
        article_id: The ID of the article to delete
    """
    try:
        logger.info("Deleting article '%s'", article_id)

        query = """
        mutation DeletePost($input: DeletePostInput!) {
          deletePost(input: $input) {
            success
          }
        }
        """
        data = await fetch_from_api(query, {"input": {"id": article_id}})

        if _safe_get(data, "errors"):
            return f"API returned errors: {data['errors']}"

        success = _safe_get(data, "data", "deletePost", "success")
        if success:
            return f"Article '{article_id}' deleted successfully."
        return f"Failed to delete article '{article_id}'. Response: {data}"
    except Exception as e:
        logger.error("Error deleting article '%s': %s", article_id, e)
        return f"Error deleting article '{article_id}': {e}"


@mcp.tool()
async def publish_draft(draft_id: str) -> str:
    """
    Publish an existing draft article.

    Args:
        draft_id: The ID of the draft to publish
    """
    try:
        logger.info("Publishing draft '%s'", draft_id)
        data = await fetch_from_api(PUBLISH_DRAFT_MUTATION, {"draftId": draft_id})

        if _safe_get(data, "errors"):
            return f"API returned errors: {data['errors']}"

        if not _safe_get(data, "data", "publishDraft", "post"):
            return f"Error: No data returned from API. Full response: {data}"

        return format_publish_draft_result(data)
    except Exception as e:
        logger.error("Error publishing draft '%s': %s", draft_id, e)
        return f"Error publishing draft '{draft_id}': {e}"


@mcp.tool()
async def search_articles(query: str, page: int = 1) -> str:
    """
    Search for articles on Hashnode.

    Args:
        query: Search term to find articles
        page: Page number for pagination (default: 1)
    """
    try:
        logger.info("Searching articles for '%s' (page %d)", query, page)

        publication_id = await _get_user_publication_id()
        if not publication_id:
            return "Could not find your publications. Please make sure you have a publication set up on Hashnode."

        per_page = 10
        after = None
        if page > 1:
            after = f"offset_{(page - 1) * per_page}"

        search_variables = {
            "first": per_page,
            "after": after,
            "filter": {
                "publicationId": publication_id,
                "query": query,
            },
        }

        data = await fetch_from_api(SEARCH_POSTS_OF_PUBLICATION_QUERY, search_variables)

        if _safe_get(data, "errors"):
            return f"API returned errors: {data['errors']}"

        return format_search_results(data)
    except Exception as e:
        logger.error("Error searching articles for '%s': %s", query, e)
        return f"Error searching for articles with query '{query}': {e}"


@mcp.tool()
async def get_article_details(article_id: str) -> str:
    """
    Get detailed information about a specific article.

    Args:
        article_id: The ID of the article to retrieve
    """
    try:
        logger.info("Getting article details for '%s'", article_id)
        data = await fetch_from_api(GET_POST_BY_ID_QUERY, {"id": article_id})

        if _safe_get(data, "errors"):
            return f"API returned errors: {data['errors']}"

        if not _safe_get(data, "data", "post"):
            return f"No article found with ID '{article_id}'"

        return format_post_details(data)
    except Exception as e:
        logger.error("Error getting article details '%s': %s", article_id, e)
        return f"Error getting article details '{article_id}': {e}"


@mcp.tool()
async def get_user_info(username: str) -> str:
    """
    Get information about a Hashnode user.

    Args:
        username: The username of the user
    """
    try:
        logger.info("Getting user info for '%s'", username)
        data = await fetch_from_api(GET_USER_INFO_QUERY, {"username": username})

        if _safe_get(data, "errors"):
            return f"API returned errors: {data['errors']}"

        if not _safe_get(data, "data", "user"):
            return f"No user found with username '{username}'"

        return format_user_info(data)
    except Exception as e:
        logger.error("Error getting user info for '%s': %s", username, e)
        return f"Error getting user information for '{username}': {e}"


@mcp.tool()
async def get_latest_articles(hostname: str, limit: int = 10) -> str:
    """
    Get the latest articles from a Hashnode publication by hostname.

    Args:
        hostname: The hostname of the publication (e.g., "blog.example.com")
        limit: The number of articles to retrieve (default: 10)
    """
    try:
        logger.info("Getting latest articles for '%s' (limit %d)", hostname, limit)

        pub_data = await fetch_from_api(GET_PUBLICATION_ID_QUERY, {"host": hostname})
        publication_id = _safe_get(pub_data, "data", "publication", "id")
        publication_title = _safe_get(pub_data, "data", "publication", "title")

        if not publication_id:
            return f"Could not find publication with hostname '{hostname}'. Please make sure the hostname is correct."

        search_variables = {
            "first": limit,
            "filter": {
                "publicationId": publication_id,
                "query": "",
            },
        }

        data = await fetch_from_api(SEARCH_POSTS_OF_PUBLICATION_QUERY, search_variables)

        if _safe_get(data, "errors"):
            return f"API returned errors: {data['errors']}"

        edges = _safe_get(data, "data", "searchPostsOfPublication", "edges", default=[])
        if not edges:
            return f"No articles found for publication '{publication_title}'."

        result = f"# Latest Articles from {publication_title}\n\n"
        for edge in edges:
            node = edge.get("node", {})
            title = node.get("title", "Untitled")
            result += f"## {title}\n"
            if "id" in node:
                result += f"ID: {node['id']}\n"
            author = _safe_get(node, "author", "name")
            if author:
                result += f"Author: {author}\n"
            published_at = node.get("publishedAt")
            if published_at:
                try:
                    pub_date = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
                    result += f"Published: {pub_date.strftime('%b %d, %Y')}\n"
                except (ValueError, TypeError):
                    result += f"Published: {published_at}\n"
            brief = node.get("brief")
            if brief:
                result += f"Description: {brief[:200]}{'...' if len(brief) > 200 else ''}\n"
            result += "\n"

        return result
    except Exception as e:
        logger.error("Error getting latest articles for '%s': %s", hostname, e)
        return f"Error getting latest articles for hostname '{hostname}': {e}"


@mcp.tool()
async def get_articles_by_username(username: str, limit: int = 10) -> str:
    """
    Get articles by a specific Hashnode user.

    Args:
        username: The username of the user
        limit: Number of articles to retrieve (default: 10)
    """
    try:
        logger.info("Getting articles for user '%s' (limit %d)", username, limit)
        data = await fetch_from_api(GET_ARTICLES_BY_USERNAME_QUERY, {"username": username, "first": limit})

        if _safe_get(data, "errors"):
            return f"API returned errors: {data['errors']}"

        edges = _safe_get(data, "data", "user", "posts", "edges", default=[])
        if not edges:
            return f"No articles found for user '{username}'."

        user_name = _safe_get(data, "data", "user", "name", default=username)
        result = f"# Articles by {user_name}\n\n"
        for edge in edges:
            node = edge.get("node", {})
            title = node.get("title", "Untitled")
            result += f"## {title}\n"
            if "id" in node:
                result += f"ID: {node['id']}\n"
            if "url" in node:
                result += f"URL: {node['url']}\n"
            published_at = node.get("publishedAt")
            if published_at:
                try:
                    pub_date = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
                    result += f"Published: {pub_date.strftime('%b %d, %Y')}\n"
                except (ValueError, TypeError):
                    result += f"Published: {published_at}\n"
            brief = node.get("brief")
            if brief:
                result += f"Description: {brief[:200]}{'...' if len(brief) > 200 else ''}\n"
            result += "\n"

        return result
    except Exception as e:
        logger.error("Error getting articles for user '%s': %s", username, e)
        return f"Error getting articles for user '{username}': {e}"


@mcp.tool()
async def get_top_articles(limit: int = 10) -> str:
    """
    Get top/trending articles from the Hashnode global feed.

    Args:
        limit: Number of articles to retrieve (default: 10)
    """
    try:
        logger.info("Getting top articles (limit %d)", limit)
        data = await fetch_from_api(GET_TOP_ARTICLES_QUERY, {"first": limit})

        if _safe_get(data, "errors"):
            return f"API returned errors: {data['errors']}"

        return format_top_articles(data)
    except Exception as e:
        logger.error("Error getting top articles: %s", e)
        return f"Error getting top articles: {e}"


@mcp.tool()
async def get_articles_by_tag(tag: str, limit: int = 10) -> str:
    """
    Get articles filtered by a specific tag.

    Args:
        tag: The tag slug to filter by (e.g., "python", "webdev")
        limit: Number of articles to retrieve (default: 10)
    """
    try:
        logger.info("Getting articles by tag '%s' (limit %d)", tag, limit)
        data = await fetch_from_api(GET_ARTICLES_BY_TAG_QUERY, {"tag": tag, "first": limit})

        if _safe_get(data, "errors"):
            return f"API returned errors: {data['errors']}"

        return format_articles_by_tag(data)
    except Exception as e:
        logger.error("Error getting articles by tag '%s': %s", tag, e)
        return f"Error getting articles by tag '{tag}': {e}"


@mcp.tool()
async def toggle_follow_user(username: str) -> str:
    """
    Follow or unfollow a Hashnode user (toggles current state).

    Args:
        username: The username of the user to follow/unfollow
    """
    try:
        logger.info("Toggling follow for user '%s'", username)
        data = await fetch_from_api(TOGGLE_FOLLOW_MUTATION, {"username": username})

        if _safe_get(data, "errors"):
            return f"API returned errors: {data['errors']}"

        return format_toggle_follow_result(data)
    except Exception as e:
        logger.error("Error toggling follow for '%s': %s", username, e)
        return f"Error toggling follow status for '{username}': {e}"


@mcp.tool()
async def create_webhook(
    publication_id: str,
    url: str,
    events: str,
    secret: str,
) -> str:
    """
    Create a webhook for a Hashnode publication.

    Args:
        publication_id: The ID of the publication
        url: The webhook URL to receive events
        events: Comma-separated list of events (e.g., "POST_PUBLISHED,POST_UPDATED,POST_DELETED")
        secret: A secret for webhook verification
    """
    try:
        logger.info("Creating webhook for publication '%s'", publication_id)
        event_list = [e.strip() for e in events.split(",") if e.strip()]

        data = await fetch_from_api(
            CREATE_WEBHOOK_MUTATION,
            {
                "publicationId": publication_id,
                "url": url,
                "events": event_list,
                "secret": secret,
            },
        )

        if _safe_get(data, "errors"):
            return f"API returned errors: {data['errors']}"

        return format_create_webhook_result(data)
    except Exception as e:
        logger.error("Error creating webhook: %s", e)
        return f"Error creating webhook: {e}"


@mcp.tool()
async def get_publication_posts(hostname: str, limit: int = 10) -> str:
    """
    Get posts from a Hashnode publication by hostname.

    Args:
        hostname: The hostname of the publication (e.g., "blog.example.com")
        limit: Number of posts to retrieve (default: 10)
    """
    try:
        logger.info("Getting publication posts for '%s' (limit %d)", hostname, limit)
        data = await fetch_from_api(GET_PUBLICATION_POSTS_QUERY, {"host": hostname, "first": limit})

        if _safe_get(data, "errors"):
            return f"API returned errors: {data['errors']}"

        return format_posts(data)
    except Exception as e:
        logger.error("Error getting publication posts for '%s': %s", hostname, e)
        return f"Error getting publication posts for hostname '{hostname}': {e}"


def main():
    """Entry point for the package."""
    logger.info("Starting Hashnode MCP server...")
    mcp.run()


if __name__ == "__main__":
    main()
