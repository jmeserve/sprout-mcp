# sprout-mcp

An MCP (Model Context Protocol) server that wraps the [Sprout Social Public API](https://developers.sproutsocial.com/), letting Claude and other MCP clients interact with your Sprout Social account directly.

## Tools

| Tool | Description |
|---|---|
| `list_customers` | List all customers/accounts accessible with your API token |
| `list_profiles` | List all social profiles for a customer |
| `list_tags` | List all message tags |
| `list_groups` | List all profile groups |
| `list_users` | List all active users |
| `list_teams` | List all teams |
| `get_profile_analytics` | Get aggregated analytics by profile (impressions, engagements, etc.) |
| `get_post_analytics` | Get analytics for individual posts |
| `get_messages` | Retrieve inbound inbox messages (Smart Inbox) — for outbound post counts use `get_post_analytics` |
| `create_post` | Create a draft or scheduled post |
| `get_publishing_post` | Retrieve a specific publishing post by ID |

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
