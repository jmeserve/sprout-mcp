import json
import os

import httpx
from mcp.server.fastmcp import FastMCP

from .client import SproutClient

mcp = FastMCP("sprout-social")

_client: SproutClient | None = None


def _get_client() -> SproutClient:
    global _client
    if _client is None:
        _client = SproutClient()
    return _client


def _cid(customer_id: str) -> str:
    result = customer_id or os.environ.get("SPROUT_CUSTOMER_ID", "")
    if not result:
        raise ValueError(
            "customer_id is required. Pass it explicitly or set SPROUT_CUSTOMER_ID env var."
        )
    return result


def _split(s: str) -> list[str]:
    return [x.strip() for x in s.split(",") if x.strip()]


def _date(dt: str) -> str:
    """Extract YYYY-MM-DD from an ISO 8601 datetime string."""
    return dt[:10]


def _err(e: Exception) -> str:
    """Return a structured JSON error string from an exception."""
    if isinstance(e, httpx.HTTPStatusError):
        try:
            detail = e.response.json()
        except Exception:
            detail = e.response.text
        return json.dumps({
            "error": f"HTTP {e.response.status_code}",
            "url": str(e.request.url),
            "detail": detail,
        }, indent=2)
    return json.dumps({"error": type(e).__name__, "message": str(e)}, indent=2)


# ===== METADATA =====


@mcp.tool()
async def list_customers() -> str:
    """List all customers/accounts accessible with the current API token.

    Returns customer IDs and names needed for other API calls.
    """
    try:
        data = await _get_client().get("/v1/metadata/client")
        return json.dumps(data, indent=2)
    except Exception as e:
        return _err(e)


@mcp.tool()
async def list_profiles(customer_id: str = "") -> str:
    """List all social profiles for a customer.

    Args:
        customer_id: Sprout customer ID. Defaults to SPROUT_CUSTOMER_ID env var.
    """
    try:
        data = await _get_client().get(f"/v1/{_cid(customer_id)}/metadata/customer")
        return json.dumps(data, indent=2)
    except Exception as e:
        return _err(e)


@mcp.tool()
async def list_tags(customer_id: str = "") -> str:
    """List all message tags for a customer.

    Args:
        customer_id: Sprout customer ID. Defaults to SPROUT_CUSTOMER_ID env var.
    """
    try:
        data = await _get_client().get(f"/v1/{_cid(customer_id)}/metadata/customer/tags")
        return json.dumps(data, indent=2)
    except Exception as e:
        return _err(e)


@mcp.tool()
async def list_groups(customer_id: str = "") -> str:
    """List all profile groups for a customer.

    Args:
        customer_id: Sprout customer ID. Defaults to SPROUT_CUSTOMER_ID env var.
    """
    try:
        data = await _get_client().get(f"/v1/{_cid(customer_id)}/metadata/customer/groups")
        return json.dumps(data, indent=2)
    except Exception as e:
        return _err(e)


@mcp.tool()
async def list_users(customer_id: str = "") -> str:
    """List all active users for a customer.

    Args:
        customer_id: Sprout customer ID. Defaults to SPROUT_CUSTOMER_ID env var.
    """
    try:
        data = await _get_client().get(f"/v1/{_cid(customer_id)}/metadata/customer/users")
        return json.dumps(data, indent=2)
    except Exception as e:
        return _err(e)


@mcp.tool()
async def list_teams(customer_id: str = "") -> str:
    """List all teams for a customer.

    Args:
        customer_id: Sprout customer ID. Defaults to SPROUT_CUSTOMER_ID env var.
    """
    try:
        data = await _get_client().get(f"/v1/{_cid(customer_id)}/metadata/customer/teams")
        return json.dumps(data, indent=2)
    except Exception as e:
        return _err(e)


# ===== ANALYTICS =====


@mcp.tool()
async def get_profile_analytics(
    profile_ids: str,
    start_time: str,
    end_time: str,
    metrics: str = "impressions,engagements,net_follower_growth",
    timezone: str = "UTC",
    customer_id: str = "",
) -> str:
    """Get analytics metrics aggregated by social profile.

    Args:
        profile_ids: Comma-separated Sprout profile IDs.
        start_time: Start of period (ISO 8601, e.g. '2024-01-01T00:00:00').
        end_time: End of period (ISO 8601, e.g. '2024-01-31T23:59:59').
        metrics: Comma-separated metric names. Common options:
                 impressions, engagements, net_follower_growth, engagement_rate,
                 video_views, reactions, comments, shares, clicks.
        timezone: Timezone for the report (e.g. 'America/Chicago'). Default: UTC.
        customer_id: Sprout customer ID. Defaults to SPROUT_CUSTOMER_ID env var.
    """
    try:
        ids = ",".join(_split(profile_ids))
        start_date = _date(start_time)
        end_date = _date(end_time)
        body = {
            "filters": [
                f"customer_profile_id.eq({ids})",
                f"reporting_period.in({start_date}...{end_date})",
            ],
            "metrics": _split(metrics),
            "timezone": timezone,
        }
        data = await _get_client().post(f"/v1/{_cid(customer_id)}/analytics/profiles", body)
        return json.dumps(data, indent=2)
    except Exception as e:
        return _err(e)


