#!/bin/bash
set -e
cd "$(dirname "$0")/.."
echo "Starting backend at http://localhost:8000"
python3 backend/main.py
