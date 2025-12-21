#!/bin/bash

# Build frontend using Docker with local source code
echo "Building frontend from local source..."

# Create a temporary Dockerfile
cat > /tmp/Dockerfile.build-frontend-local << 'EOF'
FROM node:18

WORKDIR /root/frontend

# Copy package files first for better caching
COPY package.json yarn.lock* ./
RUN yarn install --registry=https://registry.npmmirror.com

# Copy source code
COPY . .

# Build
RUN yarn build

CMD ["sh", "-c", "cp -r /root/frontend/dist/* /output/"]
EOF

# Build the image
docker build -t genuine-oj/frontend-builder-local -f /tmp/Dockerfile.build-frontend-local ../frontend-naive

# Run the build and copy output
echo "Copying build output to ./data/frontend/..."
mkdir -p ./data/frontend
docker run --rm -v "$(pwd)/data/frontend:/output" genuine-oj/frontend-builder-local

echo "Build complete! Restarting frontend container..."
docker-compose restart frontend

echo "Done! Frontend has been updated."
