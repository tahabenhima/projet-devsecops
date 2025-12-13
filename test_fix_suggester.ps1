# Script PowerShell pour tester le microservice FixSuggester

Write-Host "=== Test du microservice FixSuggester ===" -ForegroundColor Green

# 1. Vérifier l'état de santé du service
Write-Host "`n1. Test du endpoint /health" -ForegroundColor Cyan
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8002/health" -Method Get
    Write-Host "✓ Service is healthy: $($health.status)" -ForegroundColor Green
    $health | ConvertTo-Json
} catch {
    Write-Host "✗ Service health check failed: $_" -ForegroundColor Red
}

# 2. Tester la génération de correctifs
Write-Host "`n2. Test du endpoint /fix" -ForegroundColor Cyan
$testPayload = Get-Content "test_fix_suggester.json" -Raw
try {
    $fixes = Invoke-RestMethod -Uri "http://localhost:8002/fix" `
        -Method Post `
        -ContentType "application/json" `
        -Body $testPayload
    
    Write-Host "✓ Fixes generated successfully" -ForegroundColor Green
    Write-Host "Number of fixes: $($fixes.fixes.Count)" -ForegroundColor Yellow
    
    foreach ($fix in $fixes.fixes) {
        Write-Host "`n--- Fix $($fix.id) ---" -ForegroundColor Magenta
        Write-Host "Type: $($fix.vulnerability_type)"
        Write-Host "Severity: $($fix.severity)"
        Write-Host "Auto-applicable: $($fix.auto_applicable)"
        Write-Host "Description: $($fix.description)"
    }
} catch {
    Write-Host "✗ Fix generation failed: $_" -ForegroundColor Red
}

# 3. Récupérer toutes les suggestions
Write-Host "`n3. Test du endpoint /fixes" -ForegroundColor Cyan
try {
    $allFixes = Invoke-RestMethod -Uri "http://localhost:8002/fixes" -Method Get
    Write-Host "✓ Retrieved $($allFixes.Count) fix suggestions" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed to retrieve fixes: $_" -ForegroundColor Red
}

# 4. Récupérer une suggestion spécifique
Write-Host "`n4. Test du endpoint /fixes/{id}" -ForegroundColor Cyan
try {
    $specificFix = Invoke-RestMethod -Uri "http://localhost:8002/fixes/1" -Method Get
    Write-Host "✓ Retrieved fix suggestion #1" -ForegroundColor Green
    Write-Host "Diff preview:" -ForegroundColor Yellow
    Write-Host $specificFix.diff
} catch {
    Write-Host "✗ Failed to retrieve specific fix: $_" -ForegroundColor Red
}

Write-Host "`n=== Tests terminés ===" -ForegroundColor Green
