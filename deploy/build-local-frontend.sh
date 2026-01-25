#!/bin/bash

set -euo pipefail

# Build frontend using Docker with local source code
echo "Building frontend from local source..."

# Create a temporary Dockerfile
cat > /tmp/Dockerfile.build-frontend-local << 'EOF'
FROM node:18

ARG YARN_REGISTRY=https://registry.npmjs.org

WORKDIR /root/frontend

# Copy package files first for better caching
COPY package.json yarn.lock* ./
RUN yarn install --registry=$YARN_REGISTRY --network-timeout 600000

# Copy source code
COPY . .

# Build
RUN NODE_OPTIONS="--max-old-space-size=4096" yarn build

CMD ["sh", "-c", "cp -r /root/frontend/dist/* /output/"]
EOF

# Build the image
if [ "${NO_CACHE:-false}" = "true" ]; then
  docker build --no-cache -t genuine-oj/frontend-builder-local -f /tmp/Dockerfile.build-frontend-local --build-arg YARN_REGISTRY=${YARN_REGISTRY:-https://registry.npmjs.org} ../frontend-naive
else
  docker build -t genuine-oj/frontend-builder-local -f /tmp/Dockerfile.build-frontend-local --build-arg YARN_REGISTRY=${YARN_REGISTRY:-https://registry.npmjs.org} ../frontend-naive
fi

# Run the build and copy output
echo "Copying build output to ./data/frontend/..."
mkdir -p ./data/frontend ./data/frontend-tmp
rm -rf ./data/frontend-tmp/*
docker run --rm -v "$(pwd)/data/frontend-tmp:/output" genuine-oj/frontend-builder-local

if [ ! -f ./data/frontend-tmp/index.html ]; then
  echo "ERROR: frontend build output missing index.html. Not updating ./data/frontend." >&2
  exit 1
fi

rm -rf ./data/frontend/*
cp -r ./data/frontend-tmp/* ./data/frontend/

echo "Build complete! Restarting frontend container..."
docker compose -f docker-compose.yml up -d --force-recreate frontend

echo "Done! Frontend has been updated."
