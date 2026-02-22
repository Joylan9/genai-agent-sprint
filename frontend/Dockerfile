# Build stage
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine
# Install bash for the config generation script
RUN apk add --no-cache bash

WORKDIR /usr/share/nginx/html

# Copy built assets
COPY --from=builder /app/dist .
# Copy the config generation script and nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY scripts/generate-config.sh /usr/local/bin/generate-config.sh
RUN chmod +x /usr/local/bin/generate-config.sh

# Default environment variables
ENV API_BASE=http://localhost:8000
ENV REFRESH_ENDPOINT=/api/auth/refresh
ENV APP_VERSION=1.0.0

EXPOSE 80

# Generate config.js at runtime and start nginx
CMD ["/bin/bash", "-c", "/usr/local/bin/generate-config.sh > config.js && nginx -g 'daemon off;'"]
