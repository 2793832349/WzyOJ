from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import BattleRoomViewSet
from .views_rating import leaderboard, my_rating, battle_history, seasons

router = SimpleRouter()
router.register('rooms', BattleRoomViewSet, basename='battle_room')

urlpatterns = [
    path('leaderboard/', leaderboard, name='battle_leaderboard'),
    path('my-rating/', my_rating, name='my_battle_rating'),
    path('history/', battle_history, name='battle_history'),
    path('seasons/', seasons, name='battle_seasons'),
] + router.urls
