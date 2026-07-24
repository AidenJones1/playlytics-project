from numpy import log

def calculate_elo_win_probability(home_team_elo: int, away_team_elo: int) -> float:
    exponent = (away_team_elo - home_team_elo) / 400
    return 1 / (1 + 10 ** exponent)

# Award bonus ratings for margin of victory
def calculate_elo_mov_multiplier(point_difference: int, home_team_elo: int, away_team_elo: int) -> float:
    return log(abs(point_difference) + 1) * (2.2 / (((home_team_elo - away_team_elo) * 0.001) + 2.2))