#!/bin/bash
echo "Stopping Class Music Dashboard..."
pkill -f "python app.py"
pkill -f "vite"
echo "›All processes stopped!"
