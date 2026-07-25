from django.urls import path

import apps.scheduling.views as views

app_name = "scheduling"

urlpatterns = [
    path(
        "weekly-schedule/",
        views.WeeklyScheduleViewSet.as_view({"get": "list"}),
        name="weekly-schedule"
    ),
]