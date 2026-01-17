from pathlib import Path
import logging

from app.settings import settings

logger = logging.getLogger(__name__)


def get_cache_dir() -> Path:
    """Get or create cache directory."""
    cache_path = Path(settings.cache_dir)
    cache_path.mkdir(parents=True, exist_ok=True)
    return cache_path


def get_cache_path(series_id: str) -> Path:
    """Get cache path for a specific series."""
    cache_dir = get_cache_dir()
    series_cache = cache_dir / series_id
    series_cache.mkdir(parents=True, exist_ok=True)
    return series_cache


def ensure_cache_dir(path: Path) -> None:
    """Ensure cache directory exists."""
    path.mkdir(parents=True, exist_ok=True)


def clear_cache(series_id: str) -> None:
    """Clear cache for a specific series."""
    cache_path = get_cache_path(series_id)
    import shutil
    try:
        shutil.rmtree(cache_path)
        logger.info(f"Cleared cache for {series_id}")
    except Exception as e:
        logger.error(f"Error clearing cache for {series_id}: {e}")
