#!/bin/bash

# Build backend using Docker with local source code
echo "Building backend from local source..."

# Build the image
docker-compose build backend

echo "Build complete! Restarting backend container..."
docker-compose restart backend

echo "Done! Backend has been updated."
