# Semantic Search Examples

This directory contains sample scripts demonstrating various features and use cases of the Semantic Search Core Module.

## Prerequisites

1. **Install Dependencies**:
   ```bash
   pip install -r ../requirements.txt
   ```

2. **Set Environment Variables**:
   ```bash
   export OPENAI_API_KEY="your-openai-api-key"
   ```

3. **Optional Configuration**:
   ```bash
   cp ../.env.example ../.env
   # Edit .env file with your settings
   ```

## Available Examples

### 1. Basic Usage (`basic_usage.py`)

**Purpose**: Demonstrates fundamental CRUD operations and search functionality.

**Features**:
- Creating, reading, updating, and deleting products
- Different search methods (hybrid, semantic, keyword)
- Product retrieval and system statistics
- Error handling examples

**Run**:
```bash
python basic_usage.py
```

**What you'll see**:
- Step-by-step product creation
- Search comparisons between different methods
- Product updates and their effect on search results
- System statistics and product listing

### 2. Advanced Search (`advanced_search.py`)

**Purpose**: Showcases advanced search features and performance analysis.

**Features**:
- Custom weight configurations for hybrid search
- Search method comparison analysis
- Performance benchmarking
- Semantic understanding demonstration
- Comprehensive e-commerce dataset

**Run**:
```bash
python advanced_search.py
```

**What you'll see**:
- Weight configuration testing (keyword-heavy vs semantic-heavy)
- Performance metrics for different search types
- Semantic similarity showcase with synonyms
- Large dataset search performance

### 3. Batch Operations (`batch_operations.py`)

**Purpose**: Demonstrates efficient batch processing and large-scale operations.

**Features**:
- Batch vs individual operation performance comparison
- Large-scale dataset creation (200+ products)
- Data migration simulation
- Performance optimization techniques

**Run**:
```bash
python batch_operations.py
```

**What you'll see**:
- Performance comparison: batch vs individual operations
- Large-scale product creation and search
- Data export/import simulation
- Migration performance metrics

### 4. Interactive Demo (`interactive_demo.py`)

**Purpose**: Provides a hands-on, interactive command-line interface.

**Features**:
- Interactive menu system
- Real-time product management
- Live search testing
- Custom weight experimentation
- Search method comparison

**Run**:
```bash
python interactive_demo.py
```

**What you'll see**:
- Menu-driven interface
- Real-time search testing
- Product CRUD operations
- Weight configuration testing
- Help system with tips

## Example Output Samples

### Basic Usage Output
```
=== Semantic Search Core Module - Basic Usage ===

1. Initializing ProductService...
✅ ProductService initialized successfully

2. Creating sample products...
✅ Created: MacBook Pro 16-inch
✅ Created: iPhone 15 Pro
✅ Created: Sony WH-1000XM5
✅ Created: iPad Pro 12.9

📊 Total products created: 4

3. Testing different search methods...

🔍 Query: 'professional laptop for work'
  Hybrid: ['laptop-001', 'tablet-001']
  Semantic: ['laptop-001', 'tablet-001']
  Keyword: ['laptop-001']
```

### Advanced Search Output
```
=== Testing Different Search Weight Configurations ===

🔍 Query: 'laptop for programming and development'

Keyword Only (BM25:1.0, Vector:0.0):
  1. MacBook Pro 16-inch M2
  2. Dell XPS 13 Plus

Semantic Heavy (BM25:0.2, Vector:0.8):
  1. MacBook Pro 16-inch M2
  2. Dell XPS 13 Plus
  3. iPad Pro 12.9 M2
```

### Interactive Demo Menu
```
============================================================
🔍 SEMANTIC SEARCH INTERACTIVE DEMO
============================================================
1. Search products
2. Add new product
3. Update product
4. Delete product
5. List all products
6. Compare search methods
7. Test custom weights
8. System statistics
9. Help
0. Exit
============================================================
```

## Common Use Cases

### E-commerce Search Testing
```bash
# Test product search with different approaches
python advanced_search.py
```

### Performance Benchmarking
```bash
# Compare batch vs individual operations
python batch_operations.py
```

### Learning and Experimentation
```bash
# Interactive exploration of features
python interactive_demo.py
```

### Development and Debugging
```bash
# Basic functionality testing
python basic_usage.py
```

## Tips for Using Examples

1. **Start with Basic Usage**: Get familiar with core concepts
2. **Experiment with Interactive Demo**: Test different queries and weights
3. **Analyze Advanced Search**: Understand semantic vs keyword differences
4. **Test Performance**: Use batch operations for large datasets

## Customization

You can modify the examples to:

- **Add your own products**: Edit the sample data in any script
- **Test different queries**: Change search terms to match your use case
- **Adjust configurations**: Modify weights, top-k values, and other parameters
- **Add new features**: Extend scripts with additional functionality

## Troubleshooting

### Common Issues

1. **OpenAI API Key Not Set**:
   ```bash
   export OPENAI_API_KEY="your-key-here"
   ```

2. **Module Import Errors**:
   ```bash
   # Make sure you're in the examples directory
   cd examples
   python basic_usage.py
   ```

3. **Rate Limiting**:
   - The scripts include retry logic for API calls
   - Large datasets may take time due to embedding generation

4. **Memory Issues**:
   - For large datasets, consider reducing batch sizes
   - Clear data between runs if needed

## Next Steps

After exploring these examples:

1. **Integrate with FastAPI**: Use the core module in a REST API
2. **Add Custom Features**: Extend functionality for your specific needs
3. **Production Deployment**: Configure for production environments
4. **Performance Optimization**: Fine-tune for your data and use cases

## Support

For questions or issues:
- Check the main README.md for detailed API documentation
- Review the core module source code for implementation details
- Experiment with the interactive demo for hands-on learning 