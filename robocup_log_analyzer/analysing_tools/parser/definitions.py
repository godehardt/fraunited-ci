from .regex_builder import RAW_REGEX, EXPANDABLE

dont_import_just_register_everything = None

############
# literals #
############

RAW_REGEX("INT",        r'[-+]?\d+')
RAW_REGEX("STATE",      r'(?:0x)?[0-9a-fA-F]+')
RAW_REGEX("FLOAT", r'[-+]?[0-9]*[.]?[0-9]+([ed][-+]?[0-9]+)?')
RAW_REGEX("MATCH_ALL",  r'.*')
RAW_REGEX("WORD",       r'[^ ()]+')
RAW_REGEX("TAB",        r'\t')

# Expandable f"" string like definitions for compound structures

#########
# *.rcg #
#########

EXPANDABLE("SHOW", "(show {step:INT} {ball:BALL} {players:MATCH_ALL})")
EXPANDABLE("BALL","((b) {x:FLOAT} {y:FLOAT} {x_velocity:FLOAT} {y_velocity:FLOAT})")
EXPANDABLE("POINTTO","{point_to_x:FLOAT} {point_to_y:FLOAT} ")
EXPANDABLE("FOCUS","(f {focus_side:[lr]} {focus_target:INT}) ")
EXPANDABLE("FOCUSPOINT","(fp {fp1:FLOAT} {fp2:FLOAT}) ")
EXPANDABLE("C12"," {c12:INT}")
EXPANDABLE("PLAYER","".join([
    "(",
    "({team_side:[lr]} {player_number:INT}) {type:INT} {state:STATE} ",
    "{x:FLOAT} {y:FLOAT} {x_velocity:FLOAT} {y_velocity:FLOAT} ",
    "{body_angle:FLOAT} {neck_angle:FLOAT} ",
    "{pointto:POINTTO?}",
    "(v {view_quality:[^ ]+} {view_area:INT}) ",
    "{fp:FOCUSPOINT?}",
    "(s {stamina:FLOAT} {stamina_effort:FLOAT} ",
    "{stamina_recovery:FLOAT} {stamina_capacity:FLOAT}) ",
    "{focus:FOCUS?}",
    "(c {c1:INT} {c2:INT} {c3:INT} {c4:INT} {c5:INT} {c6:INT} ",
    "{c7:INT} {c8:INT} {c9:INT} {c10:INT} {c11:INT}{c12g:C12?})",
    ")"
    ])
)

EXPANDABLE("PREAMBLE", "{ULG5}|{ULG6}")
EXPANDABLE("PARAMETER","({name:WORD} {value_str:WORD})")
EXPANDABLE("SERVER_PARAM", "(server_param {params:MATCH_ALL})")
EXPANDABLE("PLAYER_PARAM", "(player_param {params:MATCH_ALL})")
EXPANDABLE("PLAYER_TYPE", "(player_type (id {id:INT}){params:MATCH_ALL})")
EXPANDABLE("MSG", "(msg {step:INT} {parameter:INT} {message:MATCH_ALL})")
EXPANDABLE("PLAYMODE", "(playmode {step:INT} {playmode:WORD})")
EXPANDABLE("TEAM", "(team {step:INT} {team_l:WORD} {team_r:WORD} {goals_l:INT} {goals_r:INT})")

#########
# *.rcl #
#########

EXPANDABLE("MESSAGE","".join([
    "{playtime:INT},{pausetime:INT}{tabulator:TAB}",
    "Recv {team_player:WORD}: ",
    "{messages:MATCH_ALL}",
    ]))
EXPANDABLE("REFEREE_MESSAGE","".join([
    "{playtime:INT},{pausetime:INT}{tabulator:TAB}",
    "(referee {decision:WORD})"
    ]))

EXPANDABLE("MESSAGE_COMMAND","({command:WORD} {params:ANY})")


