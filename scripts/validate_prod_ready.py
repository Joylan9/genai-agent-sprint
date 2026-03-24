'''
import os
import sys
import asyncio
import json
from motor.motor_asyncio import AsyncIOMotorClient
import redis.asyncio as redis
import ollama

def check_env():
    print("🔍 Checking Environment Variables...")
    critical_vars = ["API_KEY", "SERPAPI_KEY", "HF_TOKEN", "MONGO_URI", "OLLAMA_HOST"]
    missing = [v for v in critical_vars if not os.getenv(v) or os.getenv(v).startswith("__")]
    if missing:
        print(f"❌ Missing critical variables: {missing}")
        return False
    print("✅ Environment variables look good.")
    return True

async def check_mongodb():
    print("\n🔍 Checking MongoDB Connectivity...")
    uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    try:
        client = AsyncIOMotorClient(uri, serverSelectionTimeoutMS=2000)
        await client.admin.command('ping')
        print("✅ MongoDB is reachable.")
        return True
    except Exception as e:
        print(f"❌ MongoDB connectivity failed: {e}")
        return False

async def check_redis():
    print("\n🔍 Checking Redis Connectivity...")
    url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    try:
        r = redis.from_url(url, socket_timeout=2)
        await r.ping()
        print("✅ Redis is reachable.")
        return True
    except Exception as e:
        print(f"❌ Redis connectivity failed: {e}")
        return False

def check_ollama():
    print("\n🔍 Checking Ollama Connectivity...")
    try:
        models = ollama.list()
        print(f"✅ Ollama is reachable. Found {len(models.get('models', []))} models.")
        return True
    except Exception as e:
        print(f"❌ Ollama connectivity failed: {e}")
        return False

def check_data():
    print("\n🔍 Checking Data Integrity...")
    paths = ["data/vector_store.pkl", "data/docs"]
    missing = [p for p in paths if not os.path.exists(p)]
    if missing:
        print(f"❌ Missing data paths: {missing}")
        return False
    
    docs = os.listdir("data/docs")
    if not docs:
        print("❌ data/docs is empty.")
        return False
    
    print(f"✅ Data integrity verified. Found {len(docs)} documents.")
    return True

async def main():
    print("🚀 GENAI AGENT ENGINE - PRODUCTION READINESS VALIDATOR\n" + "="*50)
    
    results = [
        check_env(),
        await check_mongodb(),
        await check_redis(),
        check_ollama(),
        check_data()
    ]
    
    print("\n" + "="*50)
    if all(results):
        print("🎉 ALL SYSTEMS READY FOR PRODUCTION! 🎉")
    else:
        print("⚠️  PRODUCTION READINESS CHECKS FAILED. Please address the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
'''

import asyncio
import os
import sys

import ollama
from motor.motor_asyncio import AsyncIOMotorClient
import redis.asyncio as redis


def check_env() -> bool:
    print("Checking environment variables...")
    required = ["JWT_SECRET", "MONGODB_URI", "MONGODB_DB", "OLLAMA_HOST", "CELERY_BROKER_URL"]
    missing = [name for name in required if not os.getenv(name) or os.getenv(name, "").startswith("__")]
    if missing:
        print(f"Missing required variables: {missing}")
        return False

    if not os.getenv("SERPAPI_KEY"):
        print("Optional variable missing: SERPAPI_KEY. Web search will be disabled.")
    return True


async def check_mongodb() -> bool:
    print("\nChecking MongoDB connectivity...")
    uri = os.getenv("MONGODB_URI", os.getenv("MONGO_URI", "mongodb://localhost:27017"))
    try:
        client = AsyncIOMotorClient(uri, serverSelectionTimeoutMS=2000)
        await client.admin.command("ping")
        print("MongoDB is reachable.")
        return True
    except Exception as exc:
        print(f"MongoDB connectivity failed: {exc}")
        return False


async def check_redis() -> bool:
    print("\nChecking Redis connectivity...")
    url = os.getenv("REDIS_URL", os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"))
    try:
        client = redis.from_url(url, socket_timeout=2)
        await client.ping()
        print("Redis is reachable.")
        return True
    except Exception as exc:
        print(f"Redis connectivity failed: {exc}")
        return False


def check_ollama() -> bool:
    print("\nChecking Ollama connectivity...")
    try:
        models = ollama.list()
        print(f"Ollama is reachable. Found {len(models.get('models', []))} models.")
        return True
    except Exception as exc:
        print(f"Ollama connectivity failed: {exc}")
        return False


def check_eval_suites() -> bool:
    print("\nChecking eval suite registry...")
    eval_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "eval")
    suites = [name for name in os.listdir(eval_dir) if name.endswith(".json")] if os.path.isdir(eval_dir) else []
    if not suites:
        print("No eval suites found under eval/.")
        return False
    print(f"Found {len(suites)} eval suite file(s): {', '.join(sorted(suites))}")
    return True


async def main():
    print("TraceAI production readiness validator\n" + "=" * 48)
    results = [
        check_env(),
        await check_mongodb(),
        await check_redis(),
        check_ollama(),
        check_eval_suites(),
    ]

    print("\n" + "=" * 48)
    if all(results):
        print("All blocking readiness checks passed.")
        return

    print("One or more blocking readiness checks failed.")
    sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
