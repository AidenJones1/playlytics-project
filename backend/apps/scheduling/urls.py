from django.urls import path

import apps.scheduling.views as views

app_name = "scheduling"

urlpatterns = [
    path(
        "weekly-schedule/",
        views.WeeklyScheduleViewSet.as_view({"get": "list"}),
        name="weekly-schedule"
    ),
    path(
        "team-schedule/",
        views.TeamScheduleViewSet.as_view({"get": "list"}),
        name="team-schedule"
    ),
    path(
        "game-preview/<str:game_id>/",
        views.GamePreviewViewSet.as_view({"get": "retrieve"}),
        name="game-preview"
    ),
]