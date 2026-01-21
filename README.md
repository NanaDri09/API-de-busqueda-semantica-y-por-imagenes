# Semantic Search Core Module

A modular semantic search system combining BM25 keyword matching and vector embeddings for e-commerce product search.

## Features

- **Hybrid Search**: Combines BM25 (keyword) and vector (semantic) search for optimal results
- **CRUD Operations**: Create, read, update, and delete products with automatic index management
- **Configurable Weights**: Adjust the balance between keyword and semantic search
- **Persistent Storage**: FAISS vector store with automatic saving/loading
- **Batch Operations**: Efficient bulk product creation and indexing
- **Multiple Search Types**: Hybrid, semantic-only, and keyword-only search modes
- **Image Search**: Types of searches based on visual approaches

## Installation

1. Install dependencies:
```bash
pip install -r requirements_act.txt
```

2. Set up environment variables:
```bash
export OPENAI_API_KEY="your-openai-api-key"
```

## Quick Start

```python
from core import ProductService

# Initialize the service
service = ProductService()

# Create products
service.create_product(
    id="1",
    title="Wireless Bluetooth Headphones",
    description="High-quality wireless headphones with noise cancellation"
)

service.create_product(
    id="2", 
    title="Gaming Laptop",
    description="High-performance laptop for gaming and productivity"
)

# Search products
results = service.search_products("wireless audio", search_type="hybrid")
print(f"Found products: {results}")

# Get product details
product = service.get_product_by_id("1")
print(f"Product: {product.title}")
```

## Configuration

Environment variables can be set to customize behavior:

```bash
# OpenAI Configuration
export OPENAI_API_KEY="your-key"
export OPENAI_MODEL="text-embedding-3-small"

# Search Configuration
export DEFAULT_TOP_K="10"
export DEFAULT_BM25_WEIGHT="0.4"
export DEFAULT_VECTOR_WEIGHT="0.6"

# Storage Configuration
export VECTOR_STORE_PATH="data/vector_store"
```

## API Reference

### ProductService

Main interface for all product operations.

#### Methods

**create_product(id: str, title: str, description: str) -> Product**
- Creates a new product and adds it to both search indexes
- Validates input and generates embeddings
- Automatically saves indexes to disk

**update_product(id: str, title: str = None, description: str = None) -> Product**
- Updates an existing product
- Re-generates embeddings for changed fields
- Rebuilds indexes for optimal performance

**delete_product(id: str) -> bool**
- Removes product from both indexes
- Returns True if successful

**search_products(query: str, search_type: str = "hybrid", **kwargs) -> List[str]**
- Searches products using specified method
- `search_type`: "hybrid", "semantic", or "keyword"
- `bm25_weight`, `vector_weight`: Custom weights for hybrid search
- `top_k`: Number of results to return
- Returns list of product IDs ranked by relevance

**get_product_by_id(id: str) -> Optional[Product]**
- Retrieves a product by its ID
- Returns None if not found

**list_all_products() -> List[Product]**
- Returns all products in the system

**batch_create_products(products_data: List[Dict]) -> List[Product]**
- Creates multiple products efficiently
- Better performance for large datasets

### Search Types

1. **Hybrid Search** (default)
   - Combines BM25 and vector search
   - Configurable weights (default: 40% BM25, 60% vector)
   - Best overall performance

2. **Semantic Search**
   - Uses only vector embeddings
   - Great for finding conceptually similar products
   - Handles synonyms and related terms

3. **Keyword Search**
   - Uses only BM25 algorithm
   - Excellent for exact phrase matching
   - Fast and deterministic
4. **Image Search** (added)
   - Applies semantic search logic to an image provided in the query.
5. **Caption Search** (added)
   - Performs the same process as image search, but instead of transforming the image to an embedding, it is described.
   - The search runs with the obtained description and compares it to the embeddings of product image descriptions stored.
6. **Image-Description Search** (added)
   - This mode uses the product descriptions to run the search from the description of the query image.
   - Follows the same process as caption search.
7. **Image-and-Description Hybrid** (added)
   - A weighted hybrid search that combines the three previous modalities (image, caption, and descriptions).

## Examples

### Basic CRUD Operations

```python
from core import ProductService

service = ProductService()

# Create
product = service.create_product(
    id="laptop-001",
    title="MacBook Pro 16-inch",
    description="Professional laptop with M2 chip and 32GB RAM"
)

# Read
found_product = service.get_product_by_id("laptop-001")
all_products = service.list_all_products()

# Update
updated_product = service.update_product(
    id="laptop-001",
    description="Professional laptop with M2 chip, 32GB RAM, and 1TB SSD"
)

# Delete
service.delete_product("laptop-001")
```

### Advanced Search

```python
# Hybrid search with custom weights
results = service.search_products(
    query="professional laptop",
    search_type="hybrid",
    bm25_weight=0.3,
    vector_weight=0.7,
    top_k=5
)

# Semantic search for conceptual similarity
semantic_results = service.search_products(
    query="portable computer for work",
    search_type="semantic"
)

# Keyword search for exact matches
keyword_results = service.search_products(
    query="MacBook Pro",
    search_type="keyword"
)
```

### Batch Operations

```python
# Create multiple products efficiently
products_data = [
    {
        "id": "phone-001",
        "title": "iPhone 15 Pro",
        "description": "Latest iPhone with advanced camera system"
    },
    {
        "id": "phone-002", 
        "title": "Samsung Galaxy S24",
        "description": "Android flagship with AI features"
    }
]

products = service.batch_create_products(products_data)
```

### System Statistics

```python
# Get system information
stats = service.get_search_statistics()
print(f"Total products: {stats['total_products']}")
print(f"Vector index size: {stats['vector_index_size']}")
print(f"BM25 index size: {stats['bm25_index_size']}")
```

## Architecture

The system is organized into several layers:

- **Models**: Data structures and validation (`Product`, `ProductDocument`)
- **Repositories**: Data access layer (`VectorRepository`, `BM25Repository`)
- **Services**: Business logic (`ProductService`, `SearchService`, `EmbeddingService`)
- **Config**: Configuration management (`Settings`)

## Performance Considerations

- **Batch Operations**: Use `batch_create_products()` for large datasets
- **Index Persistence**: Vector indexes are automatically saved/loaded
- **Memory Usage**: FAISS indexes are memory-efficient
- **API Limits**: Embedding generation respects OpenAI rate limits

## Error Handling

The system includes comprehensive error handling:

- Input validation using Pydantic
- OpenAI API retry logic with exponential backoff
- Graceful handling of missing products
- Detailed logging for debugging

## Future Enhancements

This core module is designed to be easily extended with:

- Additional vector databases (Pinecone, Weaviate)
- Advanced search filters
- Real-time updates via webhooks
- User-history-based recommendation system

## License

MIT License - see LICENSE file for details. 
