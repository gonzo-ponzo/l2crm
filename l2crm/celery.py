import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'l2crm.settings')

app = Celery('l2crm')
app.loader.override_backends['django-db'] = 'django_celery_results.backends.database:DatabaseBackend'
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')