#!/usr/bin/env bash
# Vercel Build Script for A Man's Benchmark
echo "==> Installing Python dependencies..."
python3 -m pip install -r requirements.txt

echo "==> Collecting static assets..."
python3 backend/manage.py collectstatic --noinput --clear

echo "==> Running database migrations..."
python3 backend/manage.py migrate --noinput

echo "==> Build complete."
