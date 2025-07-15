import time
import logging
from typing import Callable
from fastapi import Request, Response, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from .dependencies import check_rate_limit, get_client_ip, generate_request_id

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request/response logging."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate request ID if not present
        if not hasattr(request.state, 'request_id'):
            request.state.request_id = generate_request_id()
        
        request_id = request.state.request_id
        start_time = time.time()
        
        # Get client info
        client_ip = get_client_ip(request)
        user_agent = request.headers.get("user-agent", "unknown")
        
        # Log request
        logger.info(
            f"Request started: {request.method} {request.url.path} "
            f"[IP: {client_ip}] [Request: {request_id}]"
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Add headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)
            
            # Log response
            logger.info(
                f"Request completed: {request.method} {request.url.path} "
                f"[Status: {response.status_code}] [Time: {process_time:.3f}s] "
                f"[IP: {client_ip}] [Request: {request_id}]"
            )
            
            return response
            
        except Exception as e:
            # Calculate processing time for errors too
            process_time = time.time() - start_time
            
            # Log error
            logger.error(
                f"Request failed: {request.method} {request.url.path} "
                f"[Error: {str(e)}] [Time: {process_time:.3f}s] "
                f"[IP: {client_ip}] [Request: {request_id}]"
            )
            
            # Re-raise the exception
            raise


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting."""
    
    def __init__(self, app, calls_per_hour: int = 1000):
        super().__init__(app)
        self.calls_per_hour = calls_per_hour
        self.window_seconds = 3600  # 1 hour
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/api/v1/search/health"]:
            return await call_next(request)
        
        # Get client IP
        client_ip = get_client_ip(request)
        
        # Check rate limit
        if not check_rate_limit(client_ip, self.calls_per_hour, self.window_seconds):
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later.",
                headers={
                    "Retry-After": str(self.window_seconds),
                    "X-RateLimit-Limit": str(self.calls_per_hour),
                    "X-RateLimit-Window": str(self.window_seconds)
                }
            )
        
        return await call_next(request)


def setup_cors(app):
    """Setup CORS middleware."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",  # React dev server
            "http://localhost:8080",  # Vue dev server
            "http://localhost:8000",  # FastAPI docs
            "https://yourdomain.com",  # Production domain
        ],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID", "X-Process-Time"]
    )


def setup_middleware(app):
    """Setup all middleware for the application."""
    
    # Rate limiting (apply first, before logging)
    app.add_middleware(RateLimitMiddleware, calls_per_hour=1000)
    
    # Request logging
    app.add_middleware(RequestLoggingMiddleware)
    
    # CORS (apply last)
    setup_cors(app)
    
    logger.info("Middleware setup completed") 