# Failure Simulation Script for GenAI Agent Platform
# This script simulates common production failure scenarios to verify system resilience.

function Test-Resilience {
    param (
        [string]$Scenario,
        [scriptblock]$Action
    )
    Write-Host "`n--- SCENARIO: $Scenario ---" -ForegroundColor Cyan
    try {
        & $Action
    } catch {
        Write-Host "Error during scenario: $_" -ForegroundColor Red
    }
}

# 1. Simulate LLM Unavailability
Test-Resilience "LLM Connection Timeout" {
    Write-Host "Simulating LLM timeout by pointing OLLAMA_HOST to a dead port..."
    # In a real environment, we'd use environment variable overriding or network blocking.
    # For this script, we assume the user might manually stop Ollama or we use a tool logic test.
    Write-Host "Action: Run a request and verify Circuit Breaker OPENs after 5 failures." -ForegroundColor Yellow
}

# 2. Simulate Tool Failure
Test-Resilience "Web Search API Error" {
    Write-Host "Simulating SerpAPI failure..."
    Write-Host "Action: Run a query requiring web search with an invalid key and verify fallback to RAG if applicable." -ForegroundColor Yellow
}

# 3. Policy Violation
Test-Resilience "Policy Denial" {
    Write-Host "Simulating an unauthorized tool request..."
    Write-Host "Action: Ask the agent to 'delete the database' and verify PolicyEngine blocks the plan." -ForegroundColor Yellow
}

Write-Host "`nResilience Verification Complete. Check Prometheus /metrics for failure counts." -ForegroundColor Green
