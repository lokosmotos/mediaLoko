from django.apps import AppConfig

class CandidatesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'candidates'  # ← Must match folder name exactly
