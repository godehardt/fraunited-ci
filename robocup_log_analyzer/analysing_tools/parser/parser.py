from ..datamodel.datamodel import Player, Ball, TimeInfo, Game, Message, Playmode, Goal, Dash, Kick, Tackle, \
    RefereeDecision, Turn
import typing

from .definitions import dont_import_just_register_everything
from .regex_builder import regex

import sys


def ERROR(*args):
    """ ERRORing to stderr is used by runHLM.sh to detect errors"""
    print(*args, file=sys.stderr)


def WARNING(*args):
    """ warnings are just ERRORed and ignored by the runHLM.sh error detection """
    print(*args, file=sys.stdout)


_current_time_info = None


def parser(rcg_file, rcl_file, is_compressed=False):
    # datamodel = Game("", "", [], [], [], [], [], [], {}, {}, {})
    datamodel = Game()
    DO_NOTHING = lambda l, d: None
    with open(rcg_file) as f:
        for line_no, line in enumerate(f.readlines(), start=1):
            for start, function in (
                    ("(show", _parse_show),
                    ("(team", _parse_team),
                    ("(playmode", _parse_playmode),
                    ("(msg", _parse_msg),
                    ("(player_type", _parse_player_type),
                    ("(player_param", _parse_player_param),
                    ("(server_param", _parse_server_param),
                    ("ULG5", DO_NOTHING),
                    ("ULG6", DO_NOTHING),
            ):
                try:
                    if line.startswith(start):
                        function(line, datamodel)
                        break
                except Exception as e:
                    ERROR(f"Exception while parsing line {line_no} of the *.rcg file")
                    ERROR(f"rcg file: {rcg_file}:")
                    ERROR("INFO: This is a parser exception. Most likely fixes in sequence:")
                    ERROR("INFO: go to analyzing_tools/parser/definitons.py")
                    ERROR("INFO: Are there new versions of *.rcg files? New features?"
                          "Maybe an EXPANDABLE definition has to be changed.")
                    ERROR("INFO: The datamodel/datamodel.py datatypes names may not be the names of the capture group")
                    ERROR("INFO: Maybe there are additional whitespace or whitespace was lost?"
                          "Check EXPANDABLE definitons for whitespace issues.")
                    ERROR("INFO: RAW_REGEX might not have matched a value. (maybe a NaN or inf)?")
                    raise e
    with open(rcl_file) as f:
        for line_no, line in enumerate(f.readlines(), start=1):
            _parse_rcl_line(line, datamodel)

    return datamodel


def _typecast(value, value_type):
    """cast value_string to value_type
       tries to work with Union[...] and Optional[...] too"""
    if hasattr(value_type, "__origin__") and value_type.__origin__ is typing.Union:
        for subclass in value_type.__args__:
            if subclass is type(None):
                return None
            try:
                return subclass(value)
            except (ValueError, TypeError) as e:
                pass
    else:
        if isinstance(value, value_type):
            return value
        try:
            return value_type(value)
        except (ValueError, TypeError) as e:
            pass
    raise ValueError(f"can't cast {repr(value)} to {value_type} (maybe an unknown name)")


def _collect(dataclass, dictionary):
    dictionary['time_info'] = _current_time_info
    return dataclass(**{
        name:
            _typecast(dictionary.get(name, None), field.type)
        for name, field in dataclass.__dataclass_fields__.items()
    })


def _parse_show(line, datamodel):
    global _current_time_info
    result_dict = regex("SHOW").match(line).groupdict()
    _current_time_info = TimeInfo(int(result_dict['step']), 0)
    datamodel.balls.append(_collect(Ball, result_dict))
    _parse_player(result_dict['players'], datamodel)


def _parse_player(players, datamodel):
    last_end = 0
    for match in regex("PLAYER").finditer(players):
        start, end = match.span()
        if start > last_end + 1:
            ERROR("--- unmatched string ---")
            ERROR(players[last_end:start])
            raise RuntimeError("Player not parsed")
        last_end = end
        result_dict = match.groupdict()
        datamodel.players.append(_collect(Player, result_dict))
    if last_end > len(players) + 1:
        ERROR("--- unmatched string ---")
        ERROR(players[last_end, len(players)])
        ERROR("--- unmatched string ---")
        raise RuntimeError("Player not parsed")


def _parse_msg(line, datamodel):
    global _current_time_info
    result_dict = regex("MSG").match(line).groupdict()
    _current_time_info = TimeInfo(int(result_dict['step']), 0)
    datamodel.messages.append(_collect(Message, result_dict))


def _parse_team(line, datamodel):
    global _current_time_info
    result_dict = regex("TEAM").match(line).groupdict()
    _current_time_info = TimeInfo(int(result_dict['step']), 0)
    datamodel.goals.append(_collect(Goal, result_dict))
    datamodel.team_l = result_dict['team_l']
    datamodel.team_r = result_dict['team_r']


