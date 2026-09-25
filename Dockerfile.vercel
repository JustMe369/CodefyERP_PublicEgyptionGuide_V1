# Dockerfile.vercel
#
# The app is plain PHP with no Composer dependencies, so no vendor stage.

# Build the final image
FROM dunglas/frankenphp:latest
WORKDIR /app

# Copy your application code
COPY . .

# Copy the Caddyfile configuration
COPY Caddyfile /etc/caddy/Caddyfile

# Set permissions
RUN chown -R www-data:www-data /app

# Use the non-root user
USER www-data

# FrankenPHP will listen on the port Vercel provides
EXPOSE 80