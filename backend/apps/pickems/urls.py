from django.urls import path

import apps.pickems.views as views

app_name = "pickems"

urlpatterns = [
    path(
        "groups/",
        views.PickemGroupViewSet.as_view({
            "post": "create",
            "get": "list"
        }),
        name="create-group"
    ),
    path(
        "groups/<str:group_key>/",
        views.PickemGroupViewSet.as_view({
            "delete": "destroy"
        }),
        name="delete-group"
    ),
    path(
        "join-group/",
        views.PickemsGroupMemberViewSet.as_view({
            "post": "create"
        }),
        name="join-group"
    ),
    path(
        "groups/<str:group_key>/members/",
        views.PickemsGroupMemberViewSet.as_view({
            "get": "list",
            "delete": "destroy"
        }),
        name="list-group-members"
    ),
    path(
        "groups/<str:group_key>/owner/",
        views.PickemGroupOwnerViewSet.as_view({"put": "update"}),
        name="transfer-group-ownership"
    ),
    path(
        "groups/<str:group_key>/remove-member/",
        views.PickemGroupOwnerViewSet.as_view({"delete": "destroy"}),
        name="remove-member"
    ),
    path(
        "user-picks/<str:game_id>/",
        views.UserPickViewSet.as_view({"post": "create"}),
        name="user-picks"
    ),
    path(
        "groups/<str:group_key>/leaderboard/",
        views.GroupPickemLeaderboardViewSet.as_view({"get": "list"}),
        name="group-leaderboard"
    ),
    path(
        "global-leaderboard/",
        views.GlobalPickemLeaderboardViewSet.as_view({"get": "list"}),
        name="global-leaderboard"
    ),
]