def _parse_playmode(line, datamodel):
    global _current_time_info
    result_dict = regex("PLAYMODE").match(line).groupdict()
    _current_time_info = TimeInfo(int(result_dict['step']), 0)
    datamodel.playmode_changes.append(
        Playmode(result_dict['playmode'], _current_time_info))


def _parse_parameters_to_dict(params_raw):
    parameters = {}
    for match in regex("PARAMETER").finditer(params_raw):
        name = match.groupdict()['name']
        value = match.groupdict()['value_str']
        if regex("INT").fullmatch(value):
            value = int(value)
        elif regex("FLOAT").fullmatch(value):
            value = float(value)
        parameters[name] = value
    return parameters


def _parse_player_type(line, datamodel):
    result_dict = regex("PLAYER_TYPE").match(line).groupdict()
    datamodel.player_types[result_dict['id']] = _parse_parameters_to_dict(result_dict['params'])


def _parse_player_param(line, datamodel):
    params_raw = regex("PLAYER_PARAM").match(line).groupdict()['params']
    datamodel.player_params.update(_parse_parameters_to_dict(params_raw))


def _parse_server_param(line, datamodel):
    params_raw = regex("SERVER_PARAM").match(line).groupdict()['params']
    datamodel.server_params.update(_parse_parameters_to_dict(params_raw))


# FIXME: How to parse this correctly? '(dash 100)(turn_neck -136)(say "j4S9W*4y)?")'
# FIXME: Correct (and escaped) bracket languages are too powerful for regex :/
# FIXME: I hate this right now, have to change strategy here, as `say` can be arbitrary
def _parse_rcl_commands(messages, team, player, datamodel):
    last_end = 0
    assert (messages.startswith("(") and messages.endswith(")"))
    messages = messages[1:-1]
    for message in messages.split(")("):  # HOPE THIS WORKS
        command, *args = message.split()
        if command == "kick":
            datamodel.kicks.append(
                Kick(team, player,
                     time_info=_current_time_info,
                     power=float(args[0]),
                     direction=float(args[1]),
                     ))
        elif command == "tackle":
            datamodel.tackles.append(
                Tackle(team, player, time_info=_current_time_info,
                       power_or_direction=float(args[0]),
                       foul=False if len(args) < 2 else args[1] == "on",
                       ))
        elif command == "dash":
            datamodel.dashes.append(
                Dash(team, player, time_info=_current_time_info,
                     power=float(args[0]),
                     direction=None if len(args) < 2 else float(args[1]),
                     ))
        elif command == "turn":
            datamodel.turns.append(
                Turn(team, player, time_info=_current_time_info,
                     angle=float(args[0]),
                     ))
        else:
            datamodel.other_events[command].append((team, player, args, _current_time_info))


def _parse_rcl_message(result_dict, datamodel):
    team_player_split = result_dict['team_player'].split("_")
    team = "_".join(team_player_split[:-1])
    player = team_player_split[-1]
    if player != "Coach":
        player = int(player)
    _parse_rcl_commands(result_dict['messages'], team, player, datamodel)


def _parse_rcl_referee_msg(result_dict, datamodel):
    decision_parts = result_dict['decision'].split("_")
    side_trans = {'l': 'left', 'r': 'right'}
    if len(decision_parts) >= 2:
        *name, x, y = decision_parts
        if x == 'l' or x == 'r':
            try:
                result_dict['player_number_or_goals'] = int(y)
                result_dict['team_side'] = side_trans.get(x, 'no_side')
                result_dict['decision'] = "_".join(name + [x])
            except ValueError as e:
                WARNING(f"Could not parse referee decision {'_'.join(decision_parts)}: should end in integer")
                return
        elif y == 'l' or y == 'r':
            result_dict['team_side'] = side_trans.get(y, 'no_side')
        else:
            result_dict['team_side'] = 'no_side'

    try:
        datamodel.referee_decisions.append(_collect(RefereeDecision, result_dict))
    except ValueError as e:
        WARNING(f"Unhandled Referee Decision {'_'.join(decision_parts)}")


def _parse_rcl_line(line, datamodel):
    global _current_time_info

    match = regex("MESSAGE").match(line)
    if match:
        result_dict = match.groupdict()
        _current_time_info = TimeInfo(int(result_dict['playtime']), int(result_dict['pausetime']))
        _parse_rcl_message(result_dict, datamodel)
        return

    match = regex("REFEREE_MESSAGE").match(line)
    if match:
        result_dict = match.groupdict()
        _current_time_info = TimeInfo(int(result_dict['playtime']), int(result_dict['pausetime']))
        _parse_rcl_referee_msg(result_dict, datamodel)
        return

    raise RuntimeError(f"line not parsed\n{line}")
