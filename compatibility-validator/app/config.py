"""Validated runtime limits and filesystem locations."""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
REPO_DIR = BASE_DIR.parents[1]
DATA_PATH = Path(os.getenv("NVIDIA_DATA_PATH", str(REPO_DIR / "data/nvidia-interconnects.json")))
PROFILE_PATH = Path(os.getenv("DEVICE_PROFILES_PATH", str(BASE_DIR.parent / "data/device-profiles.json")))
STATIC_DIR = BASE_DIR / "static"


def positive_env(name: str, default: int, maximum: int) -> int:
    value = int(os.getenv(name, str(default)))
    if not 1 <= value <= maximum:
        raise ValueError(f"{name} must be between 1 and {maximum}")
    return value


MAX_DATA_BYTES = positive_env("MAX_DATA_BYTES", 2 * 1024 * 1024, 16 * 1024 * 1024)
MAX_PROFILE_BYTES = positive_env("MAX_PROFILE_BYTES", 512 * 1024, 8 * 1024 * 1024)
COMPAT_CACHE_MAX_ENTRIES = positive_env("COMPAT_CACHE_MAX_ENTRIES", 256, 4096)
MAX_REQUEST_BYTES = 16 * 1024
MAX_PROJECT_BYTES = 1024 * 1024
MAX_BREAKOUT_BYTES = 256 * 1024
