# sprout-mcp

An MCP (Model Context Protocol) server that wraps the [Sprout Social Public API](https://developers.sproutsocial.com/), letting Claude and other MCP clients interact with your Sprout Social account directly.

## Tools

### Metadata
| Tool | Description |
|---|---|
| `list_customers` | List all customers/accounts accessible with your API token |
| `list_profiles` | List all social profiles for a customer |
| `list_tags` | List all message tags |
| `list_groups` | List all profile groups |
| `list_users` | List all active users |
| `list_teams` | List all teams |

### Analytics
| Tool | Description |
|---|---|
| `get_profile_analytics` | Get aggregated metrics by profile (impressions, engagements, follower growth, etc.) |
| `get_post_analytics` | Get metrics for individual published posts — also use this for post counts |

### Listening
| Tool | Description |
|---|---|
| `list_listening_topics` | List all Listening topics and their IDs |
| `get_listening_messages` | Fetch messages from a Listening topic, filterable by network (Reddit, Twitter, etc.) |

### Smart Inbox
| Tool | Description |
|---|---|
| `get_messages` | Retrieve inbound inbox messages (mentions, DMs, comments) |

### Publishing
| Tool | Description |
|---|---|
| `list_publishing_posts` | List published, scheduled, or draft posts |
| `create_post` | Create a draft or scheduled post |
| `get_publishing_post` | Retrieve a specific post by ID |

> **Note:** All tools return structured JSON error details on failure (HTTP status, endpoint, and API error body) instead of raw exceptions.

## Setup

### Prerequisites
- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- A Sprout Social account with API access

### Install

```bash
git clone https://github.com/jmeserve/sprout-mcp.git
cd sprout-mcp
uv sync
```

### Configure

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

```env
SPROUT_API_TOKEN=your_api_token_here
SPROUT_CUSTOMER_ID=your_customer_id_here
```

- **SPROUT_API_TOKEN** — Generate at Sprout Social → Settings → API → OAuth tokens
- **SPROUT_CUSTOMER_ID** — Found in your Sprout Social account URL or via the `list_customers` tool

### Add to Claude Code

Add to your `~/.claude.json` MCP servers config:

```json
{
  "mcpServers": {
    "sprout-social": {
      "command": "uv",
      "args": ["--directory", "/path/to/sprout-mcp", "run", "sprout-mcp"],
      "env": {
        "SPROUT_API_TOKEN": "your_api_token_here",
        "SPROUT_CUSTOMER_ID": "your_customer_id_here"
      }
    }
  }
}
```

### Add to Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "sprout-social": {
      "command": "uv",
      "args": ["--directory", "/path/to/sprout-mcp", "run", "sprout-mcp"],
      "env": {
        "SPROUT_API_TOKEN": "your_api_token_here",
        "SPROUT_CUSTOMER_ID": "your_customer_id_here"
      }
    }
  }
}
```

## Development

```bash
uv sync
uv run sprout-mcp       # run the server
uv run mcp dev sprout_mcp/server.py  # run with MCP inspector
```
