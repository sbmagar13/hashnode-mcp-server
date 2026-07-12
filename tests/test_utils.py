"""Tests for hashnode_mcp.utils formatter functions."""
import pytest

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
)


class TestFormatArticleCreation:
    def test_successful_creation(self):
        data = {
            "data": {
                "publishPost": {
                    "post": {
                        "id": "abc123",
                        "slug": "my-article",
                        "title": "My Article",
                        "url": "https://blog.example.com/my-article",
                        "brief": "A brief description",
                        "publishedAt": "2025-01-15T10:00:00Z",
                    }
                }
            }
        }
        result = format_article_creation(data)
        assert "Article Created Successfully" in result
        assert "My Article" in result
        assert "abc123" in result
        assert "https://blog.example.com/my-article" in result

    def test_draft_creation(self):
        data = {
            "data": {
                "publishPost": {
                    "post": {
                        "id": "abc123",
                        "title": "Draft Article",
                    }
                }
            }
        }
        result = format_article_creation(data)
        assert "Draft (Not published)" in result

    def test_no_data(self):
        assert "No data returned" in format_article_creation({})
        assert "No data returned" in format_article_creation({"data": None})

    def test_no_post_returned(self):
        assert "Failed to create" in format_article_creation({"data": {"publishPost": None}})


class TestFormatArticleUpdate:
    def test_successful_update(self):
        data = {
            "data": {
                "updatePost": {
                    "post": {
                        "id": "abc123",
                        "title": "Updated Article",
                        "url": "https://blog.example.com/updated",
                    }
                }
            }
        }
        result = format_article_update(data)
        assert "Article Updated Successfully" in result
        assert "Updated Article" in result

    def test_no_data(self):
        assert "No data returned" in format_article_update({})


class TestFormatSearchResults:
    def test_with_results(self):
        data = {
            "data": {
                "searchPostsOfPublication": {
                    "edges": [
                        {
                            "node": {
                                "title": "Search Result 1",
                                "url": "https://blog.example.com/post1",
                                "slug": "post1",
                                "author": {"name": "John", "username": "john"},
                            }
                        }
                    ],
                    "pageInfo": {"hasNextPage": True, "endCursor": "cursor123"},
                }
            }
        }
        result = format_search_results(data)
        assert "Search Results" in result
        assert "Search Result 1" in result
        assert "Has Next Page: True" in result

    def test_no_results(self):
        data = {"data": {"searchPostsOfPublication": {"edges": []}}}
        assert "No matching posts found" in format_search_results(data)

    def test_empty_data(self):
        assert "No search results found" in format_search_results({})
        assert "No search results found" in format_search_results(None)


class TestFormatPostDetails:
    def test_full_post(self):
        data = {
            "data": {
                "post": {
                    "id": "post1",
                    "slug": "my-post",
                    "title": "Full Post",
                    "subtitle": "A subtitle",
                    "url": "https://blog.example.com/my-post",
                    "canonicalUrl": "https://original.com/post",
                    "publishedAt": "2025-01-15T10:00:00Z",
                    "updatedAt": "2025-01-16T12:00:00Z",
                    "readTimeInMinutes": 5,
                    "views": 1000,
                    "author": {
                        "id": "author1",
                        "username": "john",
                        "name": "John Doe",
                        "profilePicture": "https://img.example.com/john.jpg",
                    },
                    "publication": {
                        "id": "pub1",
                        "title": "My Blog",
                        "displayTitle": "My Blog",
                        "url": "https://blog.example.com",
                    },
                    "coverImage": {
                        "url": "https://img.example.com/cover.jpg",
                        "isPortrait": False,
                    },
                    "brief": "A brief description",
                    "content": {
                        "markdown": "# Hello",
                        "text": "Hello world",
                        "html": "<h1>Hello</h1>",
                    },
                }
            }
        }
        result = format_post_details(data)
        assert "Full Post" in result
        assert "A subtitle" in result
        assert "5 minutes" in result
        assert "1,000" in result or "1000" in result
        assert "John Doe" in result
        assert "My Blog" in result

    def test_no_post(self):
        assert "No post data found" in format_post_details({})
        assert "No post data found" in format_post_details(None)

    def test_missing_fields_graceful(self):
        data = {"data": {"post": {"id": "p1", "title": "Minimal"}}}
        result = format_post_details(data)
        assert "Minimal" in result
        assert "p1" in result


