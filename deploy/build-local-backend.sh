#!/bin/bash

# Build backend using Docker with local source code
echo "Building backend from local source..."

# Build the image
docker compose -f docker-compose.yml build backend

echo "Build complete! Restarting backend container..."
docker compose -f docker-compose.yml up -d --build --force-recreate backend

echo "Done! Backend has been updated."
