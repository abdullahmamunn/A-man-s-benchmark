#!/usr/bin/env bash
# Vercel Build Script for A Man's Benchmark
set -e

echo "==> Ensuring static output directory exists..."
mkdir -p staticfiles

echo "==> Installing Python dependencies..."
python3 -m pip install --break-system-packages -r requirements.txt || python3 -m pip install -r requirements.txt

echo "==> Collecting static assets..."
python3 backend/manage.py collectstatic --noinput --clear

echo "==> Running database migrations..."
python3 backend/manage.py migrate --noinput || echo "==> Migrations deferred."

echo "==> Build complete."

