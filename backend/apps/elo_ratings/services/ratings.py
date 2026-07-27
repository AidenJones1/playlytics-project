from apps.elo_ratings.models import TeamELORating

def get_pregame_ratings_for_team(team, game):
    ratings_obj = TeamELORating.objects.filter(
        team=team,
        game=game
    ).first()

    return ratings_obj.ratings_before if ratings_obj else 0


def get_postgame_ratings_for_team(team, game):
    ratings_obj = TeamELORating.objects.filter(
        team=team,
        game=game
    ).first()

    return ratings_obj.ratings_after if ratings_obj else 0