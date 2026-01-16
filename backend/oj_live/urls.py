from django.urls import path

from .views import active_session, end_session, get_session, start_session

urlpatterns = [
    path('session/active/', active_session),
    path('session/<int:session_id>/', get_session),
    path('session/start/', start_session),
    path('session/<int:session_id>/end/', end_session),
]
