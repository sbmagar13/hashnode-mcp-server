"""
Example usage of the Hashnode MCP server.

This script demonstrates how to use the Hashnode MCP server to interact with the Hashnode API.
"""

import asyncio
import json
from mcp.client import MCPClient

async def main():
    """Run the example."""
    # Connect to the MCP server
    # Note: Make sure the server is running before executing this script
    client = MCPClient("http://localhost:8000")
    
    # Test the API connection
    print("Testing API connection...")
    result = await client.use_tool("test_api_connection")
    print(result)
    print("-" * 50)
    
    # Get posts from a publication
    print("Getting posts from a publication...")
    publication_host = "blog.hashnode.com"  # Replace with a valid Hashnode blog hostname
    posts = await client.use_tool("get_publication_posts", {
        "host": publication_host,
        "first": 3
    })
    print(posts)
    print("-" * 50)
    
    # Get publication ID
    print("Getting publication ID...")
    publication_id_result = await client.use_tool("get_publication_id", {
        "host": publication_host
    })
    print(publication_id_result)
    print("-" * 50)
    
    # Extract publication ID from the result
    # This is a simple parsing of the text result, in a real application you might want to use a more robust method
    publication_id = publication_id_result.split("ID: ")[1].strip() if "ID: " in publication_id_result else None
    
    if publication_id:
        # Search for posts in the publication
        print(f"Searching for posts in publication {publication_id}...")
        search_results = await client.use_tool("search_posts_of_publication", {
            "publication_id": publication_id,
            "query": "python",
            "first": 3
        })
        print(search_results)
        print("-" * 50)
    
    # Search for posts by hostname
    print(f"Searching for posts in publication {publication_host}...")
    search_results = await client.use_tool("search_posts_by_hostname", {
        "host": publication_host,
        "query": "javascript",
        "first": 3
    })
    print(search_results)

if __name__ == "__main__":
    asyncio.run(main())
