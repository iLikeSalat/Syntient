#!/bin/bash

# Run all tests for the Syntient AI Assistant Platform
echo "Running tests for Syntient AI Assistant Platform..."
python -m unittest tests.py

# Check exit code
if [ $? -eq 0 ]; then
    echo "All tests passed successfully!"
    exit 0
else
    echo "Some tests failed. Please check the output above for details."
    exit 1
fi
