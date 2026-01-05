#!/bin/bash
echo "Starting Backend..."
cd api
source venv/bin/activate
# Try to find func, otherwise warn
if command -v func &> /dev/null; then
    func start &
    BACKEND_PID=$!
else
    echo "Azure Functions Core Tools 'func' not found."
    echo "Please install it or run 'python test_backend.py' to test logic only."
    echo "Attempting to run without func (imperfect emulation)..."
    # This is hard to emulate perfectly without func, so we just warn.
fi

echo "Starting Frontend..."
cd ../client
npm run dev

# Cleanup
kill $BACKEND_PID
