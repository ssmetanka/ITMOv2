#!/bin/sh
set -e
echo "==> Running automated test runner..."
python -m unittest discover -s tests -p "test_*.py"
echo "==> All checks PASSED!"

