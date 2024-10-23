#!/usr/bin/env python3
"""
Web cache and URL access tracker using Redis,
with caching and access counting.
"""

import requests
import redis
from typing import Callable
from functools import wraps


class Cache:
    """Cache class to interact with Redis."""

    def __init__(self):
        """Initialize the connection to the Redis server."""
        self._redis = redis.Redis()

    def count_and_cache(self, ttl: int = 10) -> Callable:
        """
        Decorator to count URL accesses and cache the
        results with an expiration time.
        Args:
            ttl (int): Time to live for cache in seconds (default: 10).
        Returns:
            Callable: The decorated function.
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(url: str) -> str:
                cache_key = f"count:{url}"
                self._redis.incr(cache_key)
                # Check if URL is in cache
                cached_page = self._redis.get(url)
                if cached_page:
                    return cached_page.decode('utf-8')
                # Fetch the page if not cached
                page_content = func(url)
                # Cache the content with expiration
                self._redis.setex(url, ttl, page_content)
                return page_content
            return wrapper
        return decorator

    @count_and_cache(ttl=10)
    def get_page(self, url: str) -> str:
        """
        Get the HTML content of a URL, track access count,
        and cache with expiration.
        Args:
            url (str): The URL to fetch.
        Returns:
            str: The HTML content of the URL.
        """
        response = requests.get(url)
        return response.text

    def get_count(self, url: str) -> int:
        """
        Get the access count of a URL.
        Args:
            url (str): The URL to get the count for.
        Returns:
            int: The access count.
        """
        count = self._redis.get(f"count:{url}")
        return int(count) if count else 0


if __name__ == "__main__":
    cache = Cache()

    url = ("http://slowwly.robertomurray.co.uk"
           "/delay/1000/url/http://www.google.com")
    print("Fetching URL...")
    print(cache.get_page(url))  # Fetch and cache the URL
    print(f"URL accessed {cache.get_count(url)} times")  # Print access count