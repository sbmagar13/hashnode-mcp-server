"""
Utility functions for the Hashnode MCP server.
"""
import json

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

TOGGLE_FOLLOW_MUTATION = """
mutation ToggleFollowUser($username: String!) {
  toggleFollowUser(username: $username) {
    user {
      following
    }
  }
}
"""

CREATE_ARTICLE_MUTATION = """
mutation PublishPost($input: PublishPostInput!) {
  publishPost(input: $input) {
    post {
      id
      slug
      title
      url
      brief
      publishedAt
      publication {
        id
        title
      }
    }
  }
}
"""

PUBLISH_DRAFT_MUTATION = """
mutation PublishDraft($draftId: ObjectId!) {
  publishDraft(draftId: $draftId) {
    post {
      id
      slug
      title
      url
      brief
      publishedAt
    }
  }
}
"""

CREATE_WEBHOOK_MUTATION = """
mutation CreateWebhook($publicationId: ObjectId!, $url: String!, $events: [WebhookEvent!]!, $secret: String!) {
  createWebhook(
    input: {
      publicationId: $publicationId
      url: $url
      events: $events
      secret: $secret
    }
  ) {
    webhook {
      id
      url
      events
      createdAt
      updatedAt
    }
  }
}
"""

UPDATE_ARTICLE_MUTATION = """
mutation UpdatePost($input: UpdatePostInput!) {
  updatePost(input: $input) {
    post {
      id
      slug
      title
      url
      brief
      publishedAt
    }
  }
}
"""

