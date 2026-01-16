from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class BattleConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'oj_battle'
    verbose_name = _('Battle')
