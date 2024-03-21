from typing import Dict, List
from ..constants.referee_decisions import EnumRefereeDecision, EnumTeamSide
from ..datamodel.datamodel import Tackle, RefereeDecision, Kick, Ball
from ..constants.robocup_constants import GAME_OVER_TIME, HALF_TIME, MAX_BALL_SPEED, BALL_SPEED_DECAY
from ..constants.football_constants import END_LINE_LEFT_TEAM, END_LINE_RIGHT_TEAM, OUT_LINE_LEFT, \
    OUT_LINE_RIGHT


# TODO: replace Return dicts with dataclasses?
# TODO: standardise team name parameters
# ------ UAS like analysis --------------
def get_tackle_times(tackles: List[Tackle], team1_name: str, team2_name: str) -> Dict[str, List[int]]:
    tackles_times = {team1_name: [],
                     team2_name: []}

    for t in tackles:
        tackles_times[t.team_name].append(t.time_info.playtime)

    return tackles_times


def analyze_ball_field_half_ratio(balls: List[Ball], team1_name: str, team2_name: str) -> Dict[str, float]:
    team1_half_counter = 0
    team2_half_counter = 0

    for ball in balls:
        if ball.x < 0:
            team1_half_counter += 1
        else:
            team2_half_counter += 1

    total = team1_half_counter + team2_half_counter

    return {team1_name: round((team1_half_counter / total) * 100, 1),
            team2_name: round((team2_half_counter / total) * 100, 1)}


def count_referee_decisions(ref_decisions: List[RefereeDecision], team_name_l: str, team_name_r: str) \
        -> Dict[str, Dict[EnumRefereeDecision, int]]:
    decision_counter_dict = {e: 0 for e in EnumRefereeDecision}

    for d in ref_decisions:
        # d.decision to make sure decision is not None
        # TODO: don't allow None as decision
        if d.decision:
            decision_counter_dict[d.decision] += 1

    return decision_counter_dict


def get_referee_decision_timestemps(ref_decisions: List[RefereeDecision], team_name_l: str, team_name_r: str) \
        -> Dict[EnumRefereeDecision, List[int]]:
    decision_timer_dict = {e: [] for e in EnumRefereeDecision}

    for d in ref_decisions:
        # d.decision to make sure decision is not None
        # TODO: don't allow None as decision
        if d.decision:
            decision_timer_dict[d.decision].append(d.time_info.playtime)

    return decision_timer_dict


def analyze_possession_percentage(ref_decisions: List[RefereeDecision], kicks: List[List[Kick]],
                                  team_name_l: str, team_name_r: str) -> Dict[str, float]:
    """
    Calculates the possession percentage of both teams

    :param ref_decisions: A list of all referee decisions of the game (ordered by playtime)
    :param kicks: a list of all successful kicks (and tackles) of the game (ordered in sublists of playtime)
    :param team_name_l: name of the left team
    :param team_name_r: name of the right team
    :return: dict with teamname as key and possession percentage as value
    """
    # initialize the return dictionary
    possession_time_dict = {team_name_l: 0,
                            team_name_r: 0}
    # setup iterators
    decision_iter = iter(ref_decisions)
    kick_iter = iter(kicks)
    # get the first value of both lists
    current_decision = next(decision_iter)
    current_kick = next(kick_iter)
    # the last time the ball possession changed
    last_possession_change_time = 0
    # name of the last team in possession -> starts with team that does the kickoff
    # WARNING: assumes that kickoff is the first decision off the referee
    last_team_in_possession = team_name_l if current_decision.decision == EnumRefereeDecision.KICK_OFF_L else team_name_r

    # time at which the kick happened
    kick_time = current_kick[0].time_info.playtime
    # time at which the referee decision happened
    decision_time = current_decision.time_info.playtime

    last_decision = None
    neutral = False
    while current_decision.decision != EnumRefereeDecision.TIME_OVER:
        # handle kicks and decisions in correct timing order
        if kick_time < decision_time:
            was_neutral = neutral
            neutral = len(current_kick) > 1

            # if the gamemode is not play_on no possession is counted
            if last_decision.decision != EnumRefereeDecision.PLAY_ON:
                neutral = True
            # if a multiple kicks occurred
            elif neutral and not was_neutral:
                team = current_kick[0].team_name
                intercept = False
                # check if the kick was intercepted
                for k in current_kick[1:]:
                    if k.team_name != team:
                        intercept = True
                        break
                if intercept:
                    # store the amount of possession time
                    possession_time_dict[last_team_in_possession] += kick_time - last_possession_change_time
                else:
                    neutral = False
            # if a team kicks the ball after a neutral possession
            elif not neutral and was_neutral:
                # set possession time offset
                last_possession_change_time = kick_time
                # set new team in possession
                last_team_in_possession = current_kick[0].team_name

            # if ball possession changed #not else if because of multi kick possession change
            if not neutral and not was_neutral and last_team_in_possession != current_kick[0].team_name:
                # store the amount of possession time
                possession_time_dict[last_team_in_possession] += kick_time - last_possession_change_time
                # set possession time offset
                last_possession_change_time = kick_time
                # set new team in possession
                last_team_in_possession = current_kick[0].team_name

            # get the next kick
            try:
                current_kick = next(kick_iter)
                kick_time = current_kick[0].time_info.playtime
            except StopIteration:
                # set kicktime to always be bigger than the last referee decision
                kick_time = GAME_OVER_TIME + 1
        # handle next referee decision
        else:
            if not neutral and current_decision.decision in EnumRefereeDecision.get_kick_decisions():
                # store the amount of possession time, when an event happens
                possession_time_dict[last_team_in_possession] += decision_time - 1 - last_possession_change_time
                last_possession_change_time = decision_time
                last_team_in_possession = team_name_l if current_decision.team_side == EnumTeamSide.LEFT else team_name_r
                neutral = True
            if current_decision.decision == EnumRefereeDecision.GOAL_L or \
                    current_decision.decision == EnumRefereeDecision.GOAL_R:
                possession_time_dict[last_team_in_possession] += decision_time - last_possession_change_time
                neutral = True

            # get the next decision
            try:
                last_decision = current_decision
                current_decision = next(decision_iter)
                decision_time = current_decision.time_info.playtime
            except StopIteration:
                pass

    # add remaining possession time to team that possessed the ball before the game ended
    if not neutral:
        possession_time_dict[last_team_in_possession] += decision_time - last_possession_change_time

    # calculate the total amount of possession time
    total_possession_time = possession_time_dict[team_name_l] + possession_time_dict[team_name_r]
    # calculate the possession percentage
    for team, pos_time in possession_time_dict.items():
        possession_time_dict[team] = round((pos_time / total_possession_time) * 100, 1)

    return possession_time_dict


