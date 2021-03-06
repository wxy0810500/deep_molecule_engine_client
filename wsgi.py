"""
WSGI config for deep_engine_client project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('RUNTIME_COMMAND', 'runserver')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deep_engine_client.settings.settings')
application = get_wsgi_application()
