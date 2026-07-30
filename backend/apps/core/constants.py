# Team Constants
INACTIVE_TEAMS = ["OAK", "STL", "SD", "LAR"]

# Season Types Constants
REGULAR_SEASON_TYPES = ["REG"]
PLAYOFFS_SEASON_TYPES = ["WC", "DIV", "CON", "SB"]

# Historical Year Constants
HISTORICAL_START_YEAR = 2020
HISTORICAL_END_YEAR = 2025

# ELO Ratings Constants
INITIAL_ELO = 1500
K_FACTOR = 30
HOME_FIELD_ADVANTAGE = 25

# Min/Max Constraints
MIN_SEASON_YEAR = 2020
MAX_SEASON_YEAR = 9999
MIN_WEEK_NUMBER = 1
MAX_WEEK_NUMBER = 99

DEFAULT_SEASON = 2025
DEFAULT_WEEK = 22
DEFAULT_WEEK_REGULAR = 18

# Injury Status Weights
INJURY_STATUS_WEIGHTS = {
    "Out": 1.0,
    "Doubtful": 0.7,
    "Questionable": 0.35,
    "Probable": 0.1
}

POSITION_WEIGHTS_INJURY = {
    "QB": 1.0,
    "T": 0.55,
    "C": 0.4,
    "G": 0.3,
    "WR": 0.35,
    "RB": 0.22,
    "FB": 0.15,
    "TE": 0.3,
    "DE": 0.42,
    "DT": 0.3,
    "LB": 0.28,
    "CB": 0.36,
    "S": 0.24,
    "K": 0.1,
    "P": 0.1,
    "LS": 0.1
}