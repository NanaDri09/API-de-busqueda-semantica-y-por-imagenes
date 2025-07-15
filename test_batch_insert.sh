#!/bin/bash

# Batch Insert Test Script for Semantic Search API
# Make sure your API is running on http://localhost:8000

echo "🚀 Testing Batch Product Insert API"
echo "======================================"

# Test the batch insert endpoint
echo "📤 Sending batch insert request..."

curl -X POST "http://localhost:8000/api/v1/products/batch" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test-api-key-1234567890" \
  -d @sample_batch_payload.json \
  --verbose

echo ""
echo "✅ Batch insert request completed!"
echo ""

# Test a search to verify the products were indexed
echo "🔍 Testing search functionality..."

curl -X POST "http://localhost:8000/api/v1/search/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "laptop professional development",
    "search_type": "hybrid",
    "top_k": 3,
    "include_product_details": true
  }' \
  --silent | python -m json.tool

echo ""
echo "✅ Search test completed!" 