# Semantic Search API

A comprehensive RESTful API for e-commerce product semantic search using hybrid BM25 + vector embeddings.

## Features

- **Hybrid Search**: Combines BM25 keyword matching with OpenAI vector embeddings
- **Multiple Search Types**: Semantic, keyword, and hybrid search modes
- **Full CRUD Operations**: Create, read, update, delete products
- **Batch Operations**: Efficient bulk operations for large datasets
- **Real-time Indexing**: Automatic search index updates
- **Comprehensive Statistics**: Search system monitoring and metrics
- **Production Ready**: Docker support, health checks, rate limiting, logging

## Quick Start

### Prerequisites

- Python 3.11+
- OpenAI API key
- Required Python packages (see requirements)

### Installation

1. **Clone and setup**:
```bash
git clone <repository-url>
cd semantic-search-api
```

2. **Install dependencies**:
```bash
pip install -r requirements-api.txt
```

3. **Environment setup**:
```bash
cp .env.example .env
# Edit .env with your OpenAI API key
```

4. **Run the server**:
```bash
python main.py
# or
uvicorn main:app --reload
```

5. **Access the API**:
- API Documentation: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc
- Health check: http://localhost:8000/health

## API Endpoints

### Products

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/products/` | Create a new product | Yes |
| GET | `/api/v1/products/{id}` | Get product by ID | No |
| PUT | `/api/v1/products/{id}` | Update product | Yes |
| DELETE | `/api/v1/products/{id}` | Delete product | Yes |
| GET | `/api/v1/products/` | List products (paginated) | No |
| POST | `/api/v1/products/batch` | Batch create products | Yes |
| DELETE | `/api/v1/products/batch` | Batch delete products | Yes |

### Search

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/search/` | General search | No |
| POST | `/api/v1/search/hybrid` | Hybrid search | No |
| POST | `/api/v1/search/semantic` | Semantic search | No |
| POST | `/api/v1/search/keyword` | Keyword search | No |
| GET | `/api/v1/search/stats` | Search statistics | No |
| GET | `/api/v1/search/health` | Health check | No |
| POST | `/api/v1/search/rebuild` | Rebuild indexes | Yes |
| DELETE | `/api/v1/search/clear` | Clear all data | Yes |

## Usage Examples

### Create a Product

```bash
curl -X POST "http://localhost:8000/api/v1/products/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-key" \
  -d '{
    "id": "laptop-001",
    "title": "MacBook Pro 16-inch",
    "description": "Professional laptop with M2 chip, 32GB RAM, perfect for developers"
  }'
```

### Search Products

```bash
# Hybrid search
curl -X POST "http://localhost:8000/api/v1/search/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "professional laptop for development",
    "search_type": "hybrid",
    "top_k": 5,
    "bm25_weight": 0.4,
    "vector_weight": 0.6,
    "include_product_details": true
  }'

# Semantic search
curl -X POST "http://localhost:8000/api/v1/search/semantic" \
  -H "Content-Type: application/json" \
  -d "query=mobile phone communication&top_k=3&include_product_details=true"
```

### Batch Operations

```bash
# Batch create products
curl -X POST "http://localhost:8000/api/v1/products/batch" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-key" \
  -d '{
    "products": [
      {
        "id": "phone-001",
        "title": "iPhone 15 Pro",
        "description": "Latest iPhone with advanced camera"
      },
      {
        "id": "tablet-001",
        "title": "iPad Pro",
        "description": "Professional tablet with M2 chip"
      }
    ]
  }'
```

## Search Types

### Hybrid Search (Recommended)
Combines BM25 keyword matching with vector similarity for the best of both worlds:
- **BM25**: Exact keyword matching, good for specific terms
- **Vector**: Semantic similarity, good for meaning-based search
- **Configurable weights**: Adjust the balance between approaches

### Semantic Search
Uses OpenAI embeddings for meaning-based search:
- Great for finding products by concept or description
- Handles synonyms and related terms
- Best for exploratory search

### Keyword Search
Traditional BM25 search for exact term matching:
- Fast and efficient
- Good for specific product names or features
- Best for known-item search

## Authentication

Some endpoints require API key authentication. Include your API key in the Authorization header:

```bash
Authorization: Bearer your-api-key-here
```

## Error Handling

The API returns structured error responses:

```json
{
  "error": "ValidationError",
  "message": "Product ID cannot be empty",
  "details": {
    "field": "id",
    "input_value": ""
  },
  "timestamp": "2024-01-15T10:30:00Z",
  "request_id": "req_123456789"
}
```

## Response Models

