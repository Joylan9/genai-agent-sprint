"""
app/cache/response_cache.py

Smart response caching layer with TTL support.
Enterprise-safe version.
"""

import hashlib
from datetime import datetime, timedelta
from typing import Optional

from pymongo import ASCENDING


class ResponseCache:
    def __init__(self, db, ttl_seconds: int = 3600):
        self.collection = db.response_cache
        self.ttl_seconds = ttl_seconds

    async def initialize(self):
        # TTL index
        await self.collection.create_index(
            [("expires_at", ASCENDING)],
            expireAfterSeconds=0,
        )

        # Ensure _id uniqueness (safety, usually implicit)
        await self.collection.create_index(
            [("_id", ASCENDING)],
            unique=True
        )

    @staticmethod
    def _normalize(text: str) -> str:
        return " ".join(text.strip().lower().split())

    def _build_key(self, goal: str, plan_text: str) -> str:
        normalized_goal = self._normalize(goal)
        combined = normalized_goal + plan_text
        return hashlib.sha256(combined.encode("utf-8")).hexdigest()

    async def get(self, goal: str, plan_text: str) -> Optional[str]:
        key = self._build_key(goal, plan_text)

        doc = await self.collection.find_one({"_id": key})

        if not doc:
            return None

        # Safety check (TTL should handle expiration automatically)
        if "expires_at" in doc and doc["expires_at"] < datetime.utcnow():
            return None

        return doc.get("response")

    async def set(self, goal: str, plan_text: str, response: str):
        key = self._build_key(goal, plan_text)
        now = datetime.utcnow()

        await self.collection.update_one(
            {"_id": key},
            {
                "$set": {
                    "goal": self._normalize(goal),
                    "plan": plan_text,
                    "response": response,
                    "created_at": now,
                    "expires_at": now + timedelta(seconds=self.ttl_seconds),
                }
            },
            upsert=True,
        )
