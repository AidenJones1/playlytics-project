from django.urls import path

import apps.elo_ratings.views as views

app_name = "elo_ratings"

urlpatterns = [
    path(
        "ratings-standings/",
        views.TeamELORatingsViewSet.as_view({"get": "list"}),
        name="ratings-standings",
    )
]