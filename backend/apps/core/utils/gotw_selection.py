from apps.elo_ratings.models import TeamELORating
from apps.models.models import Prediction
from apps.standings.models import TeamStandings
from apps.standings.services.rankings import get_team_pregame_rankings

def competitiveness(game_obj):
    home_rating = TeamELORating.objects.filter(game=game_obj, team=game_obj.home_team).first()
    away_rating = TeamELORating.objects.filter(game=game_obj, team=game_obj.away_team).first()
    if not home_rating or not away_rating:
        return 0

    rating_diff = abs(home_rating.ratings_before - away_rating.ratings_before)
    elo_score = max(0, 1 - (rating_diff / 400))

    prediction = Prediction.objects.filter(game=game_obj).first()
    if not prediction:
        return elo_score
    model_score = 1 - abs(prediction.home_win_probability - 0.5) * 2

    competitiveness_score = (elo_score + model_score) / 2
    return competitiveness_score


def team_quality(game_obj):
    home_standings = TeamStandings.objects.filter(team=game_obj.home_team, week=game_obj.week).first()
    away_standings = TeamStandings.objects.filter(team=game_obj.away_team, week=game_obj.week).first()
    if not home_standings or not away_standings:
        return 0
    home_season_win_pct = home_standings.wins / (home_standings.wins + home_standings.losses) if (home_standings.wins + home_standings.losses) > 0 else 0
    away_season_win_pct = away_standings.wins / (away_standings.wins + away_standings.losses) if (away_standings.wins + away_standings.losses) > 0 else 0
    quality_score = (min(home_season_win_pct, away_season_win_pct) * .6) + ((home_season_win_pct + away_season_win_pct) * .4)
    return quality_score

def stakes(game_obj):
    stakes_score = 0

    # Division > conference > cross-conference
    if game_obj.home_team.division == game_obj.away_team.division:
        rivalry_score = 1.0
    elif game_obj.home_team.conference == game_obj.away_team.conference:
        rivalry_score = 0.5
    else:
        rivalry_score = 0.0
    stakes_score += rivalry_score * 0.35

    if game_obj.week.week < 5:
        return stakes_score

    # Playoff relevance via conference rank (16 teams, 7 spots per conference)
    TEAMS_PER_CONFERENCE = 16
    home_rankings = get_team_pregame_rankings(game_obj, game_obj.home_team)
    away_rankings = get_team_pregame_rankings(game_obj, game_obj.away_team)
    if home_rankings and away_rankings:
        home_rank = home_rankings.get("conference_rank", TEAMS_PER_CONFERENCE)
        away_rank = away_rankings.get("conference_rank", TEAMS_PER_CONFERENCE)
        home_playoff_score = max(0, (TEAMS_PER_CONFERENCE - home_rank) / (TEAMS_PER_CONFERENCE - 1))
        away_playoff_score = max(0, (TEAMS_PER_CONFERENCE - away_rank) / (TEAMS_PER_CONFERENCE - 1))
        playoff_score = (home_playoff_score + away_playoff_score) / 2
    else:
        playoff_score = 0

    stakes_score += playoff_score * 0.45
    return stakes_score

def narrative(game_obj):
    home_standings = TeamStandings.objects.filter(team=game_obj.home_team, week=game_obj.week).first()
    away_standings = TeamStandings.objects.filter(team=game_obj.away_team, week=game_obj.week).first()
    if not home_standings or not away_standings:
        return 0

    def _streak_score(streak):
        if not streak or streak == '-' or len(streak) < 2:
            return 0
        return min(int(streak[1:]) / 5, 1.0)

    home_streak = _streak_score(home_standings.streak)
    away_streak = _streak_score(away_standings.streak)
    streak_score = (home_streak + away_streak) / 2

    # Hot vs cold matchup amplifies the narrative
    home_dir = home_standings.streak[0] if home_standings.streak != '-' else None
    away_dir = away_standings.streak[0] if away_standings.streak != '-' else None
    if home_dir and away_dir and home_dir != away_dir:
        streak_score = min(streak_score * 1.3, 1.0)

    # Higher combined scoring = more entertaining game
    PPG_CEILING = 35
    home_ppg = home_standings.points_for / home_standings.games_played if home_standings.games_played > 0 else 0
    away_ppg = away_standings.points_for / away_standings.games_played if away_standings.games_played > 0 else 0
    scoring_score = min(((home_ppg + away_ppg) / 2) / PPG_CEILING, 1.0)

    return streak_score * 0.5 + scoring_score * 0.5