class TestFormatUserInfo:
    def test_full_user(self):
        data = {
            "data": {
                "user": {
                    "id": "user1",
                    "name": "Jane Doe",
                    "username": "jane",
                    "profilePicture": "https://img.example.com/jane.jpg",
                    "bio": {"text": "Software engineer"},
                    "socialMediaLinks": {
                        "twitter": "@jane",
                        "github": "jane",
                        "linkedin": "jane-doe",
                        "website": "https://jane.dev",
                    },
                    "publications": {
                        "edges": [
                            {
                                "node": {
                                    "title": "Jane's Blog",
                                    "url": "https://jane.blog",
                                }
                            }
                        ]
                    },
                    "followersCount": 500,
                    "followingsCount": 200,
                }
            }
        }
        result = format_user_info(data)
        assert "Jane Doe" in result
        assert "Software engineer" in result
        assert "@jane" in result
        assert "500" in result
        assert "200" in result
        assert "Jane's Blog" in result

    def test_no_user(self):
        assert "No user data found" in format_user_info({})
        assert "No user data found" in format_user_info(None)


class TestFormatTopArticles:
    def test_with_results(self):
        data = {
            "data": {
                "feed": {
                    "edges": [
                        {
                            "node": {
                                "id": "feed1",
                                "title": "Trending Post",
                                "url": "https://blog.example.com/trending",
                                "author": {"name": "Author", "username": "author"},
                                "publishedAt": "2025-06-01T00:00:00Z",
                                "brief": "A trending article",
                            }
                        }
                    ]
                }
            }
        }
        result = format_top_articles(data)
        assert "Top Articles on Hashnode" in result
        assert "Trending Post" in result

    def test_no_results(self):
        data = {"data": {"feed": {"edges": []}}}
        assert "No top articles found" in format_top_articles(data)

    def test_no_data(self):
        assert "No top articles data found" in format_top_articles({})
        assert "No top articles data found" in format_top_articles(None)


class TestFormatArticlesByTag:
    def test_with_results(self):
        data = {
            "data": {
                "tag": {
                    "name": "Python",
                    "slug": "python",
                    "posts": {
                        "edges": [
                            {
                                "node": {
                                    "id": "tag1",
                                    "title": "Python Article",
                                    "url": "https://blog.example.com/python",
                                    "author": {"name": "Dev", "username": "dev"},
                                    "publishedAt": "2025-05-01T00:00:00Z",
                                    "brief": "Learn Python",
                                }
                            }
                        ]
                    },
                }
            }
        }
        result = format_articles_by_tag(data)
        assert "Python" in result
        assert "Python Article" in result

    def test_no_articles_for_tag(self):
        data = {"data": {"tag": {"name": "Rare", "slug": "rare", "posts": {"edges": []}}}}
        assert "No articles found" in format_articles_by_tag(data)

    def test_no_data(self):
        assert "No tag data found" in format_articles_by_tag({})
        assert "No tag data found" in format_articles_by_tag(None)


class TestFormatToggleFollow:
    def test_follow(self):
        data = {"data": {"toggleFollowUser": {"user": {"following": True}}}}
        assert "Successfully followed" in format_toggle_follow_result(data)

    def test_unfollow(self):
        data = {"data": {"toggleFollowUser": {"user": {"following": False}}}}
        assert "Successfully unfollowed" in format_toggle_follow_result(data)

    def test_no_data(self):
        assert "No data returned" in format_toggle_follow_result({})


class TestFormatPublishDraft:
    def test_success(self):
        data = {
            "data": {
                "publishDraft": {
                    "post": {
                        "id": "draft1",
                        "title": "From Draft",
                        "url": "https://blog.example.com/from-draft",
                    }
                }
            }
        }
        result = format_publish_draft_result(data)
        assert "Draft Published Successfully" in result
        assert "From Draft" in result

    def test_no_data(self):
        assert "No data returned" in format_publish_draft_result({})


class TestFormatCreateWebhook:
    def test_success(self):
        data = {
            "data": {
                "createWebhook": {
                    "webhook": {
                        "id": "wh1",
                        "url": "https://example.com/webhook",
                        "events": ["POST_PUBLISHED"],
                        "createdAt": "2025-01-01T00:00:00Z",
                    }
                }
            }
        }
        result = format_create_webhook_result(data)
        assert "Webhook Created Successfully" in result
        assert "POST_PUBLISHED" in result

    def test_no_data(self):
        assert "No data returned" in format_create_webhook_result({})


class TestFormatPosts:
    def test_publication_posts(self):
        data = {
            "data": {
                "publication": {
                    "title": "Test Blog",
                    "isTeam": True,
                    "posts": {
                        "edges": [
                            {
                                "node": {
                                    "title": "Team Post",
                                    "url": "https://blog.example.com/team",
                                    "slug": "team-post",
                                    "author": {"name": "Author"},
                                    "publishedAt": "2025-01-01T00:00:00Z",
                                    "brief": "A team post",
                                }
                            }
                        ]
                    },
                }
            }
        }
        result = format_posts(data)
        assert "Test Blog" in result
        assert "Team Publication: Yes" in result
        assert "Team Post" in result

    def test_no_publication(self):
        assert "No data found" in format_posts({})
