# Multi-stage Dockerfile for the Puente AI frontend (Vite + React).
# Builds the static bundle in a node image, then serves it from nginx.
# Designed to deploy as a Cloud Run service alongside `backend/` (us-central1).

# ---- Build stage ----
FROM node:20-alpine AS build

WORKDIR /app

# Copy lockfile + manifest first so dependency layers cache across rebuilds
COPY package.json package-lock.json ./
RUN npm ci

# Now copy the rest of the source and run the production Vite build
COPY . .
RUN npm run build

# ---- Runtime stage ----
FROM nginx:1.27-alpine

# Cloud Run injects $PORT (default 8080) — render an nginx.conf at boot that listens on it.
# This keeps the image portable to local docker run -p 8080:8080 too.
COPY nginx.conf.template /etc/nginx/templates/default.conf.template

# The built Vite assets
COPY --from=build /app/dist /usr/share/nginx/html

# Cloud Run scales to PORT; default to 8080 locally
ENV PORT=8080
EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
