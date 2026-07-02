"""
app/cache/response_cache.py

Smart response caching layer with TTL support.
Enterprise-safe version with L1 + L2 caching.
"""

import hashlib
import time
from datetime import datetime, timedelta
from typing import Optional

from pymongo import ASCENDING


class ResponseCache:
    def __init__(self, db, ttl_seconds: int = 3600):
        self.collection = db.response_cache
        self.ttl_seconds = ttl_seconds

        # ----------------------------
        # L1 In-Memory Cache (Process Level)
        # ----------------------------
        self._memory_cache = {}
        self._memory_expiry = {}

    async def initialize(self):
        # TTL index (L2 auto-expiry)
        await self.collection.create_index(
            [("expires_at", ASCENDING)],
            expireAfterSeconds=0,
        )

        # Ensure _id uniqueness (usually implicit but explicit for safety)
        await self.collection.create_index(
            [("_id", ASCENDING)],
            unique=True
        )

    # ============================================================
    # Utilities
    # ============================================================

    @staticmethod
    def _normalize(text: str) -> str:
        return " ".join(text.strip().lower().split())

    def _goal_key(self, goal: str) -> str:
        normalized_goal = self._normalize(goal)
        return hashlib.sha256(normalized_goal.encode("utf-8")).hexdigest()

    def _plan_key(self, goal: str, plan_text: str) -> str:
        normalized_goal = self._normalize(goal)
        combined = normalized_goal + plan_text
        return hashlib.sha256(combined.encode("utf-8")).hexdigest()

    # ============================================================
    # L1 Memory Layer
    # ============================================================

    def _l1_get(self, key: str) -> Optional[str]:
        if key in self._memory_cache:
            if time.time() < self._memory_expiry.get(key, 0):
                return self._memory_cache[key]
            else:
                # Expired in memory
                self._memory_cache.pop(key, None)
                self._memory_expiry.pop(key, None)
        return None

    def _l1_set(self, key: str, value: str):
        self._memory_cache[key] = value
        self._memory_expiry[key] = time.time() + self.ttl_seconds

    # ============================================================
    # Public API
    # ============================================================

    async def get(self, goal: str, plan_text: str) -> Optional[str]:
        goal_key = self._goal_key(goal)
        plan_key = self._plan_key(goal, plan_text)

        # ----------------------------
        # 1️⃣ L1 Memory Check
        # ----------------------------
        result = self._l1_get(goal_key)
        if result:
            return result

        result = self._l1_get(plan_key)
        if result:
            return result

        # ----------------------------
        # 2️⃣ L2 Mongo Check
        # ----------------------------
        doc = await self.collection.find_one({"_id": goal_key})
        if doc:
            if "expires_at" in doc and doc["expires_at"] < datetime.utcnow():
                return None

            response = doc.get("response")
            if response:
                self._l1_set(goal_key, response)
                return response

        doc = await self.collection.find_one({"_id": plan_key})
        if doc:
            if "expires_at" in doc and doc["expires_at"] < datetime.utcnow():
                return None

            response = doc.get("response")
            if response:
                self._l1_set(plan_key, response)
                return response

        return None

    async def set(self, goal: str, plan_text: str, response: str):
        now = datetime.utcnow()

        goal_key = self._goal_key(goal)
        plan_key = self._plan_key(goal, plan_text)

        # ----------------------------
        # L1 Store
        # ----------------------------
        self._l1_set(goal_key, response)
        self._l1_set(plan_key, response)

        # ----------------------------
        # L2 Store
        # ----------------------------
        await self.collection.update_one(
            {"_id": goal_key},
            {
                "$set": {
                    "goal": self._normalize(goal),
                    "response": response,
                    "created_at": now,
                    "expires_at": now + timedelta(seconds=self.ttl_seconds),
                }
            },
            upsert=True,
        )

        await self.collection.update_one(
            {"_id": plan_key},
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
