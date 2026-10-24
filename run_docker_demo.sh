#!/bin/bash
set -e

cd /home/mugunth/.gemini/antigravity/scratch/campus-booking

echo "=========================================================="
echo " 1. BUILDING DOCKER IMAGE (campus-booking:latest)"
echo "=========================================================="
docker build -t campus-booking .

echo ""
echo "=========================================================="
echo " 2. STOPPING ANY EXISTING CONTAINER (clean slate)"
echo "=========================================================="
docker rm -f campus-booking-app 2>/dev/null || true

echo ""
echo "=========================================================="
echo " 3. RUNNING CONTAINER (Port 3000 -> 80)"
echo "=========================================================="
docker run -d \
  --name campus-booking-app \
  --dns 8.8.8.8 \
  --dns 1.1.1.1 \
  -p 3000:80 \
  --env-file backend/.env \
  campus-booking

echo ""
echo "=========================================================="
echo " 4. WAITING FOR CONTAINER TO INITIALIZE..."
echo "=========================================================="
sleep 4

echo ""
echo "=========================================================="
echo " 5. CONTAINER STATUS (docker ps)"
echo "=========================================================="
docker ps --filter "name=campus-booking-app"

echo ""
echo "=========================================================="
echo " 6. CONTAINER LOGS (Gunicorn + Nginx Startup)"
echo "=========================================================="
docker logs campus-booking-app

echo ""
echo "=========================================================="
echo " 7. TESTING LOCALHOST:3000 VIA CURL"
echo "=========================================================="
curl -s -I http://localhost:3000 | head -n 5
curl -s http://localhost:3000/api/health

echo ""
echo "=========================================================="
echo " SUCCESS! Open http://localhost:3000 in your browser!"
echo "=========================================================="