def count_passes_and_missed_passes(kicks: List[Kick], team1_name: str, team2_name: str) -> Dict[str, List[int]]:
    # team name: [correct passes, missed passes]
    team_pass_analysis = {team1_name: [0, 0],
                          team2_name: [0, 0]}

    last_team_that_kicked = None

    for kick in kicks:
        if kick.team_name == team1_name:
            if last_team_that_kicked == team1_name:
                team_pass_analysis[team1_name][0] += 1
            else:
                # TODO: check if this is correct (instead of team2 whose missed pass count should go up)
                team_pass_analysis[team1_name][1] += 1
        else:
            if last_team_that_kicked == team2_name:
                team_pass_analysis[team2_name][0] += 1
            else:
                # TODO: check if this is correct (instead of team1 whose missed pass count should go up)
                team_pass_analysis[team2_name][1] += 1
        last_team_that_kicked = kick.team_name

    return team_pass_analysis


def count_successful_and_unsuccessful_dribblings(kicks: List[Kick],  team1_name: str, team2_name: str) -> Dict[str, List[int]]:
    team_dribblings_dict = {team1_name: [0, 0],
                            team2_name: [0, 0]}

    last_kick_power = 0
    last_team_that_kicked = None
    last_player_that_kicked = None
    for kick in kicks:
        if kick.team_name == last_team_that_kicked and \
           kick.power > last_kick_power:     # TODO: Why?
            if kick.player_number == last_player_that_kicked:
                team_dribblings_dict[kick.team_name][0] += 1
            else:
                last_player_that_kicked = kick.player_number
        else:
            # TODO: check if this shouldn't be last_team_that_kicked instead of kick.team_name
            team_dribblings_dict[kick.team_name][1] += 1
            last_team_that_kicked = kick.team_name
            last_player_that_kicked = kick.player_number
        last_kick_power = kick.power

    return team_dribblings_dict


def get_goals_per_half_and_timing(referee_decisions: List[RefereeDecision],
                                  team_name_l: str, team_name_r: str) -> Dict[str, List[object]]:
    # team name: [first half, second half, after time, goal times
    goal_count_dict = {team_name_l: [0, 0, 0, []],
                       team_name_r: [0, 0, 0, []]}

    for ref_dec in referee_decisions:
        if ref_dec.decision == EnumRefereeDecision.GOAL_L:
            goal_count_dict[team_name_l][ref_dec.time_info.playtime // HALF_TIME] += 1
            goal_count_dict[team_name_l][3].append(ref_dec.time_info.playtime)
        elif ref_dec.decision == EnumRefereeDecision.GOAL_R:
            goal_count_dict[team_name_r][ref_dec.time_info.playtime // HALF_TIME] += 1
            goal_count_dict[team_name_r][3].append(ref_dec.time_info.playtime)

    return goal_count_dict


# TODO: What does this analyse
def analyse_shot(kicks: List[Kick], balls: List[Ball], team1_name: str, team2_name: str) -> Dict[str, List[int]]:
    # team name: [shot on target, shot]
    shot_count_dict = {team1_name: [0, 0],
                       team2_name: [0, 0]}

    # setup ball iterator
    ball_iter = iter(balls)

    for kick in kicks:
        time = kick.time_info.playtime
        try:
            ball = next(ball_iter)

            # find ball with correct time
            while ball.time_info.playtime < time:
                ball = next(ball_iter)

            # calculate where the shot is going to be
            # TODO: maybe use the real velocity instead of the maximum
            # TODO: check if this should be * BALL_SPEED_DECAY isntead of - BALL_SPEED_DECAY
            next_x = ball.x + MAX_BALL_SPEED - BALL_SPEED_DECAY
            next_y = ball.y + MAX_BALL_SPEED - BALL_SPEED_DECAY

            # TODO: check where the magic numbers come from
            if 44.25 < next_x < END_LINE_RIGHT_TEAM and OUT_LINE_LEFT < next_y < OUT_LINE_RIGHT:
                shot_count_dict[team1_name][1] += 1
                if -20.16 < next_y < 20.16:
                    shot_count_dict[team1_name][0] += 1
            elif END_LINE_LEFT_TEAM < next_x < -44.25 and OUT_LINE_LEFT < next_y < OUT_LINE_RIGHT:
                shot_count_dict[team2_name][1] += 1
                if -20.16 < next_y < 20.16:
                    shot_count_dict[team2_name][0] += 1
        except StopIteration:
            continue
    return shot_count_dict
