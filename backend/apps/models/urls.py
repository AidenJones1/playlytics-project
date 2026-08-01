from django.urls import path

import apps.models.views as views

app_name = 'models'

urlpatterns = [
    path(
        'performance/<str:model_version>/',
        views.ModelPerformanceViewSet.as_view({'get': 'retrieve'}),
        name='model-performance'
    ),
]