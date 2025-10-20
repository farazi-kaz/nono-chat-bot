#!/bin/bash
# Cleanup script

echo "Stopping Docker Compose services..."
docker-compose down

echo "Removing volumes (optional - comment out to keep data)..."
# docker-compose down -v

echo "Cleanup complete!"
