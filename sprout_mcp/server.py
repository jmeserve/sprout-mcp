import json
import os

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


# ===== METADATA =====


@mcp.tool()
async def list_customers() -> str:
    """List all customers/accounts accessible with the current API token.

    Returns customer IDs and names needed for other API calls.
    """
    data = await _get_client().get("/v1/metadata/client")
    return json.dumps(data, indent=2)


@mcp.tool()
async def list_profiles(customer_id: str = "") -> str:
    """List all social profiles for a customer.

    Args:
        customer_id: Sprout customer ID. Defaults to SPROUT_CUSTOMER_ID env var.
    """
    data = await _get_client().get(f"/v1/{_cid(customer_id)}/metadata/customer")
    return json.dumps(data, indent=2)


@mcp.tool()
async def list_tags(customer_id: str = "") -> str:
    """List all message tags for a customer.

    Args:
        customer_id: Sprout customer ID. Defaults to SPROUT_CUSTOMER_ID env var.
    """
    data = await _get_client().get(f"/v1/{_cid(customer_id)}/metadata/customer/tags")
    return json.dumps(data, indent=2)


@mcp.tool()
async def list_groups(customer_id: str = "") -> str:
    """List all profile groups for a customer.

    Args:
        customer_id: Sprout customer ID. Defaults to SPROUT_CUSTOMER_ID env var.
    """
    data = await _get_client().get(f"/v1/{_cid(customer_id)}/metadata/customer/groups")
    return json.dumps(data, indent=2)


@mcp.tool()
async def list_users(customer_id: str = "") -> str:
    """List all active users for a customer.

    Args:
        customer_id: Sprout customer ID. Defaults to SPROUT_CUSTOMER_ID env var.
    """
    data = await _get_client().get(f"/v1/{_cid(customer_id)}/metadata/customer/users")
    return json.dumps(data, indent=2)


@mcp.tool()
async def list_teams(customer_id: str = "") -> str:
    """List all teams for a customer.

    Args:
        customer_id: Sprout customer ID. Defaults to SPROUT_CUSTOMER_ID env var.
    """
    data = await _get_client().get(f"/v1/{_cid(customer_id)}/metadata/customer/teams")
    return json.dumps(data, indent=2)


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


@mcp.tool()
async def get_post_analytics(
    profile_ids: str,
    start_time: str,
    end_time: str,
    metrics: str = "impressions,engagements,clicks",
    timezone: str = "UTC",
    limit: int = 50,
    customer_id: str = "",
) -> str:
    """Get analytics metrics for individual posts.

    Args:
        profile_ids: Comma-separated Sprout profile IDs.
        start_time: Start of period (ISO 8601).
        end_time: End of period (ISO 8601).
        metrics: Comma-separated metric names. Common options:
                 impressions, engagements, clicks, reactions, comments, shares, video_views.
        timezone: Timezone for the report. Default: UTC.
        limit: Number of posts to return (default 50, max 100).
        customer_id: Sprout customer ID. Defaults to SPROUT_CUSTOMER_ID env var.
    """
    ids = ",".join(_split(profile_ids))
    body = {
        "filters": [
            f"customer_profile_id.eq({ids})",
            f"created_time.in({start_time}..{end_time})",
        ],
        "metrics": _split(metrics),
        "timezone": timezone,
        "limit": limit,
    }
    data = await _get_client().post(f"/v1/{_cid(customer_id)}/analytics/posts", body)
    return json.dumps(data, indent=2)


# ===== MESSAGES =====


@mcp.tool()
async def get_messages(
    profile_ids: str,
    start_time: str,
    end_time: str,
    post_type: str = "",
    tag_ids: str = "",
    limit: int = 50,
    page_cursor: str = "",
    customer_id: str = "",
) -> str:
    """Retrieve messages with metadata and filtering.

    Args:
        profile_ids: Comma-separated Sprout profile IDs.
        start_time: Start datetime (ISO 8601, e.g. '2024-01-01T00:00:00').
        end_time: End datetime (ISO 8601).
        post_type: Filter by direction: 'INBOUND', 'OUTBOUND', or '' for all.
        tag_ids: Comma-separated tag IDs to filter by (optional).
        limit: Number of messages to return (default 50).
        page_cursor: Pagination cursor from a previous response (optional).
        customer_id: Sprout customer ID. Defaults to SPROUT_CUSTOMER_ID env var.
    """
    ids = ",".join(_split(profile_ids))
    filters = [
        f"customer_profile_id.eq({ids})",
        f"created_time.in({start_time}..{end_time})",
    ]
    if post_type:
        filters.append(f"post_type.eq({post_type})")
    if tag_ids:
        tag_list = ",".join(_split(tag_ids))
        filters.append(f"tag_id.eq({tag_list})")

    body: dict = {"filters": filters, "limit": limit}
    if page_cursor:
        body["page_cursor"] = page_cursor

    data = await _get_client().post(f"/v1/{_cid(customer_id)}/messages", body)
    return json.dumps(data, indent=2)


# ===== PUBLISHING =====


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
    body: dict = {
        "post_type": "OUTBOUND",
        "profile_ids": _split(profile_ids),
        "fields": {"text": text},
    }
    if scheduled_send_time:
        body["scheduled_send_time"] = scheduled_send_time

    data = await _get_client().post(f"/v1/{_cid(customer_id)}/publishing/posts", body)
    return json.dumps(data, indent=2)


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
    data = await _get_client().get(f"/v1/{_cid(customer_id)}/publishing/posts/{post_id}")
    return json.dumps(data, indent=2)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
