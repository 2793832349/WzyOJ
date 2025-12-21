# Genuine OJ Docker Deployment Script

## Pre-requirements

* Docker Engine 17.04.0+
* Docker Compose(built-in by default)

## Steps for manual build

### 1. Configuration

Change the **environment** field in `docker-compose.yml` **according to your needs!** `docker-compose.yml` contain variables for backend and database.

### 2. Build the frontend compiler image

```bash
docker compose -f docker-compose.builder.yml build
```

### 3. Compile the frontend page to static files

```bash
docker compose -f docker-compose.builder.yml run --rm build-frontend
```

### 4. Build the backend and judge-server image

```bash
docker compose build
```

### 5. Create a secret.key file in the data/backend directory

```bash
mkdir -p ./data/backend
touch ./data/backend/secret.key
```

### 6. Boot up the server

```bash
docker compose up -d
```
