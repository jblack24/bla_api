"""
WSGI config for bet_stats project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""

import os


from django.core.wsgi import get_wsgi_application
import django
django.setup()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bet_stats.settings")

application = get_wsgi_application()
