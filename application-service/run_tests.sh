#!/usr/bin/env bash
# Run backend tests (requires Python 3.11+ with pytest, pytest-asyncio)
# Install: pip install -r requirements-dev.txt
set -e
cd "$(dirname "$0")"
python -m pytest tests/ -v --tb=short
