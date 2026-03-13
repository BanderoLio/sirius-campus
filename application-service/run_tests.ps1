# Run backend tests (requires Python 3.11+ with pytest, pytest-asyncio)
# Install: pip install -r requirements-dev.txt
# Then: .\run_tests.ps1   or   python -m pytest tests/ -v

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$py = $null
if (Get-Command python -ErrorAction SilentlyContinue) { $py = "python" }
elseif (Get-Command py -ErrorAction SilentlyContinue) { $py = "py -3" }
elseif (Get-Command python3 -ErrorAction SilentlyContinue) { $py = "python3" }

if (-not $py) {
    Write-Error "Python not found. Install Python 3.11+ and add to PATH, or run: pip install -r requirements-dev.txt && pytest tests/ -v"
    exit 1
}

& $py -m pytest tests/ -v --tb=short 2>&1
exit $LASTEXITCODE
