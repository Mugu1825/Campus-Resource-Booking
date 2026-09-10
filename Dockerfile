FROM python:3.12-slim

# Install system dependencies (Nginx and curl)
RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python requirements
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy backend application code
COPY backend /app/backend

# Copy frontend assets to Nginx standard directory
COPY frontend /usr/share/nginx/html

# Clean up default site and install our custom Nginx config
RUN rm -f /etc/nginx/sites-enabled/default /etc/nginx/sites-available/default 2>/dev/null || true
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Setup startup entrypoint script
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Render injects PORT dynamically (typically 10000); default to 80 for local
ENV PORT=80
EXPOSE 80 10000

ENTRYPOINT ["/app/entrypoint.sh"]
