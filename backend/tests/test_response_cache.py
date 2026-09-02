import hashlib

from app.cache.response_cache import CACHE_NAMESPACE, ResponseCache


def test_response_cache_keys_are_namespaced(fake_db):
    cache = ResponseCache(fake_db)
    old_key = hashlib.sha256("define aiml".encode("utf-8")).hexdigest()

    assert cache._goal_key("define AIML") != old_key
    assert cache._goal_key("define AIML") == hashlib.sha256(
        f"{CACHE_NAMESPACE}:goal:define aiml".encode("utf-8")
    ).hexdigest()
