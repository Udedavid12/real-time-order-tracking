from app.cache import cache_delete, cache_get, cache_set, driver_latest_key


def test_cache_set_and_get():
    key = "test:key:1"
    value = {"hello": "world", "num": 42}

    cache_set(key, value, ttl_seconds=60)
    result = cache_get(key)

    assert result == value
    cache_delete(key)


def test_cache_get_missing_key():
    result = cache_get("test:missing:key")
    assert result is None


def test_cache_delete():
    key = "test:key:delete"
    cache_set(key, {"a": 1}, ttl_seconds=60)
    assert cache_get(key) is not None

    cache_delete(key)
    assert cache_get(key) is None


def test_driver_latest_key_format():
    key = driver_latest_key("abc-123")
    assert key == "driver:abc-123:latest"