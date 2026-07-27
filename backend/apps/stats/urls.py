from django.urls import path

import apps.stats.views as views

app_name = "stats"

urlpatterns = [
    path(
        'season-stats/',
        views.SeasonStatsViewSet.as_view({'get': 'list'}),
        name='season-stats'
    ),
]