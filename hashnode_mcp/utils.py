"""
Utility functions for the Hashnode MCP server.
"""

def format_posts(posts_data: dict) -> str:
    """
    Format posts data for display
    
    Args:
        posts_data: The data returned from the Hashnode API
        
    Returns:
        A formatted string representation of the posts data
    """
    if not posts_data or "data" not in posts_data or not posts_data["data"]:
        return "No data found."
    
    if "publication" in posts_data["data"] and posts_data["data"]["publication"]:
        publication = posts_data["data"]["publication"]
        result = f"# Publication: {publication.get('title', 'Untitled')}\n\n"
        result += f"Team Publication: {'Yes' if publication.get('isTeam', False) else 'No'}\n\n"
        
        if "posts" in publication and "edges" in publication["posts"]:
            result += "## Posts\n\n"
            for edge in publication["posts"]["edges"]:
                if "node" in edge:
                    node = edge["node"]
                    result += f"### {node.get('title', 'Untitled')}\n"
                    
                    if "url" in node and node["url"]:
                        result += f"URL: {node['url']}\n"
                    
                    result += f"Slug: {node.get('slug', '')}\n"
                    
                    if "publishedAt" in node and node["publishedAt"]:
                        result += f"Date: {node['publishedAt']}\n"
                    
                    if "author" in node and node["author"]:
                        author = node["author"]
                        result += f"Author: {author.get('name', 'Unknown')}\n"
                        if "username" in author:
                            result += f"Author Username: {author['username']}\n"
                        if "profilePicture" in author and author["profilePicture"]:
                            result += f"Author Profile Picture: {author['profilePicture']}\n"
                    
                    if "coverImage" in node and node["coverImage"] and "url" in node["coverImage"]:
                        result += f"Cover Image: {node['coverImage']['url']}\n"
                    
                    result += f"Brief: {node.get('brief', 'No description available.')}\n\n"
        
        return result
    
    return "No publication data found."

def format_search_results(search_data: dict) -> str:
    """
    Format search results data for display
    
    Args:
        search_data: The data returned from the Hashnode API search
        
    Returns:
        A formatted string representation of the search results
    """
    if not search_data or "data" not in search_data or not search_data["data"]:
        return "No search results found."
    
    if "searchPostsOfPublication" in search_data["data"]:
        search_results = search_data["data"]["searchPostsOfPublication"]
        result = "# Search Results\n\n"
        
        if "edges" in search_results and search_results["edges"]:
            for edge in search_results["edges"]:
                if "node" in edge:
                    node = edge["node"]
                    result += f"## {node.get('title', 'Untitled')}\n"
                    
                    if "url" in node and node["url"]:
                        result += f"URL: {node['url']}\n"
                    
                    result += f"Slug: {node.get('slug', '')}\n"
                    
                    if "publishedAt" in node and node["publishedAt"]:
                        result += f"Date: {node['publishedAt']}\n"
                    
                    if "author" in node and node["author"]:
                        author = node["author"]
                        result += f"Author: {author.get('name', 'Unknown')}\n"
                        if "username" in author:
                            result += f"Author Username: {author['username']}\n"
                        if "profilePicture" in author and author["profilePicture"]:
                            result += f"Author Profile Picture: {author['profilePicture']}\n"
                    
                    if "coverImage" in node and node["coverImage"] and "url" in node["coverImage"]:
                        result += f"Cover Image: {node['coverImage']['url']}\n"
                    
                    result += f"Brief: {node.get('brief', 'No description available.')}\n\n"
            
            if "pageInfo" in search_results:
                page_info = search_results["pageInfo"]
                result += "## Pagination\n"
                result += f"Has Next Page: {page_info.get('hasNextPage', False)}\n"
                if page_info.get('hasNextPage', False) and "endCursor" in page_info:
                    result += f"End Cursor: {page_info['endCursor']}\n"
                result += "\n"
            
            return result
        else:
            return "No matching posts found."
    
    return "No search results found."

# GraphQL query constants
TEST_QUERY = """
query {
  __schema {
    queryType {
      name
    }
  }
}
"""

GET_PUBLICATION_ID_QUERY = """
query GetPublicationByHost($host: String!) {
    publication(host: $host) {
        id
        title
    }
}
"""

GET_PUBLICATION_POSTS_QUERY = """
query GetPublicationByHost($host: String!, $first: Int!) {
    publication(host: $host) {
        isTeam
        title
        posts(first: $first) {
            edges {
                node {
                    title
                    brief
                    url
                }
            }
        }
    }
}
"""

SEARCH_POSTS_OF_PUBLICATION_QUERY = """
query SearchPostsOfPublication(
  $first: Int!,
  $after: String,
  $sortBy: PostSortBy,
  $filter: SearchPostsOfPublicationFilter!
) {
  searchPostsOfPublication(
    first: $first,
    after: $after,
    sortBy: $sortBy,
    filter: $filter
  ) {
    edges {
      node {
        title
        brief
        url
        slug
        publishedAt
        author {
          name
          username
          profilePicture
        }
        coverImage {
          url
        }
      }
      cursor
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
"""
