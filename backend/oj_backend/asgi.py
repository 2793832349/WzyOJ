"""
ASGI config for oj_backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/asgi/
"""

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oj_backend.settings')

django_asgi_app = get_asgi_application()

import oj_submission.routing
import oj_battle.routing
import oj_live.routing

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                oj_submission.routing.websocket_urlpatterns
                + oj_battle.routing.websocket_urlpatterns
                + oj_live.routing.websocket_urlpatterns
            )
        )
    )
})
