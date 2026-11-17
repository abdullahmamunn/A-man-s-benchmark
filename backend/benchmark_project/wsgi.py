"""
WSGI config for benchmark_project.
Exposes the WSGI callable as both `application` and `app` (standard for Vercel).
"""
import os
import sys
from pathlib import Path
from django.core.wsgi import get_wsgi_application

# Ensure backend directory is in sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'benchmark_project.settings')

application = get_wsgi_application()
app = application # Vercel serverless entry point
