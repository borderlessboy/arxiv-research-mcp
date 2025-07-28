"""Caching service for storing and retrieving search results."""

import asyncio
import hashlib
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import aiofiles
from pydantic import BaseModel

from src.models.paper import Paper
from config.settings import settings

logger = logging.getLogger(__name__)


class CacheEntry(BaseModel):
    """Cache entry model."""
    query: str
    years_back: int
    papers: List[Paper]
    created_at: datetime
    expires_at: datetime


class CacheManager:
    """Service for caching search results."""
    
    def __init__(self):
        self.cache_dir = settings.CACHE_DIR
        self.ttl_hours = settings.CACHE_TTL_HOURS
        self.enabled = settings.CACHE_ENABLED
        
        if self.enabled:
            os.makedirs(self.cache_dir, exist_ok=True)
            
    async def get_cached_results(
        self, 
        query: str, 
        years_back: int
    ) -> Optional[List[Paper]]:
        """Get cached search results if available and valid."""
        
        if not self.enabled:
            return None
            
        cache_key = self._generate_cache_key(query, years_back)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        try:
            if os.path.exists(cache_file):
                async with aiofiles.open(cache_file, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    cache_entry_data = json.loads(content)
                    cache_entry = CacheEntry(**cache_entry_data)
                    
                    # Check if cache is still valid
                    if datetime.now() < cache_entry.expires_at:
                        logger.info(f"Cache hit for query: {query}")
                        return cache_entry.papers
                    else:
                        # Cache expired, delete file
                        os.remove(cache_file)
                        logger.info(f"Cache expired for query: {query}")
                        
        except Exception as e:
            logger.warning(f"Error reading cache for {cache_key}: {e}")
            # Delete corrupted cache file
            try:
                if os.path.exists(cache_file):
                    os.remove(cache_file)
            except Exception:
                pass
                
        return None
    
    async def cache_results(
        self, 
        query: str, 
        years_back: int, 
        papers: List[Paper]
    ) -> bool:
        """Cache search results."""
        
        if not self.enabled:
            return False
            
        cache_key = self._generate_cache_key(query, years_back)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        try:
            now = datetime.now()
            cache_entry = CacheEntry(
                query=query,
                years_back=years_back,
                papers=papers,
                created_at=now,
                expires_at=now + timedelta(hours=self.ttl_hours)
            )
            
            cache_data = cache_entry.model_dump(mode='json')
            
            async with aiofiles.open(cache_file, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(cache_data, indent=2, default=str))
            
            logger.info(f"Cached {len(papers)} papers for query: {query}")
            return True
            
        except Exception as e:
            logger.error(f"Error caching results for {cache_key}: {e}")
            return False
    
    def _generate_cache_key(self, query: str, years_back: int) -> str:
        """Generate a cache key for the query."""
        key_string = f"{query.lower().strip()}_{years_back}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    async def clear_cache(self) -> int:
        """Clear all cached results."""
        if not self.enabled:
            return 0
            
        cleared_count = 0
        try:
            if not os.path.exists(self.cache_dir):
                return 0
                
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(self.cache_dir, filename)
                    os.remove(file_path)
                    cleared_count += 1
            
            logger.info(f"Cleared {cleared_count} cache files")
            return cleared_count
            
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return cleared_count
    
    async def get_cache_stats(self) -> Dict:
        """Get cache statistics."""
        if not self.enabled:
            return {"enabled": False}
            
        try:
            if not os.path.exists(self.cache_dir):
                return {"enabled": True, "total_entries": 0, "total_size_mb": 0, "cache_dir": self.cache_dir, "ttl_hours": self.ttl_hours}
                
            cache_files = [f for f in os.listdir(self.cache_dir) if f.endswith('.json')]
            total_size = sum(
                os.path.getsize(os.path.join(self.cache_dir, f)) 
                for f in cache_files
            )
            
            return {
                "enabled": True,
                "total_entries": len(cache_files),
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "cache_dir": self.cache_dir,
                "ttl_hours": self.ttl_hours
            }
            
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {"enabled": True, "error": str(e)}