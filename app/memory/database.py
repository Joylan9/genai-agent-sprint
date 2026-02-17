"""
app/memory/database.py

MongoDB connection layer for Enterprise Memory System.
Production-safe, singleton async client. No side-effects at import time.
"""

import os
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING
from dotenv import load_dotenv

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
            mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
            db_name = os.getenv("MONGODB_DB", "agent_memory")

            if not mongo_uri or not db_name:
                raise RuntimeError("MongoDB configuration missing in .env")

            # Create client; this does not block
            cls._client = AsyncIOMotorClient(mongo_uri)
            cls._db = cls._client[db_name]

        return cls._db

    # ✅ ADDED — REQUIRED FOR TRACE INSERTS
    @classmethod
    def get_database(cls):
        """
        Returns the database handle.
        Ensures connection is initialized.
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

        # ✅ ADDED — Trace collection indexes
        await db.traces.create_index([("request_id", ASCENDING)], unique=True)
        await db.traces.create_index([("session_id", ASCENDING)])
        await db.traces.create_index([("timestamp", ASCENDING)])
