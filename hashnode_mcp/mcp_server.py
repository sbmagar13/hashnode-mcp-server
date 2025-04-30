import os
import json
import httpx
from dotenv import load_dotenv
from typing import List, Optional, Dict, Any
from mcp.server.fastmcp import FastMCP, Context
from hashnode_mcp.utils import (
    format_posts,
    format_search_results,
    TEST_QUERY,
    GET_PUBLICATION_ID_QUERY,
    GET_PUBLICATION_POSTS_QUERY,
    SEARCH_POSTS_OF_PUBLICATION_QUERY
)

load_dotenv()

HASHNODE_API_URL = os.getenv("HASHNODE_API_URL", "https://gql.hashnode.com")
print(f"Using Hashnode API URL: {HASHNODE_API_URL}")

mcp = FastMCP(
    "Hashnode API",
    instructions="""
    # Hashnode API Server
    
    This server provides access to Hashnode content through various tools.
    
    ## Available Tools
    - `test_api_connection()` - Test the connection to the Hashnode API
    - `get_publication_posts(host, first=5)` - Get posts from a specific publication
    - `get_publication_id(host)` - Get the publication ID from a hostname
    - `search_posts_of_publication(publication_id, query, first=10)` - Search for posts within a specific publication
    - `search_posts_by_hostname(host, query, first=10)` - Search for posts within a publication using its hostname
    
    ## When to use what
    - For publication-specific content: Use `get_publication_posts(host)`
    - For getting a publication ID: Use `get_publication_id(host)`
    - For searching within a publication (with ID): Use `search_posts_of_publication(publication_id, query)`
    - For searching within a publication (with hostname): Use `search_posts_by_hostname(host, query)`
    
    ## Example Queries
    - "Get posts from publication blog.example.com" → Use `get_publication_posts("blog.example.com")`
    - "Get the ID for publication blog.example.com" → Use `get_publication_id("blog.example.com")`
    - "Search for 'docker' in publication with ID 123" → Use `search_posts_of_publication("123", "docker")`
    - "Search for 'docker' in publication blog.example.com" → Use `search_posts_by_hostname("blog.example.com", "docker")`
    """
)

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
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                HASHNODE_API_URL,
                json=request_data,
                headers=headers,
                timeout=10.0
            )
            response.raise_for_status()
            result = response.json()
            print(f"Response: {json.dumps(result)}")
            return result
        except Exception as e:
            print(f"Error in API request: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response content: {e.response.text}")
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
async def get_publication_posts(host: str, first: int = 5) -> str:
    """
    Fetch posts from a specific publication on Hashnode
    
    Args:
        host: The hostname of the publication (e.g., "blog.budhathokisagar.com.np")
        first: Number of posts to fetch (default: 5)
    """
    variables = {
        "host": host,
        "first": first
    }
    
    try:
        print(f"Fetching posts from publication '{host}'")
        print(f"Query: {GET_PUBLICATION_POSTS_QUERY}")
        print(f"Variables: {json.dumps(variables)}")
        
        data = await fetch_from_api(GET_PUBLICATION_POSTS_QUERY, variables)
        return format_posts(data)
    except Exception as e:
        print(f"Error getting publication posts: {str(e)}")
        error_message = f"Error fetching posts from publication '{host}': {str(e)}"
        
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_content = e.response.text
                error_message += f"\nResponse content: {error_content}"
            except:
                pass
        
        return error_message

@mcp.tool()
async def get_publication_id(host: str) -> str:
    """
    Get the publication ID from a hostname
    
    Args:
        host: The hostname of the publication (e.g., "blog.budhathokisagar.com.np")
    """
    variables = {
        "host": host
    }
    
    try:
        print(f"Getting publication ID for '{host}'")
        print(f"Query: {GET_PUBLICATION_ID_QUERY}")
        print(f"Variables: {json.dumps(variables)}")
        
        data = await fetch_from_api(GET_PUBLICATION_ID_QUERY, variables)
        
        if not data or "data" not in data or not data["data"] or "publication" not in data["data"] or not data["data"]["publication"]:
            return f"No publication found for hostname '{host}'."
        
        publication = data["data"]["publication"]
        publication_id = publication.get("id")
        title = publication.get("title", "Untitled")
        
        if not publication_id:
            return f"Could not find ID for publication '{title}' with hostname '{host}'."
        
        return f"Publication: {title}\nID: {publication_id}"
    except Exception as e:
        print(f"Error getting publication ID: {str(e)}")
        error_message = f"Error getting publication ID for '{host}': {str(e)}"
        
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_content = e.response.text
                error_message += f"\nResponse content: {error_content}"
            except:
                pass
        
        return error_message

@mcp.tool()
async def search_posts_by_hostname(host: str, query: str, first: int = 10, after: Optional[str] = None) -> str:
    """
    Search for posts within a publication using its hostname
    
    Args:
        host: The hostname of the publication (e.g., "blog.budhathokisagar.com.np")
        query: The search query
        first: Number of posts to fetch (default: 10)
        after: Cursor for pagination (optional)
    """
    try:
        variables = {
            "host": host
        }
        
        print(f"Getting publication ID for '{host}'")
        print(f"Query: {GET_PUBLICATION_ID_QUERY}")
        print(f"Variables: {json.dumps(variables)}")
        
        data = await fetch_from_api(GET_PUBLICATION_ID_QUERY, variables)
        
        if not data or "data" not in data or not data["data"] or "publication" not in data["data"] or not data["data"]["publication"]:
            return f"No publication found for hostname '{host}'."
        
        publication = data["data"]["publication"]
        publication_id = publication.get("id")
        title = publication.get("title", "Untitled")
        
        if not publication_id:
            return f"Could not find ID for publication '{title}' with hostname '{host}'."
        
        print(f"Found publication ID '{publication_id}' for '{title}'")
        
        return await search_posts_of_publication(publication_id, query, first, after)
    except Exception as e:
        print(f"Error searching posts by hostname: {str(e)}")
        error_message = f"Error searching for '{query}' in publication with hostname '{host}': {str(e)}"
        
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_content = e.response.text
                error_message += f"\nResponse content: {error_content}"
            except:
                pass
        
        return error_message

@mcp.tool()
async def search_posts_of_publication(publication_id: str, query: str, first: int = 10, after: Optional[str] = None) -> str:
    """
    Search for posts within a specific publication on Hashnode
    
    Args:
        publication_id: The ID of the publication to search within
        query: The search query
        first: Number of posts to fetch (default: 10)
        after: Cursor for pagination (optional)
    """
    variables = {
        "first": first,
        "after": after,
        "filter": {
            "publicationId": publication_id,
            "query": query
        }
    }
    
    try:
        print(f"Searching for '{query}' in publication '{publication_id}'")
        print(f"Query: {SEARCH_POSTS_OF_PUBLICATION_QUERY}")
        print(f"Variables: {json.dumps(variables)}")
        
        data = await fetch_from_api(SEARCH_POSTS_OF_PUBLICATION_QUERY, variables)
        return format_search_results(data)
    except Exception as e:
        print(f"Error searching posts: {str(e)}")
        error_message = f"Error searching for '{query}' in publication '{publication_id}': {str(e)}"
        
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_content = e.response.text
                error_message += f"\nResponse content: {error_content}"
            except:
                pass
        
        return error_message

def main():
    """Entry point for the package."""
    print("Starting Hashnode MCP server...")
    mcp.run()

if __name__ == "__main__":
    main()