GET_POST_BY_ID_QUERY = """
query Post($id: ID!) {
  post(id: $id) {
    id
    slug
    previousSlugs
    title
    subtitle
    author {
      id
      username
      name
      profilePicture
    }
    url
    canonicalUrl
    publication {
      id
      title
      displayTitle
      url
    }
    cuid
    coverImage {
      url
      isPortrait
      attribution
      photographer
      isAttributionHidden
    }
    brief
    readTimeInMinutes
    views
    content {
      markdown
      html
      text
    }
    publishedAt
    updatedAt
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
  $filter: SearchPostsOfPublicationFilter!
) {
  searchPostsOfPublication(
    first: $first,
    after: $after,
    sortBy: DATE_PUBLISHED_DESC,
    filter: $filter
  ) {
    edges {
      node {
        id
        title
        brief
        publishedAt
        author {
          name
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

GET_TOP_ARTICLES_QUERY = """
query GetTopArticles($first: Int!) {
  feed(first: $first) {
    edges {
      node {
        ... on Post {
          id
          title
          brief
          url
          publishedAt
          author {
            name
            username
          }
        }
      }
    }
  }
}
"""

GET_ARTICLES_BY_TAG_QUERY = """
query GetArticlesByTag($tag: String!, $first: Int!) {
  tag(slug: $tag) {
    name
    slug
    posts(first: $first) {
      edges {
        node {
          id
          title
          brief
          url
          publishedAt
          author {
            name
            username
          }
        }
      }
    }
  }
}
"""

GET_USER_INFO_QUERY = """
query GetUserInfo($username: String!) {
  user(username: $username) {
    id
    name
    username
    profilePicture
    bio {
      text
    }
    socialMediaLinks {
      twitter
      github
      linkedin
      website
    }
    publications(first: 5) {
      edges {
        node {
          id
          title
          url
        }
      }
    }
    followersCount
    followingsCount
  }
}
"""

GET_ARTICLES_BY_USERNAME_QUERY = """
query GetArticlesByUsername($username: String!, $first: Int!) {
  user(username: $username) {
    id
    name
    username
    posts(first: $first) {
      edges {
        node {
          id
          title
          brief
          url
          publishedAt
        }
      }
    }
  }
}
"""

def format_article_creation(creation_data: dict) -> str:
    """
    Format article creation response data for display
    
    Args:
        creation_data: The data returned from the Hashnode API after creating an article
        
    Returns:
        A formatted string representation of the created article
    """
    if not creation_data or "data" not in creation_data or not creation_data["data"]:
        return "No data returned from article creation."
    
    if "publishPost" in creation_data["data"] and creation_data["data"]["publishPost"]:
        result = creation_data["data"]["publishPost"]
        if "post" in result and result["post"]:
            post = result["post"]
            response = "# Article Created Successfully\n\n"
            response += f"Title: {post.get('title', 'Untitled')}\n"
            response += f"ID: {post.get('id', 'Unknown')}\n"
            
            if "slug" in post:
                response += f"Slug: {post['slug']}\n"
            
            if "url" in post:
                response += f"URL: {post['url']}\n"
            
            if "brief" in post and post["brief"]:
                response += f"Brief: {post['brief']}\n"
            
            if "publishedAt" in post and post["publishedAt"]:
                response += f"Published At: {post['publishedAt']}\n"
            else:
                response += "Status: Draft (Not published)\n"
            
            return response
        
        return "Article created but no post data returned."
    
    return "Failed to create article."

def format_article_update(update_data: dict) -> str:
    """
    Format article update response data for display
    
    Args:
        update_data: The data returned from the Hashnode API after updating an article
        
    Returns:
        A formatted string representation of the updated article
    """
    if not update_data or "data" not in update_data or not update_data["data"]:
        return "No data returned from article update."
    
    if "updatePost" in update_data["data"] and update_data["data"]["updatePost"]:
        result = update_data["data"]["updatePost"]
        if "post" in result and result["post"]:
            post = result["post"]
            response = "# Article Updated Successfully\n\n"
            response += f"Title: {post.get('title', 'Untitled')}\n"
            response += f"ID: {post.get('id', 'Unknown')}\n"
            
            if "slug" in post:
                response += f"Slug: {post['slug']}\n"
            
            if "url" in post:
                response += f"URL: {post['url']}\n"
            
            if "brief" in post and post["brief"]:
                response += f"Brief: {post['brief']}\n"
            
            if "publishedAt" in post and post["publishedAt"]:
                response += f"Published At: {post['publishedAt']}\n"
            else:
                response += "Status: Draft (Not published)\n"
            
            return response
        
        return "Article updated but no post data returned."
    
    return "Failed to update article."

def format_toggle_follow_result(toggle_data: dict) -> str:
    """
    Format toggle follow response data for display
    
    Args:
        toggle_data: The data returned from the Hashnode API after toggling follow status
        
    Returns:
        A formatted string representation of the toggle follow result
    """
    if not toggle_data or "data" not in toggle_data or not toggle_data["data"]:
        return "No data returned from toggle follow operation."
    
    if "toggleFollowUser" in toggle_data["data"] and toggle_data["data"]["toggleFollowUser"]:
        result = toggle_data["data"]["toggleFollowUser"]
        if "user" in result and "following" in result["user"]:
            status = result["user"]["following"]
            if status:
                return "Successfully followed the user."
            else:
                return "Successfully unfollowed the user."
    
    return "Failed to toggle follow status."

def format_publish_draft_result(publish_data: dict) -> str:
    """
    Format publish draft response data for display
    
    Args:
        publish_data: The data returned from the Hashnode API after publishing a draft
        
    Returns:
        A formatted string representation of the published draft
    """
    if not publish_data or "data" not in publish_data or not publish_data["data"]:
        return "No data returned from draft publication."
    
    if "publishDraft" in publish_data["data"] and publish_data["data"]["publishDraft"]:
        result = publish_data["data"]["publishDraft"]
        if "post" in result and result["post"]:
            post = result["post"]
            response = "# Draft Published Successfully\n\n"
            response += f"Title: {post.get('title', 'Untitled')}\n"
            response += f"ID: {post.get('id', 'Unknown')}\n"
            
            if "slug" in post:
                response += f"Slug: {post['slug']}\n"
            
            if "url" in post:
                response += f"URL: {post['url']}\n"
            
            if "brief" in post and post["brief"]:
                response += f"Brief: {post['brief']}\n"
            
            if "publishedAt" in post and post["publishedAt"]:
                response += f"Published At: {post['publishedAt']}\n"
            
            return response
        
        return "Draft published but no post data returned."
    
    return "Failed to publish draft."

def format_create_webhook_result(webhook_data: dict) -> str:
    """
    Format create webhook response data for display
    
    Args:
        webhook_data: The data returned from the Hashnode API after creating a webhook
        
    Returns:
        A formatted string representation of the created webhook
    """
    if not webhook_data or "data" not in webhook_data or not webhook_data["data"]:
        return "No data returned from webhook creation."
    
    if "createWebhook" in webhook_data["data"] and webhook_data["data"]["createWebhook"]:
        result = webhook_data["data"]["createWebhook"]
        if "webhook" in result and result["webhook"]:
            webhook = result["webhook"]
            response = "# Webhook Created Successfully\n\n"
            response += f"ID: {webhook.get('id', 'Unknown')}\n"
            
            if "url" in webhook:
                response += f"URL: {webhook['url']}\n"
            
            if "events" in webhook and webhook["events"]:
                response += f"Events: {', '.join(webhook['events'])}\n"
            
            if "createdAt" in webhook:
                response += f"Created At: {webhook['createdAt']}\n"
            
            if "updatedAt" in webhook:
                response += f"Updated At: {webhook['updatedAt']}\n"
            
            return response
        
        return "Webhook created but no webhook data returned."
    
    return "Failed to create webhook."

def format_post_details(post_data: dict) -> str:
    """
    Format post details data for display
    
    Args:
        post_data: The data returned from the Hashnode API for a specific post
        
    Returns:
        A formatted string representation of the post details
    """
    if not post_data or "data" not in post_data or not post_data["data"]:
        return "No post data found."
    
    if "post" in post_data["data"] and post_data["data"]["post"]:
        post = post_data["data"]["post"]
        result = f"# {post.get('title', 'Untitled')}\n\n"
        
        if "subtitle" in post and post["subtitle"]:
            result += f"## {post['subtitle']}\n\n"
        
        # Basic post information
        result += "## Post Information\n\n"
        result += f"ID: {post.get('id', 'Unknown')}\n"
        result += f"Slug: {post.get('slug', 'Unknown')}\n"
        
        if "url" in post and post["url"]:
            result += f"URL: {post['url']}\n"
        
        if "canonicalUrl" in post and post["canonicalUrl"]:
            result += f"Canonical URL: {post['canonicalUrl']}\n"
        
        if "publishedAt" in post and post["publishedAt"]:
            result += f"Published: {post['publishedAt']}\n"
        
        if "updatedAt" in post and post["updatedAt"]:
            result += f"Last Updated: {post['updatedAt']}\n"
        
        if "readTimeInMinutes" in post:
            result += f"Read Time: {post['readTimeInMinutes']} minutes\n"
        
        if "views" in post:
            result += f"Views: {post['views']}\n"
        
        # Author information
        if "author" in post and post["author"]:
            author = post["author"]
            result += "\n## Author\n\n"
            result += f"Name: {author.get('name', 'Unknown')}\n"
            
            if "username" in author:
                result += f"Username: {author['username']}\n"
            
            if "id" in author:
                result += f"ID: {author['id']}\n"
            
            if "profilePicture" in author and author["profilePicture"]:
                result += f"Profile Picture: {author['profilePicture']}\n"
        
        # Publication information
        if "publication" in post and post["publication"]:
            publication = post["publication"]
            result += "\n## Publication\n\n"
            result += f"Title: {publication.get('title', 'Unknown')}\n"
            
            if "displayTitle" in publication:
                result += f"Display Title: {publication['displayTitle']}\n"
            
            if "id" in publication:
                result += f"ID: {publication['id']}\n"
            
            if "url" in publication:
                result += f"URL: {publication['url']}\n"
        
        # Cover image
        if "coverImage" in post and post["coverImage"]:
            cover_image = post["coverImage"]
            result += "\n## Cover Image\n\n"
            
            if "url" in cover_image:
                result += f"URL: {cover_image['url']}\n"
            
            if "isPortrait" in cover_image:
                result += f"Is Portrait: {cover_image['isPortrait']}\n"
            
            if "photographer" in cover_image and cover_image["photographer"]:
                result += f"Photographer: {cover_image['photographer']}\n"
            
            if "attribution" in cover_image and cover_image["attribution"]:
                result += f"Attribution: {cover_image['attribution']}\n"
        
        # Brief
        if "brief" in post and post["brief"]:
            result += f"\n## Brief\n\n{post['brief']}\n"
        
        # Content
        if "content" in post and post["content"]:
            content = post["content"]
            result += "\n## Content\n\n"
            
            if "text" in content and content["text"]:
                # Limit the text content to a reasonable length for display
                text = content["text"]
                max_length = 1000
                if len(text) > max_length:
                    text = text[:max_length] + "...\n\n(Content truncated for display. Full content available in the markdown or html fields.)"
                result += text
            
            # Note: We're not including the full markdown or HTML content in the display
            # as they could be very large, but we note their availability
            if "markdown" in content and content["markdown"]:
                result += "\n\n(Full markdown content available but not displayed due to length)"
            
            if "html" in content and content["html"]:
                result += "\n\n(Full HTML content available but not displayed due to length)"
        
        return result
    
    return "No post data found."

def format_top_articles(top_articles_data: dict) -> str:
    """
    Format top articles data for display
    
    Args:
        top_articles_data: The data returned from the Hashnode API for top articles
        
    Returns:
        A formatted string representation of the top articles
    """
    if not top_articles_data or "data" not in top_articles_data or not top_articles_data["data"]:
        return "No top articles data found."
    
    if "feed" in top_articles_data["data"] and "edges" in top_articles_data["data"]["feed"]:
        edges = top_articles_data["data"]["feed"]["edges"]
        result = "# Top Articles on Hashnode\n\n"
        
        if not edges:
            return "No top articles found."
        
        for edge in edges:
            if "node" in edge:
                node = edge["node"]
                title = node.get("title", "Untitled")
                result += f"## {title}\n"
                
                if "id" in node:
                    result += f"ID: {node['id']}\n"
                
                if "url" in node:
                    result += f"URL: {node['url']}\n"
                
                if "author" in node and node["author"]:
                    author = node["author"]
                    result += f"Author: {author.get('name', 'Unknown')}"
                    if "username" in author:
                        result += f" (@{author['username']})"
                    result += "\n"
                
                if "publishedAt" in node and node["publishedAt"]:
                    from datetime import datetime
                    try:
                        published_date = datetime.fromisoformat(node["publishedAt"].replace("Z", "+00:00"))
                        result += f"Published: {published_date.strftime('%b %d, %Y')}\n"
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
    
    return "No top articles data found."

def format_articles_by_tag(tag_data: dict) -> str:
    """
    Format articles by tag data for display
    
    Args:
        tag_data: The data returned from the Hashnode API for articles by tag
        
    Returns:
        A formatted string representation of the articles by tag
    """
    if not tag_data or "data" not in tag_data or not tag_data["data"]:
        return "No tag data found."
    
    if "tag" in tag_data["data"] and tag_data["data"]["tag"]:
        tag = tag_data["data"]["tag"]
        tag_name = tag.get("name", tag.get("slug", "Unknown Tag"))
        result = f"# Articles with Tag: {tag_name}\n\n"
        
        if "posts" not in tag or "edges" not in tag["posts"] or not tag["posts"]["edges"]:
            return f"No articles found with tag '{tag_name}'."
        
        for edge in tag["posts"]["edges"]:
            if "node" in edge:
                node = edge["node"]
                title = node.get("title", "Untitled")
                result += f"## {title}\n"
                
                if "id" in node:
                    result += f"ID: {node['id']}\n"
                
                if "url" in node:
                    result += f"URL: {node['url']}\n"
                
                if "author" in node and node["author"]:
                    author = node["author"]
                    result += f"Author: {author.get('name', 'Unknown')}"
                    if "username" in author:
                        result += f" (@{author['username']})"
                    result += "\n"
                
                if "publishedAt" in node and node["publishedAt"]:
                    from datetime import datetime
                    try:
                        published_date = datetime.fromisoformat(node["publishedAt"].replace("Z", "+00:00"))
                        result += f"Published: {published_date.strftime('%b %d, %Y')}\n"
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
    
    return "No tag data found."

def format_user_info(user_data: dict) -> str:
    """
    Format user information data for display
    
    Args:
        user_data: The data returned from the Hashnode API for a specific user
        
    Returns:
        A formatted string representation of the user information
    """
    if not user_data or "data" not in user_data or not user_data["data"]:
        return "No user data found."
    
    if "user" in user_data["data"] and user_data["data"]["user"]:
        user = user_data["data"]["user"]
        result = f"# User: {user.get('name', 'Unknown')}\n\n"
        
        # Basic user information
        result += "## User Information\n\n"
        result += f"ID: {user.get('id', 'Unknown')}\n"
        result += f"Username: {user.get('username', 'Unknown')}\n"
        
        if "profilePicture" in user and user["profilePicture"]:
            result += f"Profile Picture: {user['profilePicture']}\n"
        
        if "followersCount" in user:
            result += f"Followers: {user['followersCount']}\n"
        
        if "followingsCount" in user:
            result += f"Following: {user['followingsCount']}\n"
        
        # Bio
        if "bio" in user and user["bio"] and "text" in user["bio"] and user["bio"]["text"]:
            result += f"\n## Bio\n\n{user['bio']['text']}\n"
        
        # Social media links
        if "socialMediaLinks" in user and user["socialMediaLinks"]:
            social_media = user["socialMediaLinks"]
            result += "\n## Social Media\n\n"
            
            if "twitter" in social_media and social_media["twitter"]:
                result += f"Twitter: {social_media['twitter']}\n"
            
            if "github" in social_media and social_media["github"]:
                result += f"GitHub: {social_media['github']}\n"
            
            if "linkedin" in social_media and social_media["linkedin"]:
                result += f"LinkedIn: {social_media['linkedin']}\n"
            
            if "website" in social_media and social_media["website"]:
                result += f"Website: {social_media['website']}\n"
        
        # Publications
        if "publications" in user and "edges" in user["publications"] and user["publications"]["edges"]:
            result += "\n## Publications\n\n"
            for edge in user["publications"]["edges"]:
                if "node" in edge:
                    node = edge["node"]
                    result += f"- {node.get('title', 'Untitled')}"
                    
                    if "url" in node and node["url"]:
                        result += f" ({node['url']})"
                    
                    result += "\n"
        
        return result
    
    return "No user data found."
