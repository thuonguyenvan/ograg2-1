#!/bin/bash
# Helper script to run with correct Python interpreter

PYTHON="/home/thuongnv/.pyenv/versions/3.11.9/bin/python"

# Show usage
if [ $# -eq 0 ]; then
    echo "Usage: ./python.sh <script.py> [args...]"
    echo "Example: ./python.sh build_duoclieu_hypergraph.py"
    echo "Example: ./python.sh test_duoclieu.py"
    echo "Example: ./python.sh query_duoclieu.py \"Câu hỏi?\""
    exit 1
fi

# Run with correct Python
exec $PYTHON "$@"
