from django.contrib.auth import get_user_model
from django.db.models import Count, F, Q

from apps.pickems import models as m
from apps.scheduling.choices import GameStatus

INVALID_SEASON_ERROR_MESSAGE = "Invalid season/seasons format. Use season=2024 or seasons=2024,2025."

User = get_user_model()


def parse_season_years(query_params):
    season_param = query_params.get("season")
    seasons_param = query_params.get("seasons")
    season_years = []

    if season_param:
        season_years.append(int(season_param.strip()))
    if seasons_param:
        season_years.extend(
            [int(year.strip()) for year in seasons_param.split(",") if year.strip()]
        )

    return list(dict.fromkeys(season_years))


def build_requested_user_rank(leaderboard, username):
    return next(
        (
            {
                "rank": entry["rank"],
                "wins": entry["wins"],
                "losses": entry["losses"],
                "accuracy": entry["accuracy"],
            }
            for entry in leaderboard
            if entry["user"] == username
        ),
        {
            "rank": None,
            "wins": 0,
            "losses": 0,
            "accuracy": 0,
        },
    )


def build_requested_user_groups(user):
    requested_user_groups = list(
        m.PickemGroupMember.objects.filter(user=user)
        .select_related("group")
        .order_by("group__name")
        .values("group__name", "group__group_key")
    )
    return [
        {
            "name": group["group__name"],
            "group_key": group["group__group_key"],
        }
        for group in requested_user_groups
    ]


def build_group_leaderboard(group_obj, season_years):
    members = list(
        m.PickemGroupMember.objects.filter(group=group_obj)
        .select_related("user")
        .order_by("user__username")
    )
    user_ids = [member.user.id for member in members]

    win_filter, loss_filter = _build_pick_outcome_filters()

    picks_queryset = m.UserPick.objects.filter(user_id__in=user_ids)
    if season_years:
        picks_queryset = picks_queryset.filter(
            pickem__game__week__season__year__in=season_years
        )

    stats_rows = picks_queryset.values("user_id").annotate(
        wins=Count("id", filter=win_filter),
        losses=Count("id", filter=loss_filter),
    )
    stats_by_user = {row["user_id"]: row for row in stats_rows}

    leaderboard = []
    for member in members:
        stats = stats_by_user.get(member.user.id, {})
        leaderboard.append(
            _build_leaderboard_entry(
                username=member.user.username,
                wins=stats.get("wins", 0) or 0,
                losses=stats.get("losses", 0) or 0,
            )
        )

    return _rank_leaderboard(leaderboard)


def build_global_leaderboard(season_years):
    win_filter, loss_filter = _build_pick_outcome_filters()

    picks_queryset = m.UserPick.objects.all()
    if season_years:
        picks_queryset = picks_queryset.filter(
            pickem__game__week__season__year__in=season_years
        )

    stats_rows = picks_queryset.values("user_id").annotate(
        picks=Count("id"),
        wins=Count("id", filter=win_filter),
        losses=Count("id", filter=loss_filter),
    )

    user_ids = [row["user_id"] for row in stats_rows if (row.get("picks", 0) or 0) > 0]
    users = list(User.objects.filter(id__in=user_ids).order_by("username"))
    stats_by_user = {
        row["user_id"]: row
        for row in stats_rows
        if (row.get("picks", 0) or 0) > 0
    }

    leaderboard = []
    for user in users:
        stats = stats_by_user.get(user.pk, {})
        leaderboard.append(
            _build_leaderboard_entry(
                username=user.username,
                wins=stats.get("wins", 0) or 0,
                losses=stats.get("losses", 0) or 0,
            )
        )

    return _rank_leaderboard(leaderboard)


def _build_pick_outcome_filters():
    win_filter = Q(pickem__game__status=GameStatus.COMPLETED) & (
        Q(
            team_id=F("pickem__game__home_team_id"),
            pickem__game__home_score__gt=F("pickem__game__away_score"),
        )
        | Q(
            team_id=F("pickem__game__away_team_id"),
            pickem__game__away_score__gt=F("pickem__game__home_score"),
        )
    )
    loss_filter = Q(pickem__game__status=GameStatus.COMPLETED) & (
        Q(
            team_id=F("pickem__game__home_team_id"),
            pickem__game__home_score__lt=F("pickem__game__away_score"),
        )
        | Q(
            team_id=F("pickem__game__away_team_id"),
            pickem__game__away_score__lt=F("pickem__game__home_score"),
        )
    )
    return win_filter, loss_filter


def _build_leaderboard_entry(username, wins, losses):
    total = wins + losses
    accuracy = round(wins / total, 3) if total > 0 else 0
    return {
        "user": username,
        "wins": wins,
        "losses": losses,
        "accuracy": accuracy,
    }


def _rank_leaderboard(leaderboard):
    leaderboard.sort(key=lambda entry: (-entry["accuracy"], -entry["wins"], entry["user"]))
    for idx, entry in enumerate(leaderboard, start=1):
        entry["rank"] = idx
    return leaderboard