ù#!/bin/bash

# Build backend using Docker with local source code
echo "Building backend from local source..."

# Build the image
docker-compose build backend

echo "Build complete! Restarting backend container..."
docker-compose restart backend

echo "Done! Backend has been updated."
ù*cascade08"(5ac4ce5149d5df03259d8e59c714ddf813d0c19c2*file:///root/deploy/build-local-backend.sh:file:///root/deploy