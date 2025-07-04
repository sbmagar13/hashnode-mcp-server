import os
import json
import httpx
from dotenv import load_dotenv
from typing import List, Optional, Dict, Any
from mcp.server.fastmcp import FastMCP, Context
from hashnode_mcp.utils import (
    format_article_creation,
    format_article_update,
    format_search_results,
    format_post_details,
    format_user_info,
    format_top_articles,
    format_articles_by_tag,
    TEST_QUERY,
    CREATE_ARTICLE_MUTATION,
    UPDATE_ARTICLE_MUTATION,
    SEARCH_POSTS_OF_PUBLICATION_QUERY,
    GET_PUBLICATION_ID_QUERY,
    GET_POST_BY_ID_QUERY,
    GET_ARTICLES_BY_USERNAME_QUERY,
    GET_USER_INFO_QUERY,
    GET_TOP_ARTICLES_QUERY,
    GET_ARTICLES_BY_TAG_QUERY
)

load_dotenv()

HASHNODE_API_URL = os.getenv("HASHNODE_API_URL", "https://gql.hashnode.com")
print(f"Using Hashnode API URL: {HASHNODE_API_URL}")

mcp = FastMCP(
    "Hashnode API",
    instructions="""
    # Hashnode API Server
    
    This server provides access to Hashnode content through several tools.
    
    ## Available Tools
    - `test_api_connection()` - Test the connection to the Hashnode API
    - `create_article(title, body_markdown, tags="", published=False)` - Create and publish a new article on Hashnode
    - `update_article(article_id, title=None, body_markdown=None, tags=None, published=None)` - Update an existing article on Hashnode
    - `get_latest_articles(hostname, limit=10)` - Get the latest articles from a Hashnode publication by hostname
    - `search_articles(query, page=1)` - Search for articles on Hashnode
    - `get_article_details(article_id)` - Get detailed information about a specific article
    - `get_user_info(username)` - Get information about a Hashnode user
    
    ## When to use what
    - For testing API connection: Use `test_api_connection()`
    - For creating a new article: Use `create_article(title, body_markdown, tags, published)`
    - For updating an existing article: Use `update_article(article_id, title, body_markdown, tags, published)`
    - For getting latest articles: Use `get_latest_articles(hostname, limit)`
    - For searching articles: Use `search_articles(query, page)`
    - For getting a specific article: Use `get_article_details(article_id)` for detailed information
    - For getting user profile information: Use `get_user_info(username)`
    
    ## Example Queries
    - "Test the API connection" → Use `test_api_connection()`
    - "Create a new article" → Use `create_article("My Title", "Content in markdown", "tag1,tag2", True)`
    - "Update an article" → Use `update_article("article_id_here", "New Title", "Updated content", "tag1,tag2", True)`
    - "Get latest articles" → Use `get_latest_articles("blog.example.com", 5)`
    - "Search for articles about Python" → Use `search_articles("Python", 1)`
    - "Get article details" → Use `get_article_details(123456)`
    - "Get user profile information" → Use `get_user_info("johndoe")`
    """
)

@mcp.tool()
async def update_article(article_id: str, title: str = None, body_markdown: str = None, tags: str = None, published: bool = None) -> str:
    """
    Update an existing article on Hashnode
    
    Args:
        article_id: The ID of the article to update
        title: New title for the article (optional)
        body_markdown: New content in markdown format (optional)
        tags: New comma-separated list of tags (optional)
        published: Change publish status (optional)
    """
    try:
        # Prepare the input variables
        input_vars = {
            "id": article_id
        }
        
        # Add optional fields if provided
        if title is not None:
            input_vars["title"] = title
            
        if body_markdown is not None:
            input_vars["contentMarkdown"] = body_markdown
        
        # Set publishedAt if the article should be published immediately
        if published is not None and published:
            from datetime import datetime
            # Format the current date and time in ISO format for GraphQL DateTime
            input_vars["publishedAt"] = datetime.utcnow().isoformat() + "Z"
        
        # Add tags if provided
        if tags is not None:
            tag_list = []
            for tag in tags.split(','):
                tag = tag.strip()
                if tag:
                    # For each tag, create a PublishPostTagInput object
                    # We'll use name and slug since we don't have access to tag IDs
                    tag_list.append({
                        "name": tag,
                        "slug": tag.lower().replace(' ', '-')
                    })
            
            if tag_list:
                input_vars["tags"] = tag_list
        
        variables = {
            "input": input_vars
        }
        
        print(f"Updating article with ID '{article_id}'")
        print(f"Query: {UPDATE_ARTICLE_MUTATION}")
        print(f"Variables: {json.dumps(variables)}")
        
        data = await fetch_from_api(UPDATE_ARTICLE_MUTATION, variables)
        print(f"Response from API: {json.dumps(data)}")
        
        if not data or "data" not in data:
            return f"Error: No data returned from API. Full response: {json.dumps(data)}"
        
        if "errors" in data:
            return f"API returned errors: {json.dumps(data['errors'])}"
        
        return format_article_update(data)
    except Exception as e:
        print(f"Error updating article: {str(e)}")
        error_message = f"Error updating article with ID '{article_id}': {str(e)}"
        
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_content = e.response.text
                error_message += f"\nResponse content: {error_content}"
            except:
                pass
        
        return error_message

