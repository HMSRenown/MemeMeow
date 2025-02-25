import time
from collections import defaultdict
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from threading import Lock
import redis
from redis.exceptions import RedisError

class RateLimiter:
    def __init__(self):
        self.counts = defaultdict(list)
        self.lock = Lock()

    def check(self, key: str, max_requests: int, window: int) -> bool:
        """返回是否允许请求"""
        with self.lock:
            now = time.time()
            # 清理过期记录
            self.counts[key] = [
                t for t in self.counts[key] 
                if (now - t) <= window
            ]
            # 检查计数
            if len(self.counts[key]) >= max_requests:
                return False
            self.counts[key].append(now)
            return True
        
class RedisRateLimiter:
    def __init__(self, host='localhost', port=6379):
        self.redis = redis.Redis(host=host, port=port)
        self.script = """
        local key = KEYS[1]
        local window = ARGV[1]
        local max = ARGV[2]
        
        local current = redis.call('GET', key) or 0
        if tonumber(current) >= tonumber(max) then
            return 0
        else
            redis.call('INCR', key)
            redis.call('EXPIRE', key, window)
            return 1
        end
        """

    def check(self, key: str, max_requests: int, window: int) -> bool:
        try:
            result = self.redis.eval(
                self.script, 
                1,  # keys数量
                key, 
                window, 
                max_requests
            )
            return bool(result)
        except RedisError:
            return True  # 降级处理

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, config):
        super().__init__(app)
        self.config = config
        if self.config.rate_limit.storage == 'redis':
            self.ratelimiter = RedisRateLimiter()
        else:
            self.ratelimiter = RateLimiter()

    async def dispatch(self, request: Request, call_next):
        if not self.config.rate_limit.enabled:
            return await call_next(request)

        # 获取客户端标识
        client_ip = request.client.host
        
        # 检查速率限制
        if not self.ratelimiter.check(
            key=client_ip,
            max_requests=self.config.rate_limit.requests,
            window=self.config.rate_limit.window
        ):
            raise HTTPException(
                status_code=429,
                detail=f"请求过于频繁，每分钟限流 {self.config.rate_limit.requests} 次",
                headers={"Retry-After": str(self.config.rate_limit.window)}
            )
            
        return await call_next(request)