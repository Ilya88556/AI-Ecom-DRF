import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ecom_drf_v1.settings")
app = Celery("ecom_drf_v1")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
