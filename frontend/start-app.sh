#!/bin/bash

# Check if port 3001 is already in use
echo "Checking if port 3001 is already in use..."
if lsof -i :3001 > /dev/null; then
  echo "WARNING: Port 3001 is already in use by another process:"
  lsof -i :3001
  echo "You may need to kill this process or use a different port."
  
  read -p "Do you want to kill the process using port 3001? (y/n): " kill_process
  if [ "$kill_process" = "y" ]; then
    pid=$(lsof -ti :3001)
    if [ ! -z "$pid" ]; then
      echo "Killing process $pid..."
      kill -9 $pid
      echo "Process killed."
    fi
  fi
else
  echo "Port 3001 is available."
fi

# Set environment variables and start the app
echo "Starting React app with explicit host and port settings..."
HOST=0.0.0.0 PORT=3001 npm start
