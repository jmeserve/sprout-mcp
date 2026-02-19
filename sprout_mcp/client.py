import os
from typing import Any

import httpx

BASE_URL = "https://api.sproutsocial.com"


class SproutClient:
    def __init__(self) -> None:
        token = os.environ.get("SPROUT_API_TOKEN")
        if not token:
            raise RuntimeError("SPROUT_API_TOKEN environment variable is not set")
        self._headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    async def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        async with httpx.AsyncClient() as c:
            r = await c.get(
                f"{BASE_URL}{path}",
                headers=self._headers,
                params=params,
                timeout=30,
            )
            r.raise_for_status()
            return r.json()

    async def post(self, path: str, body: dict[str, Any] | None = None) -> Any:
        async with httpx.AsyncClient() as c:
            r = await c.post(
                f"{BASE_URL}{path}",
                headers=self._headers,
                json=body,
                timeout=30,
            )
            r.raise_for_status()
            return r.json()
