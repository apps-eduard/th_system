# from django.apps import AppConfig


# class MonitoringConfig(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'monitoring'



from django.apps import AppConfig

class ThMonitoringConfig(AppConfig):
    name = 'monitoring'

    def ready(self):
        from . import tasks
        tasks.start()