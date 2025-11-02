import os
from celery import Celery

# os.environ.setdescover_tasks()
# app = Celery("core")
# app.config_from_object("django.conf:settings", "core.settings")
# app.autodiscover_tasks()


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
app = Celery("app")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()