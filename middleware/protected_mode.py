from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

class ProtectedModeMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, config):
        super().__init__(app)
        self.config = config

    async def dispatch(self, request: Request, call_next):
        # 检查保护模式状态
        if self.config.protected_mode:
            path = request.url.path
            
            # 放行白名单端点
            if path in self.config.allowed_endpoints:
                return await call_next(request)
                
            # 拦截其他请求
            raise HTTPException(
                status_code=403,
                detail="保护模式已启用，仅允许搜索API访问"
            )
            
        return await call_next(request)