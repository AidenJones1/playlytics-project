from apps.pickems.models import UserPick, GamePickem

def get_game_user_picks(game_obj):
    game_pickem_obj = GamePickem.objects.filter(game=game_obj).first()
    picks = UserPick.objects.filter(pickem=game_pickem_obj).select_related("user", "pickem")

    home_pick_count = picks.filter(team=game_obj.home_team).count()
    away_pick_count = picks.filter(team=game_obj.away_team).count()

    return {
        "home_pick_count": home_pick_count,
        "away_pick_count": away_pick_count,
    }