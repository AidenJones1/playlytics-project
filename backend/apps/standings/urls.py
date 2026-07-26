from django.urls import path

import apps.standings.views as views

app_name = "standings"

urlpatterns = [
    path(
        "league-standings/",
        views.LeagueStandingsViewSet.as_view({"get": "list"}),
        name="league-standings"
    ),
    path(
        "conference-standings/",
        views.ConferenceStandingsViewSet.as_view({"get": "list"}),
        name="conference-standings"
    ),
    path(
        "division-standings/",
        views.DivisionStandingsViewSet.as_view({"get": "list"}),
        name="division-standings"
    ),
]