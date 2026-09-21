"""ASGI entry point; API, catalog loading and rules live in separate modules."""

from .api import app

__all__ = ["app"]
