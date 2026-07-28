from django.urls import path

import apps.teams.views as views

app_name = "teams"

urlpatterns = [
    path(
        "<str:team_abbreviation>/",
        views.TeamViewSet.as_view({"get": "retrieve"}),
        name="team-detail"
    ),
]