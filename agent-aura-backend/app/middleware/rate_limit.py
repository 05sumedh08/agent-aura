"""
Rate Limiting Middleware for Production
Implements per-user and global rate limits with Redis backend
"""
import os
import time
import logging
from typing import Callable, Optional
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import redis.asyncio as redis
from functools import wraps

logger = logging.getLogger(__name__)


class RateLimitConfig:
    """Rate limiting configuration"""
    
    def __init__(self):
        self.enabled = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
        self.per_minute = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
        self.per_hour = int(os.getenv("RATE_LIMIT_PER_HOUR", "1000"))
        self.per_day = int(os.getenv("RATE_LIMIT_PER_DAY", "10000"))
        
        # Redis configuration for distributed rate limiting
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.redis_password = os.getenv("REDIS_PASSWORD", None)
        self.use_redis = os.getenv("USE_REDIS_RATE_LIMIT", "false").lower() == "true"
        
        # Whitelist (IP addresses exempt from rate limiting)
        self.whitelist = os.getenv("RATE_LIMIT_WHITELIST", "").split(",")
        self.whitelist = [ip.strip() for ip in self.whitelist if ip.strip()]
        
        logger.info(f"Rate limiting: {'enabled' if self.enabled else 'disabled'}")
        logger.info(f"Limits: {self.per_minute}/min, {self.per_hour}/hour, {self.per_day}/day")
        if self.whitelist:
            logger.info(f"Whitelisted IPs: {len(self.whitelist)}")


rate_limit_config = RateLimitConfig()


def get_identifier(request: Request) -> str:
    """
    Get unique identifier for rate limiting
    Uses user ID if authenticated, otherwise IP address
    """
    # Try to get user ID from request state (set by auth middleware)
    user_id = getattr(request.state, "user_id", None)
    if user_id:
        return f"user:{user_id}"
    
    # Fall back to IP address
    return f"ip:{get_remote_address(request)}"


def is_whitelisted(request: Request) -> bool:
    """Check if request is from whitelisted IP"""
    client_ip = get_remote_address(request)
    return client_ip in rate_limit_config.whitelist


# Initialize limiter
limiter = Limiter(
    key_func=get_identifier,
    default_limits=[
        f"{rate_limit_config.per_minute}/minute",
        f"{rate_limit_config.per_hour}/hour",
        f"{rate_limit_config.per_day}/day"
    ],
    enabled=rate_limit_config.enabled,
    headers_enabled=True,
)


class RedisRateLimiter:
    """
    Redis-based distributed rate limiter
    Use for multi-instance deployments
    """
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.enabled = rate_limit_config.use_redis
        
    async def connect(self):
        """Connect to Redis"""
        if not self.enabled:
            return
        
        try:
            self.redis_client = redis.from_url(
                rate_limit_config.redis_url,
                password=rate_limit_config.redis_password,
                decode_responses=True,
            )
            await self.redis_client.ping()
            logger.info("Redis rate limiter connected")
        except Exception as e:
            logger.warning(f"Redis connection failed, falling back to in-memory: {e}")
            self.enabled = False
    
    async def close(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
    
    async def check_rate_limit(
        self,
        identifier: str,
        limit: int,
        window: int
    ) -> tuple[bool, int, int]:
        """
        Check if request is within rate limit
        Returns: (is_allowed, remaining, reset_time)
        """
        if not self.enabled or not self.redis_client:
            # Fall back to allowing request
            return True, limit, int(time.time() + window)
        
        try:
            key = f"rate_limit:{identifier}:{window}"
            current_time = int(time.time())
            window_start = current_time - window
            
            # Use Redis sorted set to track requests
            pipe = self.redis_client.pipeline()
            
            # Remove old requests
            pipe.zremrangebyscore(key, 0, window_start)
            
            # Count current requests
            pipe.zcard(key)
            
            # Add current request
            pipe.zadd(key, {str(current_time): current_time})
            
            # Set expiry
            pipe.expire(key, window)
            
            results = await pipe.execute()
            current_count = results[1]
            
            is_allowed = current_count < limit
            remaining = max(0, limit - current_count - 1)
            reset_time = current_time + window
            
            return is_allowed, remaining, reset_time
            
        except Exception as e:
            logger.error(f"Redis rate limit check failed: {e}")
            # Allow request on error
            return True, limit, int(time.time() + window)


# Global Redis rate limiter instance
redis_limiter = RedisRateLimiter()


async def rate_limit_middleware(request: Request, call_next):
    """
    Rate limiting middleware
    Applies rate limits before processing request
    """
    if not rate_limit_config.enabled:
        return await call_next(request)
    
    # Skip rate limiting for whitelisted IPs
    if is_whitelisted(request):
        return await call_next(request)
    
    # Skip rate limiting for health check endpoints
    if request.url.path in ["/health", "/api/health", "/api/v1/health"]:
        return await call_next(request)
    
    identifier = get_identifier(request)
    
    # Check rate limits
    checks = [
        (rate_limit_config.per_minute, 60, "minute"),
        (rate_limit_config.per_hour, 3600, "hour"),
        (rate_limit_config.per_day, 86400, "day"),
    ]
    
    for limit, window, name in checks:
        is_allowed, remaining, reset_time = await redis_limiter.check_rate_limit(
            identifier, limit, window
        )
        
        if not is_allowed:
            retry_after = reset_time - int(time.time())
            
            logger.warning(
                f"Rate limit exceeded for {identifier}: "
                f"{limit} requests per {name}"
            )
            
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "rate_limit_exceeded",
                    "message": f"Rate limit exceeded: {limit} requests per {name}",
                    "limit": limit,
                    "window": name,
                    "retry_after": retry_after
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": str(remaining),
                    "X-RateLimit-Reset": str(reset_time),
                }
            )
    
    # Process request
    response = await call_next(request)
    
    # Add rate limit headers
    response.headers["X-RateLimit-Limit-Minute"] = str(rate_limit_config.per_minute)
    response.headers["X-RateLimit-Limit-Hour"] = str(rate_limit_config.per_hour)
    
    return response


def custom_rate_limit(limit: str):
    """
    Custom rate limit decorator for specific endpoints
    
    Usage:
        @app.get("/api/expensive")
        @custom_rate_limit("10/minute")
        async def expensive_endpoint():
            pass
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get request from kwargs
            request = kwargs.get("request") or next(
                (arg for arg in args if isinstance(arg, Request)), None
            )
            
            if request and not is_whitelisted(request):
                # Parse limit string (e.g., "10/minute")
                parts = limit.split("/")
                if len(parts) == 2:
                    count = int(parts[0])
                    period = parts[1].lower()
                    
                    # Map period to seconds
                    period_map = {
                        "second": 1,
                        "minute": 60,
                        "hour": 3600,
                        "day": 86400,
                    }
                    
                    window = period_map.get(period, 60)
                    identifier = get_identifier(request)
                    
                    # Check rate limit
                    is_allowed, remaining, reset_time = await redis_limiter.check_rate_limit(
                        identifier, count, window
                    )
                    
                    if not is_allowed:
                        retry_after = reset_time - int(time.time())
                        raise HTTPException(
                            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                            detail=f"Rate limit exceeded: {limit}",
                            headers={"Retry-After": str(retry_after)}
                        )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


# Export commonly used items
__all__ = [
    "limiter",
    "redis_limiter",
    "rate_limit_middleware",
    "custom_rate_limit",
    "RateLimitExceeded",
    "rate_limit_config",
]
