# Hashnode MCP Server

A Model Context Protocol (MCP) server for interacting with the Hashnode API. This server provides tools for accessing and searching Hashnode content programmatically.

## Features

- Test API connection to Hashnode
- Fetch posts from specific publications
- Get publication IDs from hostnames
- Search for posts within publications
- Detailed formatting of post data and search results

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/sbmagar13/hashnode-mcp-server.git
   cd hashnode-mcp-server
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory with your Hashnode API credentials:
   ```
   HASHNODE_PERSONAL_ACCESS_TOKEN=your_personal_access_token
   HASHNODE_API_URL=https://gql.hashnode.com
   ```

## Usage

### Starting the Server

Run the MCP server:

```bash
python mcp_server.py
```

### Available Tools

The server provides the following tools:

- `test_api_connection()`: Test the connection to the Hashnode API
- `get_publication_posts(host, first=5)`: Get posts from a specific publication
- `get_publication_id(host)`: Get the publication ID from a hostname
- `search_posts_of_publication(publication_id, query, first=10)`: Search for posts within a specific publication
- `search_posts_by_hostname(host, query, first=10)`: Search for posts within a publication using its hostname
- `get_article_details(article_id)`: Get detailed information about a specific article
- `get_articles_by_username(username)`: Get articles written by a specific user [Coming Soon]
- `get_user_info(username)`: Get information about a Dev.to user [Coming Soon]
- `create_article(title, body_markdown, tags, published)`: Create and publish a new article
- `update_article(article_id, title, body_markdown, tags, published)`: Update an existing article
- `toggle_follow(username)`: Follow or unfollow a user based on the specified username
- `publish_draft(draft_id)`: Publish a draft with the specified ID
- `create_webhook(publication_host, url, events, secret)`: Create a webhook for the publication

### Example Usage

```python
from mcp.client import MCPClient

# Connect to the MCP server
client = MCPClient("http://localhost:8000")

# Test the API connection
result = client.use_tool("test_api_connection")
print(result)

# Get posts from a publication
posts = client.use_tool("get_publication_posts", {"host": "blog.example.com", "first": 10})
print(posts)

# Search for posts
search_results = client.use_tool("search_posts_by_hostname", {
    "host": "blog.example.com",
    "query": "python",
    "first": 5
})
print(search_results)

# Get detailed information about a specific article
article_details = client.use_tool("get_article_details", {"article_id": "123456"})
print(article_details)

# Create a new article
new_article = client.use_tool("create_article", {
    "title": "My New Article",
    "body_markdown": "# Hello World\n\nThis is my first article on Hashnode!",
    "tags": "python,tutorial,beginners",
    "published": False  # Save as draft
})
print(new_article)

# Update an existing article
updated_article = client.use_tool("update_article", {
    "article_id": "123456",
    "title": "Updated Title",
    "published": True  # Publish the article
})
print(updated_article)

# Follow a user
follow_result = client.use_tool("toggle_follow", {
    "username": "johndoe"
})
print(follow_result)

# Publish a draft
published_draft = client.use_tool("publish_draft", {
    "draft_id": "789012"
})
print(published_draft)

# Create a webhook
webhook = client.use_tool("create_webhook", {
    "publication_host": "blog.example.com",
    "url": "https://webhook.site/123456",
    "events": "post_published,post_updated",
    "secret": "my_secret_key"
})
print(webhook)
```

## Environment Variables

- `HASHNODE_PERSONAL_ACCESS_TOKEN`: Your Hashnode personal access token
- `HASHNODE_API_URL`: The Hashnode GraphQL API URL (default: https://gql.hashnode.com)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## GitHub Repository

The source code for this project is available on GitHub:
https://github.com/sbmagar13/hashnode-mcp-server

## Acknowledgments

- [Hashnode](https://hashnode.com/) for providing the API
- [Model Context Protocol (MCP)](https://github.com/modelcontextprotocol/mcp) for the server framework
