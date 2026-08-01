from apps.core import constants

def team_injury_score(injury_report):
    injury_score = 0
    for injury in injury_report:
        injury_score += constants.INJURY_STATUS_WEIGHTS.get(injury.injury_status, 0.0) * constants.POSITION_WEIGHTS_INJURY.get(injury.position, 0.0)
    return injury_score