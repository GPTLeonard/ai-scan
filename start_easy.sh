#!/bin/bash

# Kill anything running on 7071 (Backend) or 5173 (Frontend)
lsof -ti:7071 | xargs kill -9 2>/dev/null
lsof -ti:5173 | xargs kill -9 2>/dev/null

echo "Installing Flask..."
ls -la api/
./venv/bin/pip install flask flask-cors -q

echo "Starting Backend (Python Native)..."
./venv/bin/python run_local_server.py &
BACKEND_PID=$!

echo "Backend running on PID $BACKEND_PID"
sleep 2

echo "Starting Frontend..."
cd client
npm run dev

# When frontend stops, kill backend
kill $BACKEND_PID
