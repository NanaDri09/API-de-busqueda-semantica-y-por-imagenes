# Batch Insert Test Script for Semantic Search API (PowerShell)
# Make sure your API is running on http://localhost:8000

Write-Host "🚀 Testing Batch Product Insert API" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green

# Test the batch insert endpoint
Write-Host "📤 Sending batch insert request..." -ForegroundColor Yellow

$headers = @{
    "Content-Type"  = "application/json"
    "Authorization" = "Bearer test-api-key-1234567890"
}

$payload = Get-Content -Path "sample_batch_payload.json" -Raw

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/products/batch" -Method POST -Headers $headers -Body $payload
    Write-Host "✅ Batch insert successful!" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 10
}
catch {
    Write-Host "❌ Batch insert failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "🔍 Testing search functionality..." -ForegroundColor Yellow

$searchPayload = @{
    query                   = "laptop professional development"
    search_type             = "hybrid"
    top_k                   = 3
    include_product_details = $true
} | ConvertTo-Json

try {
    $searchResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/search/" -Method POST -Headers @{"Content-Type" = "application/json" } -Body $searchPayload
    Write-Host "✅ Search test successful!" -ForegroundColor Green
    $searchResponse | ConvertTo-Json -Depth 10
}
catch {
    Write-Host "❌ Search test failed: $($_.Exception.Message)" -ForegroundColor Red
} 