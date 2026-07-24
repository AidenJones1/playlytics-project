from django.urls import path

import apps.accounts.views as views

app_name = "accounts"

urlpatterns = [
    path(
        "register/",
        views.UserViewSet.as_view({"post": "create"}),
        name="register"
    ),
    path(
        "activate/<str:activation_token>/",
        views.ActivationViewSet.as_view({"get": "retrieve"}),
        name="activate"
    ),
    path(
        "user/<str:username>/",
        views.UserViewSet.as_view({
            "get": "retrieve",
            "patch": "partial_update",
            "delete": "destroy"
        }),
        name="user-detail"
    ),
]