### Product Response
```json
{
  "id": "laptop-001",
  "title": "MacBook Pro 16-inch",
  "description": "Professional laptop with M2 chip",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### Search Response
```json
{
  "results": [
    {
      "product_id": "laptop-001",
      "score": 0.95,
      "product": {
        "id": "laptop-001",
        "title": "MacBook Pro 16-inch",
        "description": "Professional laptop with M2 chip"
      }
    }
  ],
  "query": "professional laptop",
  "search_type": "hybrid",
  "total_results": 1,
  "execution_time_ms": 45.2,
  "weights": {"bm25": 0.4, "vector": 0.6}
}
```

## Configuration

Environment variables:

```env
# Required
OPENAI_API_KEY=your-openai-api-key

# Optional (with defaults)
VECTOR_STORE_PATH=./data/vector_store
BM25_STORE_PATH=./data/bm25_store
BM25_WEIGHT=0.4
VECTOR_WEIGHT=0.6
DEFAULT_TOP_K=10
LOG_LEVEL=INFO
```

## Docker Deployment

### Build and Run
```bash
docker build -t semantic-search-api .
docker run -p 8000:8000 -e OPENAI_API_KEY=your-key semantic-search-api
```

### Docker Compose
```bash
docker-compose up -d
```

## Monitoring and Health

### Health Checks
- Basic: `GET /health`
- Detailed: `GET /api/v1/search/health`

### Statistics
```bash
curl http://localhost:8000/api/v1/search/stats
```

Returns:
```json
{
  "total_products": 1250,
  "vector_index_size": 1250,
  "bm25_index_size": 1250,
  "vector_dimension": 1536,
  "default_weights": {"bm25": 0.4, "vector": 0.6},
  "default_top_k": 10
}
```

## Testing

Run the comprehensive test suite:

```bash
# Make sure API is running first
python main.py

# In another terminal
python test_api.py
```

The test suite covers:
- All CRUD operations
- All search types
- Batch operations
- Error handling
- Health checks
- Admin operations

## Performance Considerations

### Indexing
- Products are automatically indexed when created/updated
- Use batch operations for large datasets
- Rebuild indexes periodically for optimal performance

### Search Performance
- Hybrid search: ~50-200ms depending on dataset size
- Semantic search: ~30-100ms (depends on OpenAI API)
- Keyword search: ~10-50ms (fastest)

### Rate Limiting
- Default: 1000 requests per hour per IP
- Configurable in middleware
- Use Redis for production rate limiting

## Production Deployment

### Requirements
- Python 3.11+
- OpenAI API key
- Persistent storage for indexes
- Load balancer (for multiple instances)
- Monitoring (Prometheus/Grafana)

### Scaling
- Stateless design allows horizontal scaling
- Share vector store across instances
- Use Redis for rate limiting and caching
- Monitor OpenAI API usage and costs

### Security
- API key authentication for write operations
- Rate limiting enabled
- Input validation and sanitization
- CORS configured for web frontends

## API Client Libraries

### Python
```python
import httpx

class SemanticSearchClient:
    def __init__(self, base_url: str, api_key: str = None):
        self.base_url = base_url
        self.api_key = api_key
        self.client = httpx.Client()
    
    def search(self, query: str, search_type: str = "hybrid", top_k: int = 10):
        response = self.client.post(
            f"{self.base_url}/api/v1/search/",
            json={
                "query": query,
                "search_type": search_type,
                "top_k": top_k,
                "include_product_details": True
            }
        )
        return response.json()
    
    def create_product(self, id: str, title: str, description: str):
        response = self.client.post(
            f"{self.base_url}/api/v1/products/",
            json={"id": id, "title": title, "description": description},
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        return response.json()

# Usage
client = SemanticSearchClient("http://localhost:8000", "your-api-key")
results = client.search("professional laptop")
```

### JavaScript
```javascript
class SemanticSearchClient {
    constructor(baseUrl, apiKey = null) {
        this.baseUrl = baseUrl;
        this.apiKey = apiKey;
    }
    
    async search(query, searchType = 'hybrid', topK = 10) {
        const response = await fetch(`${this.baseUrl}/api/v1/search/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query,
                search_type: searchType,
                top_k: topK,
                include_product_details: true
            })
        });
        return response.json();
    }
    
    async createProduct(id, title, description) {
        const response = await fetch(`${this.baseUrl}/api/v1/products/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${this.apiKey}`
            },
            body: JSON.stringify({ id, title, description })
        });
        return response.json();
    }
}

// Usage
const client = new SemanticSearchClient('http://localhost:8000', 'your-api-key');
const results = await client.search('professional laptop');
```

## Support

For issues, questions, or contributions:
- Check the API documentation at `/docs`
- Run the test suite to verify functionality
- Check logs for detailed error information
- Review the health check endpoints for system status

## License

MIT License - see LICENSE file for details. 