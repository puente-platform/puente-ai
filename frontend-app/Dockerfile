# Multi-stage Dockerfile for the Puente AI frontend (Vite + React).
# Builds the static bundle in a node image, then serves it from nginx.
# Designed to deploy as a Cloud Run service alongside `backend/` (us-central1).

# ---- Build stage ----
FROM node:20-alpine AS build

WORKDIR /app

# Build-time configuration. Vite bakes any `import.meta.env.VITE_*`
# value into the bundle at build time (it does NOT read them at
# runtime), so the value has to be present here, before `npm run build`.
# Default points at the *.run.app form so a local `docker build` works
# without passing --build-arg; CI overrides this to https://api.puenteai.ai
# once the custom-domain Let's Encrypt cert lands. See:
# `frontend-app/src/lib/puente-api.ts:4` for the consumer.
ARG VITE_API_URL=https://puente-backend-519686233522.us-central1.run.app
ENV VITE_API_URL=${VITE_API_URL}

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

# Drop root privileges in the runtime stage. The default nginx:alpine
# image runs the master process as root, which weakens container
# isolation (an RCE in nginx itself or in a future serving handler
# escalates to root inside the container, and matches the DS-0002
# finding from CodeRabbit's review on PR #50).
#
# nginx ships a non-root `nginx` user in the alpine image. We bind to
# the unprivileged Cloud Run-injected $PORT (default 8080, always
# >= 1024 in practice), so we don't need root to listen.
#
# Three writable paths nginx needs even when serving only static
# assets: /var/cache/nginx (proxy + fastcgi temp files even if unused),
# /var/run/nginx.pid (master pid), /etc/nginx/conf.d (envsubst writes
# the rendered template here at container boot). Chown them to the
# nginx user before the USER switch.
RUN chown -R nginx:nginx /var/cache/nginx /etc/nginx/conf.d /usr/share/nginx/html \
    && touch /var/run/nginx.pid \
    && chown nginx:nginx /var/run/nginx.pid

USER nginx

# Cloud Run scales to PORT; default to 8080 locally
ENV PORT=8080
EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