@mcp.tool()
async def get_post_analytics(
    profile_ids: str,
    start_time: str,
    end_time: str,
    metrics: str = "lifetime.impressions,lifetime.reactions,lifetime.engagements,lifetime.clicks",
    limit: int = 50,
    customer_id: str = "",
) -> str:
    """Get analytics metrics for individual published posts.

    Post-level metrics require the 'lifetime.' prefix.
    Common metrics: lifetime.impressions, lifetime.reactions, lifetime.engagements,
                    lifetime.clicks, lifetime.shares, lifetime.comments, lifetime.video_views.

    Use the count of returned posts as the post count for a profile.
    Do NOT use get_messages with an OUTBOUND filter for post counts — that endpoint
    only supports inbound inbox messages.

    Args:
        profile_ids: Comma-separated Sprout profile IDs.
        start_time: Start of period (ISO 8601, e.g. '2024-01-01T00:00:00').
        end_time: End of period (ISO 8601, e.g. '2024-01-31T23:59:59').
        metrics: Comma-separated metric names with lifetime. prefix.
        limit: Number of posts to return (default 50, max 100).
        customer_id: Sprout customer ID. Defaults to SPROUT_CUSTOMER_ID env var.
    """
    try:
        ids = ",".join(_split(profile_ids))
        body = {
            "filters": [
                f"customer_profile_id.eq({ids})",
                f"created_time.in({start_time}..{end_time})",
            ],
            "fields": ["created_time", "text", "perma_link"],
            "metrics": _split(metrics),
            "limit": limit,
            "sort": ["created_time:desc"],
        }
        data = await _get_client().post(f"/v1/{_cid(customer_id)}/analytics/posts", body)
        return json.dumps(data, indent=2)
    except Exception as e:
        return _err(e)


# ===== LISTENING =====


@mcp.tool()
async def list_listening_topics(customer_id: str = "") -> str:
    """List all Listening topics configured for a customer.

    Returns topic IDs and names needed for get_listening_messages.

    Args:
        customer_id: Sprout customer ID. Defaults to SPROUT_CUSTOMER_ID env var.
    """
    try:
        data = await _get_client().get(f"/v1/{_cid(customer_id)}/listening/topics")
        return json.dumps(data, indent=2)
    except Exception as e:
        return _err(e)


@mcp.tool()
async def get_listening_messages(
    topic_id: str,
    start_time: str,
    end_time: str,
    networks: str = "",
    limit: int = 100,
    cursor: str = "",
    customer_id: str = "",
) -> str:
    """Fetch messages from a Sprout Social Listening topic.

    Use list_listening_topics first to get topic IDs.

    Args:
        topic_id: The listening topic ID (UUID).
        start_time: Start datetime (ISO 8601, e.g. '2024-01-01T00:00:00').
        end_time: End datetime (ISO 8601, e.g. '2024-01-31T23:59:59').
        networks: Comma-separated networks to filter by. Options: REDDIT, TWITTER,
                  FACEBOOK, INSTAGRAM, YOUTUBE, NEWS, BLOG. Leave empty for all.
        limit: Number of messages to return per page (default 100, max 100).
        cursor: Pagination cursor from a previous response (optional).
        customer_id: Sprout customer ID. Defaults to SPROUT_CUSTOMER_ID env var.
    """
    try:
        filters = [f"created_time.in({start_time}..{end_time})"]
        if networks:
            for network in _split(networks):
                filters.append(f"network.eq({network.upper()})")

        body: dict = {
            "filters": filters,
            "fields": ["created_time", "text", "network", "perma_link", "language"],
            "limit": limit,
            "sort": ["created_time:desc"],
        }
        if cursor:
            body["cursor"] = cursor

        data = await _get_client().post(
            f"/v1/{_cid(customer_id)}/listening/topics/{topic_id}/messages", body
        )
        return json.dumps(data, indent=2)
    except Exception as e:
        return _err(e)