async def fetch_from_api(query: str, variables: dict = None) -> dict:
    """Helper function to fetch data from Hashnode API using GraphQL"""
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Hashnode MCP Server/1.0"
    }
    
    token = os.getenv("HASHNODE_PERSONAL_ACCESS_TOKEN")
    if token:
        headers["Authorization"] = token
    
    request_data = {"query": query, "variables": variables}
    print(f"Sending request to {HASHNODE_API_URL} with data: {json.dumps(request_data)}")
    
    async with httpx.AsyncClient(timeout=120.0) as client:  # Increased timeout to 120 seconds
        try:
            response = await client.post(
                HASHNODE_API_URL,
                json=request_data,
                headers=headers
            )
            response.raise_for_status()
            result = response.json()
            print(f"Response: {json.dumps(result)}")
            return result
        except httpx.TimeoutException:
            print("Request timed out. Consider optimizing the query or increasing the timeout.")
            raise Exception("API request timed out after 120 seconds. The Hashnode API might be experiencing high load.")
        except Exception as e:
            print(f"Error in API request: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    print(f"Response content: {e.response.text}")
                except:
                    print("Could not get response content")
            raise

@mcp.tool()
async def test_api_connection() -> str:
    """
    Test the connection to the Hashnode API
    """
    try:
        data = await fetch_from_api(TEST_QUERY)
        return f"API connection successful! Response: {json.dumps(data)}"
    except Exception as e:
        return f"API connection failed: {str(e)}"


@mcp.tool()
async def create_article(title: str, body_markdown: str, tags: str = "", published: bool = False) -> str:
    """
    Create and publish a new article on Hashnode
    
    Args:
        title: The title of the article
        body_markdown: The content of the article in markdown format
        tags: Comma-separated list of tags (e.g., "python,tutorial,webdev")
        published: Whether to publish immediately (True) or save as draft (False)
    """
    try:
        print(f"Starting article creation process for '{title}'")
        
        # Optimized query that combines getting publication info and creating article
        # First, we need to get the user's publications
        user_query = """
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
        
        print("Getting user's publications (limited to first publication)")
        user_data = await fetch_from_api(user_query)
        
        if not user_data or "data" not in user_data or not user_data["data"] or "me" not in user_data["data"] or not user_data["data"]["me"] or "publications" not in user_data["data"]["me"] or not user_data["data"]["me"]["publications"] or "edges" not in user_data["data"]["me"]["publications"] or not user_data["data"]["me"]["publications"]["edges"]:
            return "Could not find user's publications. Please make sure you have a publication set up on Hashnode."
        
        # Use the first publication in the list
        if len(user_data["data"]["me"]["publications"]["edges"]) == 0:
            return "No publications found for the user. Please create a publication on Hashnode first."
        
        publication = user_data["data"]["me"]["publications"]["edges"][0]["node"]
        publication_id = publication["id"]
        publication_title = publication["title"]
        print(f"Found publication: {publication_title} (ID: {publication_id})")
        
        # Prepare the input variables
        input_vars = {
            "title": title,
            "contentMarkdown": body_markdown,
            "publicationId": publication_id
        }
        
        # Set publishedAt if the article should be published immediately
        if published:
            from datetime import datetime
            # Format the current date and time in ISO format for GraphQL DateTime
            input_vars["publishedAt"] = datetime.utcnow().isoformat() + "Z"
        
        variables = {
            "input": input_vars
        }
        
        # Add tags if provided
        if tags:
            tag_list = []
            for tag in tags.split(','):
                tag = tag.strip()
                if tag:
                    # For each tag, create a PublishPostTagInput object
                    tag_list.append({
                        "name": tag,
                        "slug": tag.lower().replace(' ', '-')
                    })
            
            if tag_list:
                variables["input"]["tags"] = tag_list
        
        print(f"Creating article with title '{title}'")
        print(f"Variables: {json.dumps(variables)}")
        
        try:
            data = await fetch_from_api(CREATE_ARTICLE_MUTATION, variables)
            
            if not data or "data" not in data:
                return f"Error: No data returned from API. Full response: {json.dumps(data)}"
            
            if "errors" in data:
                return f"API returned errors: {json.dumps(data['errors'])}"
            
            return format_article_creation(data)
        except Exception as e:
            if "timeout" in str(e).lower():
                return f"The article creation request timed out, but the article might still have been created. Please check your Hashnode dashboard. Error details: {str(e)}"
            raise
    except Exception as e:
        print(f"Error creating article: {str(e)}")
        error_message = f"Error creating article '{title}': {str(e)}"
        
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_content = e.response.text
                error_message += f"\nResponse content: {error_content}"
            except:
                pass
        
        return error_message


@mcp.tool()
async def search_articles(query: str, page: int = 1) -> str:
    """
    Search for articles on Hashnode
    
    Args:
        query: Search term to find articles
        page: Page number for pagination (default: 1)
    """
    try:
        print(f"Starting article search for query '{query}', page {page}")
        
        # Optimized query that gets only the first publication
        user_query = """
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
        
        print("Getting user's publications for search (limited to first publication)")
        user_data = await fetch_from_api(user_query)
        
        if not user_data or "data" not in user_data or not user_data["data"] or "me" not in user_data["data"] or not user_data["data"]["me"] or "publications" not in user_data["data"]["me"] or not user_data["data"]["me"]["publications"] or "edges" not in user_data["data"]["me"]["publications"] or not user_data["data"]["me"]["publications"]["edges"]:
            return "Could not find user's publications. Please make sure you have a publication set up on Hashnode."
        
        # Use the first publication in the list
        if len(user_data["data"]["me"]["publications"]["edges"]) == 0:
            return "No publications found for the user. Please create a publication on Hashnode first."
        
        publication = user_data["data"]["me"]["publications"]["edges"][0]["node"]
        publication_id = publication["id"]
        publication_title = publication["title"]
        print(f"Found publication: {publication_title} (ID: {publication_id})")
        
        # Calculate pagination parameters - limit to 5 results per page to reduce response size
        per_page = 5  # Reduced number of results per page
        first = per_page
        after = None
        if page > 1:
            after = f"offset_{(page-1)*per_page}"
        
        # Search for posts in this publication
        search_variables = {
            "first": first,
            "after": after,
            "filter": {
                "publicationId": publication_id,
                "query": query  # The search query
            }
        }
        
        print(f"Searching for articles with query '{query}' in publication '{publication_title}'")
        
        try:
            search_data = await fetch_from_api(SEARCH_POSTS_OF_PUBLICATION_QUERY, search_variables)
            
            if not search_data or "data" not in search_data:
                return f"Error: No data returned from API. Full response: {json.dumps(search_data)}"
            
            if "errors" in search_data:
                return f"API returned errors: {json.dumps(search_data['errors'])}"
            
            # Format the search results
            return format_search_results(search_data)
        except Exception as e:
            if "timeout" in str(e).lower():
                return f"The search request timed out. Try a more specific search query or try again later. Error details: {str(e)}"
            raise
    except Exception as e:
        print(f"Error searching articles: {str(e)}")
        error_message = f"Error searching for articles with query '{query}': {str(e)}"
        
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_content = e.response.text
                error_message += f"\nResponse content: {error_content}"
            except:
                pass
        
        return error_message

@mcp.tool()
async def get_article_details(article_id: str) -> str:
    """
    Get detailed information about a specific article
    
    Args:
        article_id: The ID of the article to retrieve
    """
    try:
        variables = {
            "id": article_id  # Hashnode API expects string IDs
        }
        
        print(f"Getting detailed article information with ID '{article_id}'")
        article_data = await fetch_from_api(GET_POST_BY_ID_QUERY, variables)
        print(f"Article data response: {json.dumps(article_data)}")
        
        if not article_data or "data" not in article_data:
            return f"Error: No data returned from API. Full response: {json.dumps(article_data)}"
        
        if "errors" in article_data:
            return f"API returned errors: {json.dumps(article_data['errors'])}"
        
        if "post" not in article_data["data"] or not article_data["data"]["post"]:
            return f"No article found with ID '{article_id}'"
        
        # Format the post details
        return format_post_details(article_data)
    except Exception as e:
        print(f"Error getting article details: {str(e)}")
        error_message = f"Error getting article details with ID '{article_id}': {str(e)}"
        
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_content = e.response.text
                error_message += f"\nResponse content: {error_content}"
            except:
                pass
        
        return error_message


@mcp.tool()
async def get_user_info(username: str) -> str:
    """
    Get information about a Hashnode user
    
    Args:
        username: The username of the user
    """
    try:
        variables = {
            "username": username
        }
        
        print(f"Getting user information for username '{username}'")
        user_info_data = await fetch_from_api(GET_USER_INFO_QUERY, variables)
        print(f"User info data response: {json.dumps(user_info_data)}")
        
        if not user_info_data or "data" not in user_info_data:
            return f"Error: No data returned from API. Full response: {json.dumps(user_info_data)}"
        
        if "errors" in user_info_data:
            return f"API returned errors: {json.dumps(user_info_data['errors'])}"
        
        if "user" not in user_info_data["data"] or not user_info_data["data"]["user"]:
            return f"No user found with username '{username}'"
        
        # Format the user information
        return format_user_info(user_info_data)
    except Exception as e:
        print(f"Error getting user info: {str(e)}")
        error_message = f"Error getting user information for username '{username}': {str(e)}"
        
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_content = e.response.text
                error_message += f"\nResponse content: {error_content}"
            except:
                pass
        
        return error_message



@mcp.tool()
async def get_latest_articles(hostname: str, limit: int = 10) -> str:
    """
    Get the latest articles from a Hashnode publication by hostname
    
    Args:
        hostname: The hostname of the publication (e.g., "blog.example.com")
        limit: The number of articles to retrieve (default: 10)
        
    Note:
        If limit is higher than the actual number of available articles,
        all available articles will be returned.
    """
    try:
        # First, get the publication ID from the hostname
        variables = {
            "host": hostname
        }
        
        print(f"Getting publication ID for hostname '{hostname}'")
        publication_data = await fetch_from_api(GET_PUBLICATION_ID_QUERY, variables)
        print(f"Publication data response: {json.dumps(publication_data)}")
        
        if not publication_data or "data" not in publication_data or not publication_data["data"] or "publication" not in publication_data["data"] or not publication_data["data"]["publication"] or "id" not in publication_data["data"]["publication"]:
            return f"Could not find publication with hostname '{hostname}'. Please make sure the hostname is correct."
        
        publication_id = publication_data["data"]["publication"]["id"]
        publication_title = publication_data["data"]["publication"]["title"]
        print(f"Found publication: {publication_title} (ID: {publication_id})")
        
        # Simplified approach: just make a single request to get all articles at once
        all_edges = []
        
        # Search for posts in this publication
        search_variables = {
            "first": limit,  # Request all articles at once
            "filter": {
                "publicationId": publication_id,
                "query": ""  # Empty query to get all articles
            }
        }
        
        print(f"Searching for {limit} articles in publication '{publication_title}'")
        search_data = await fetch_from_api(SEARCH_POSTS_OF_PUBLICATION_QUERY, search_variables)
        
        if not search_data or "data" not in search_data:
            return f"Error: No data returned from API. Full response: {json.dumps(search_data)}"
        
        if "errors" in search_data:
            return f"API returned errors: {json.dumps(search_data['errors'])}"
        
        if "searchPostsOfPublication" in search_data["data"] and "edges" in search_data["data"]["searchPostsOfPublication"]:
            edges = search_data["data"]["searchPostsOfPublication"]["edges"]
            all_edges.extend(edges)
            print(f"Found {len(edges)} articles")
        else:
            print("No articles found in response")
        
        # Format the search results
        result = f"# Latest Articles from {publication_title}\n\n"
        
        if not all_edges:
            return f"No articles found for publication '{publication_title}'."
        
        for edge in all_edges:
            if "node" in edge:
                node = edge["node"]
                title = node.get("title", "Untitled")
                result += f"## {title}\n"
                
                if "id" in node:
                    result += f"ID: {node['id']}\n"
                
                if "author" in node and node["author"] and "name" in node["author"]:
                    result += f"Author: {node['author']['name']}\n"
                
                if "publishedAt" in node and node["publishedAt"]:
                    from datetime import datetime
                    try:
                        published_date = datetime.fromisoformat(node["publishedAt"].replace("Z", "+00:00"))
                        result += f"Published: {published_date.strftime('%b %d')}\n"
                    except:
                        result += f"Published: {node['publishedAt']}\n"
                
                if "brief" in node and node["brief"]:
                    brief = node["brief"]
                    max_length = 200
                    if len(brief) > max_length:
                        brief = brief[:max_length] + "..."
                    result += f"Description: {brief}\n"
                
                result += "\n"
        
        return result
    except Exception as e:
        print(f"Error getting latest articles: {str(e)}")
        error_message = f"Error getting latest articles for hostname '{hostname}': {str(e)}"
        
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_content = e.response.text
                error_message += f"\nResponse content: {error_content}"
            except:
                pass
        
        return error_message


if __name__ == "__main__":
    print("Starting Hashnode MCP server...")
    mcp.run()
