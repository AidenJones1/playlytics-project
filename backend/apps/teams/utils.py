from apps.core import constants

def team_injury_score(injury_report):
    injury_score = 0
    for injury in injury_report:
        injury_score += constants.INJURY_STATUS_WEIGHTS[injury.injury_status] * constants.POSITION_WEIGHTS_INJURY[injury.position]
    return injury_score