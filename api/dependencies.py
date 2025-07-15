import time
import uuid
from typing import Optional
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from core.services.product_service import ProductService
import logging

logger = logging.getLogger(__name__)

# Global ProductService instance
_product_service: Optional[ProductService] = None
_service_start_time = time.time()

# Security scheme for optional API key authentication
security = HTTPBearer(auto_error=False)


def get_product_service() -> ProductService:
    """
    Dependency to get the ProductService instance.
    
    Returns:
        ProductService: Singleton instance of the product service
    """
    global _product_service
    
    if _product_service is None:
        try:
            logger.info("Initializing ProductService...")
            _product_service = ProductService()
            logger.info("ProductService initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize ProductService: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service initialization failed. Please check configuration."
            )
    
    return _product_service


def get_service_uptime() -> float:
    """
    Get service uptime in seconds.
    
    Returns:
        float: Service uptime in seconds
    """
    return time.time() - _service_start_time


def generate_request_id() -> str:
    """
    Generate a unique request ID for tracking.
    
    Returns:
        str: Unique request identifier
    """
    return f"req_{uuid.uuid4().hex[:12]}"


def get_request_id(request: Request) -> str:
    """
    Get or generate request ID for the current request.
    
    Args:
        request: FastAPI request object
        
    Returns:
        str: Request identifier
    """
    # Check if request ID is already set
    if hasattr(request.state, 'request_id'):
        return request.state.request_id
    
    # Generate new request ID
    request_id = generate_request_id()
    request.state.request_id = request_id
    return request_id


async def verify_api_key(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[str]:
    """
    Optional API key verification.
    
    Args:
        credentials: HTTP authorization credentials
        
    Returns:
        str: API key if valid, None if no authentication required
        
    Raises:
        HTTPException: If API key is invalid
    """
    # If no credentials provided and API key is not required, allow access
    if credentials is None:
        return None
    
    # If credentials provided, validate them
    api_key = credentials.credentials
    
    # TODO: Implement actual API key validation
    # For now, accept any non-empty key
    if not api_key or len(api_key) < 10:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return api_key


def check_service_health() -> dict:
    """
    Check the health of the service and its dependencies.
    
    Returns:
        dict: Health status of various components
    """
    health_status = {
        "product_service": "unknown",
        "openai": "unknown",
        "vector_store": "unknown",
        "bm25_index": "unknown"
    }
    
    try:
        # Check if ProductService is initialized
        service = get_product_service()
        health_status["product_service"] = "ready"
        
        # Check if we can get statistics (this tests core functionality)
        stats = service.get_search_statistics()
        
        # Check vector store
        if stats.get("vector_index_size", 0) >= 0:
            health_status["vector_store"] = "ready"
        
        # Check BM25 index
        if stats.get("bm25_index_size", 0) >= 0:
            health_status["bm25_index"] = "ready"
        
        # Check OpenAI connection (basic check)
        try:
            from core.config.settings import settings
            if settings.validate_openai_key():
                health_status["openai"] = "connected"
            else:
                health_status["openai"] = "not_configured"
        except Exception:
            health_status["openai"] = "error"
            
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        health_status["product_service"] = "error"
    
    return health_status


class RateLimitError(Exception):
    """Custom exception for rate limiting."""
    pass


# Simple in-memory rate limiter (for production, use Redis)
_rate_limit_store = {}


def check_rate_limit(client_ip: str, limit: int = 100, window: int = 3600) -> bool:
    """
    Simple rate limiting check.
    
    Args:
        client_ip: Client IP address
        limit: Maximum requests per window
        window: Time window in seconds
        
    Returns:
        bool: True if request is allowed, False if rate limited
    """
    current_time = time.time()
    
    # Clean old entries
    for ip in list(_rate_limit_store.keys()):
        _rate_limit_store[ip] = [
            timestamp for timestamp in _rate_limit_store[ip]
            if current_time - timestamp < window
        ]
        if not _rate_limit_store[ip]:
            del _rate_limit_store[ip]
    
    # Check current IP
    if client_ip not in _rate_limit_store:
        _rate_limit_store[client_ip] = []
    
    # Count requests in current window
    recent_requests = len(_rate_limit_store[client_ip])
    
    if recent_requests >= limit:
        return False
    
    # Add current request
    _rate_limit_store[client_ip].append(current_time)
    return True


def get_client_ip(request: Request) -> str:
    """
    Get client IP address from request.
    
    Args:
        request: FastAPI request object
        
    Returns:
        str: Client IP address
    """
    # Check for forwarded headers (when behind proxy)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    forwarded = request.headers.get("X-Forwarded")
    if forwarded:
        return forwarded.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fallback to direct client IP
    return request.client.host if request.client else "unknown" 