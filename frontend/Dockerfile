FROM caddy:2.7.6-alpine
RUN apk add --no-cache ca-certificates

WORKDIR /app
COPY plugins ./
COPY static ./static
COPY templates ./
# COPY Caddyfile ./

# Copy static files and run formatting
COPY Caddyfile /etc/caddy/Caddyfile
RUN caddy fmt --overwrite /etc/caddy/Caddyfile


# Ports, health check and non-root user
EXPOSE 3000 3001
# HEALTHCHECK --interval=30s --timeout=3s CMD curl -f http://localhost/:3001/health
USER 1001
