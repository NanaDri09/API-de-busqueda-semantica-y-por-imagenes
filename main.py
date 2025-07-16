import logging
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
from datetime import datetime, timezone

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent))

from api.routers import products_router, search_router
from api.middleware import setup_middleware
from api.dependencies import get_product_service
from api.models.responses import ErrorResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting up Semantic Search API...")
    
    try:
        # Initialize the ProductService to ensure everything is working
        service = get_product_service()
        stats = service.get_search_statistics()
        logger.info(f"Service initialized successfully. Stats: {stats}")
        
        yield
        
    except Exception as e:
        logger.error(f"Failed to initialize service: {e}")
        raise
    
    finally:
        # Shutdown
        logger.info("Shutting down Semantic Search API...")


# Create FastAPI app with lifespan
app = FastAPI(
    title="Semantic Search API",
    description="""
    A RESTful API for e-commerce product semantic search using hybrid BM25 + vector embeddings.
    
    ## Features
    
    * **Hybrid Search**: Combines BM25 keyword matching with vector similarity
    * **Multiple Search Types**: Semantic, keyword, and hybrid search modes
    * **Full CRUD Operations**: Create, read, update, delete products
    * **Batch Operations**: Efficient bulk operations for large datasets
    * **Real-time Indexing**: Automatic search index updates
    * **Comprehensive Statistics**: Search system monitoring and metrics
    
    ## Search Types
    
    * **Hybrid**: Combines BM25 and vector search with configurable weights
    * **Semantic**: Uses OpenAI embeddings for meaning-based search
    * **Keyword**: Traditional BM25 for exact term matching
    
    ## Authentication
    
    Some endpoints require API key authentication. Pass your API key in the Authorization header:
    ```
    Authorization: Bearer your-api-key-here
    ```
    """,
    version="1.0.0",
    contact={
        "name": "API Support",
        "email": "support@example.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    lifespan=lifespan
)

# Setup middleware
setup_middleware(app)

# Include routers
app.include_router(products_router, prefix="/api/v1")
app.include_router(search_router, prefix="/api/v1")


# Global exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors."""
    logger.warning(f"Validation error: {exc}")
    
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            error="ValidationError",
            message="Request validation failed",
            details={
                "errors": exc.errors(),
                "body": exc.body
            },
            #timestamp=datetime.now(timezone.utc),
            request_id=getattr(request.state, 'request_id', None)
        ).model_dump(mode='json')
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=f"HTTP{exc.status_code}",
            message=exc.detail,
            #timestamp=datetime.now(timezone.utc),
            request_id=getattr(request.state, 'request_id', None)
        ).model_dump(mode='json')
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="InternalServerError",
            message="An unexpected error occurred",
            #timestamp=datetime.now(timezone.utc),
            request_id=getattr(request.state, 'request_id', None)
        ).model_dump(mode='json')
    )


# Root endpoint
@app.get("/", 
    summary="API Information",
    description="Get basic information about the API")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Semantic Search API",
        "version": "1.0.0",
        "description": "E-commerce product semantic search API",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "health_check": "/api/v1/search/health",
        "endpoints": {
            "products": "/api/v1/products",
            "search": "/api/v1/search",
            "stats": "/api/v1/search/stats"
        }
    }


# Health check endpoint at root level
@app.get("/health",
    summary="Health Check",
    description="Basic health check endpoint")
async def health():
    """Basic health check."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "semantic-search-api"
    }


if __name__ == "__main__":
    import uvicorn
    import argparse

    parser = argparse.ArgumentParser(description="Run the Semantic Search API server.")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind the server to.")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind the server to.")
    args = parser.parse_args()
    
    # Run the server
    uvicorn.run(
        "main:app",
        host=args.host,
        port=args.port,
        reload=True,
        log_level="info",
        reload_excludes=[
            "*.log",
            "*.faiss", 
            "*.pkl",
            "*.json",
            "data/*",
            "logs/*", 
            "__pycache__/*",
            "*.pyc",
            ".git/*",
            "*.tmp",
            "*.temp",
            "vector_store/*",
            "bm25_store/*"
        ]
    ) 