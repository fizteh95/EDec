#!/usr/bin/env bash

set -euxo pipefail

# isort --check-only .
black --check .
mypy .
# its flake-simplify
flake8 .
