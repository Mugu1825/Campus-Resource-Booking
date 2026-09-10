#!/bin/bash
set -e

# Support Render's dynamic PORT variable or fallback to 80
PORT="${PORT:-80}"
echo "Configuring Nginx to listen on port ${PORT}..."
sed -i "s/LISTEN_PORT/${PORT}/g" /etc/nginx/conf.d/default.conf

# Start Gunicorn in background on loopback
echo "Starting Gunicorn backend on 127.0.0.1:5000..."
cd /app/backend
gunicorn --bind 127.0.0.1:5000 --workers 2 --threads 2 --access-logfile - --error-logfile - app:app &

# Wait for backend health check
echo "Waiting for backend service to become ready..."
for i in $(seq 1 20); do
  if curl -s http://127.0.0.1:5000/api/health | grep -q "ok"; then
    echo "Backend is healthy and ready!"
    break
  fi
  sleep 1
done

echo "Starting Nginx frontend proxy..."
exec nginx -g 'daemon off;'