# ===== MESSAGES =====


@mcp.tool()
async def get_messages(
    profile_ids: str,
    start_time: str,
    end_time: str,
    tag_ids: str = "",
    limit: int = 50,
    page_cursor: str = "",
    customer_id: str = "",
) -> str:
    """Retrieve inbound inbox messages (Smart Inbox) with optional filtering.

    This endpoint returns INBOUND messages only (mentions, DMs, comments).
    For published post counts and performance metrics, use get_post_analytics instead.
    For social listening data (Reddit, news, etc.), use get_listening_messages instead.

    Args:
        profile_ids: Comma-separated Sprout profile IDs.
        start_time: Start datetime (ISO 8601, e.g. '2024-01-01T00:00:00').
        end_time: End datetime (ISO 8601).
        tag_ids: Comma-separated tag IDs to filter by (optional).
        limit: Number of messages to return (default 50).
        page_cursor: Pagination cursor from a previous response (optional).
        customer_id: Sprout customer ID. Defaults to SPROUT_CUSTOMER_ID env var.
    """
    try:
        ids = ",".join(_split(profile_ids))
        filters = [
            f"customer_profile_id.eq({ids})",
            f"created_time.in({start_time}..{end_time})",
        ]
        if tag_ids:
            tag_list = ",".join(_split(tag_ids))
            filters.append(f"tag_id.eq({tag_list})")

        body: dict = {"filters": filters, "limit": limit}
        if page_cursor:
            body["page_cursor"] = page_cursor

        data = await _get_client().post(f"/v1/{_cid(customer_id)}/messages", body)
        return json.dumps(data, indent=2)
    except Exception as e:
        return _err(e)


# ===== PUBLISHING =====


@mcp.tool()
async def list_publishing_posts(
    profile_ids: str,
    start_time: str,
    end_time: str,
    status: str = "",
    limit: int = 50,
    customer_id: str = "",
) -> str:
    """List published, scheduled, or draft posts in Sprout Social.

    Args:
        profile_ids: Comma-separated Sprout profile IDs.
        start_time: Start datetime (ISO 8601, e.g. '2024-01-01T00:00:00').
        end_time: End datetime (ISO 8601).
        status: Filter by post status: PUBLISHED, SCHEDULED, DRAFT. Leave empty for all.
        limit: Number of posts to return (default 50).
        customer_id: Sprout customer ID. Defaults to SPROUT_CUSTOMER_ID env var.
    """
    try:
        ids = ",".join(_split(profile_ids))
        filters = [
            f"customer_profile_id.eq({ids})",
            f"created_time.in({start_time}..{end_time})",
        ]
        if status:
            filters.append(f"status.eq({status.upper()})")

        body: dict = {
            "filters": filters,
            "limit": limit,
            "sort": ["created_time:desc"],
        }
        data = await _get_client().post(f"/v1/{_cid(customer_id)}/publishing/posts", body)
        return json.dumps(data, indent=2)
    except Exception as e:
        return _err(e)


@mcp.tool()
async def create_post(
    profile_ids: str,
    text: str,
    scheduled_send_time: str = "",
    customer_id: str = "",
) -> str:
    """Create a draft or scheduled post in Sprout Social.

    Args:
        profile_ids: Comma-separated Sprout profile IDs to publish to.
        text: Post content/body text.
        scheduled_send_time: When to publish (ISO 8601). Leave empty to save as draft.
        customer_id: Sprout customer ID. Defaults to SPROUT_CUSTOMER_ID env var.
    """
    try:
        body: dict = {
            "post_type": "OUTBOUND",
            "profile_ids": _split(profile_ids),
            "fields": {"text": text},
        }
        if scheduled_send_time:
            body["scheduled_send_time"] = scheduled_send_time

        data = await _get_client().post(f"/v1/{_cid(customer_id)}/publishing/posts", body)
        return json.dumps(data, indent=2)
    except Exception as e:
        return _err(e)


@mcp.tool()
async def get_publishing_post(
    post_id: str,
    customer_id: str = "",
) -> str:
    """Retrieve a specific publishing post by ID.

    Args:
        post_id: The publishing post ID to retrieve.
        customer_id: Sprout customer ID. Defaults to SPROUT_CUSTOMER_ID env var.
    """
    try:
        data = await _get_client().get(f"/v1/{_cid(customer_id)}/publishing/posts/{post_id}")
        return json.dumps(data, indent=2)
    except Exception as e:
        return _err(e)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
