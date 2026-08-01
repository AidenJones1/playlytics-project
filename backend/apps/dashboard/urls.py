from django.urls import path

import apps.dashboard.views as views

app_name = "dashboard"

urlpatterns = [
    path("", 
        views.DashboardViewSet.as_view({"get": "list"}),
        name="game-of-the-week"
    ),
]