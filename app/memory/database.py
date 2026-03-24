"""
app/memory/database.py

MongoDB connection layer for Enterprise Memory System.
Production-safe, singleton async client. No side-effects at import time.
"""

from typing import Optional

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING
from app.config.runtime import mongodb_db, mongodb_uri

# Load .env once (safe to call on import)
load_dotenv()


class MongoDB:
    """Singleton async Mongo client + DB accessor."""

    _client: Optional[AsyncIOMotorClient] = None
    _db = None

    @classmethod
    def connect(cls):
        """
        Create (or return existing) AsyncIOMotorClient and DB handle.
        This is synchronous so it is safe to call from non-async startup handlers.
        """
        if cls._client is None:
            mongo_uri = mongodb_uri()
            db_name = mongodb_db()

            if not mongo_uri or not db_name:
                raise RuntimeError("MongoDB configuration missing in .env")

            # Create client; this does not block.
            cls._client = AsyncIOMotorClient(mongo_uri)
            cls._db = cls._client[db_name]

        return cls._db

    @classmethod
    def get_database(cls):
        """
        Return the database handle and initialize the connection if needed.
        """
        return cls.connect()

    @classmethod
    async def initialize_indexes(cls):
        """
        Ensure indexes exist. Call this from an async startup hook.
        """
        db = cls.connect()

        # Conversations collection indexes
        await db.conversations.create_index([("session_id", ASCENDING)])
        await db.conversations.create_index([("created_at", ASCENDING)])

        # Long-term memory collection indexes
        await db.long_term_memory.create_index([("session_id", ASCENDING)])
        await db.long_term_memory.create_index([("created_at", ASCENDING)])

        # Trace collection indexes
        await db.traces.create_index([("request_id", ASCENDING)], unique=True)
        await db.traces.create_index([("session_id", ASCENDING)])
        await db.traces.create_index([("timestamp", ASCENDING)])

        # Agent directory indexes
        await db.agents.create_index([("name_lower", ASCENDING)], unique=True)
        await db.agents.create_index([("created_at", ASCENDING)])

        # Users collection indexes (Phase 3: Auth)
        await db.users.create_index([("email", ASCENDING)], unique=True)
        await db.users.create_index([("created_at", ASCENDING)])

        # Password reset flow
        await db.password_resets.create_index([("email", ASCENDING)], unique=True)
        await db.password_resets.create_index([("expires_at", ASCENDING)], expireAfterSeconds=0)

        # Run events collection indexes (Phase 2: SSE)
        await db.run_events.create_index([("run_id", ASCENDING)])
        await db.run_events.create_index([("timestamp", ASCENDING)])

        # Response cache (L2)
        await db.response_cache.create_index([("expires_at", ASCENDING)], expireAfterSeconds=0)
        await db.response_cache.create_index([("_id", ASCENDING)], unique=True)

        # Agent version history
        await db.agent_versions.create_index([("agent_id", ASCENDING), ("version", ASCENDING)], unique=True)
        await db.agent_versions.create_index([("agent_id", ASCENDING), ("created_at", ASCENDING)])

        # Evaluation results
        await db.eval_results.create_index([("suite_id", ASCENDING)], unique=True)
        await db.eval_results.create_index([("timestamp", ASCENDING)])
