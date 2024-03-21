import re
from string import Formatter

INT = r'[-+]?\d+'
STATE = r'0x\d+'
FLOAT = r'[-+]?\d*\.?\d+'
MATCH_ALL = r'.*'

BALL = "((b) {ball_x:FLOAT} {ball_y:FLOAT} {ball_vx:FLOAT} {ball_vy:FLOAT})"
PLAYER = "".join([
    "(",
    "({team:[lr]} {player_number:INT}) {player_type:INT} {state:STATE} ",
    "{player_x:FLOAT} {player_y:FLOAT} {player_vx:FLOAT} {player_vy:FLOAT} ",
    "{body_dir:FLOAT} {neck_angle:FLOAT} ",
    "{point_to_x:FLOAT}?{_1:[ ]?}{point_to_y:FLOAT}?{_2:[ ]?}",
    "(v h {view_angle:INT}) ",
    "(s {stamina:FLOAT} {stamina_next:FLOAT} ",
    "{stamina_next_2:FLOAT} {stamina_capacity:FLOAT}) ",
    "(c {c1:INT} {c2:INT} {c3:INT} {c4:INT} {c5:INT} ",
    "{c6:INT} {c7:INT} {c8:INT} {c9:INT} {c10:INT} {c11:INT})",
    ")"
    ])

PLAYERS = "({player:PLAYER}{space:OPTIONAL_SPACE})"
SHOW = "(show {step:INT} {ball:BALL} {players:.* # match all})"

EXPANDABLE_CATEGORIES = {category:globals()[category]
                         for category in "BALL PLAYER SHOW".split()}
RAW_REGEX_CATEGORIES = {category:globals()[category]
                        for category in "INT STATE FLOAT".split()}


def expand(proto_regex,indent=""):
    def escape_prefix(prefix):
        """ escape " ", ")", and "(" """
        return re.sub(r"([ ()])",r"[\1]",prefix)
    final_regex = ""
    for prefix, name, category,_ in Formatter.parse(None, proto_regex):
        prefix_regex = escape_prefix(prefix)
        final_regex += f'# literal "{prefix}"' + "\n"
        final_regex += "  " + escape_prefix(prefix) + "\n"
        if name:
            final_regex += f"# begin of {name} variable" + "\n"
            final_regex += f"  (?P<{name}>" + "\n"
            if category in EXPANDABLE_CATEGORIES:
                final_regex += f"    # {category}" + "\n"
                final_regex += expand(EXPANDABLE_CATEGORIES[category],
                                        indent+"    ") + "\n"
            elif category in RAW_REGEX_CATEGORIES:
                final_regex += f"    # raw {category}" + "\n"
                final_regex += "    "+RAW_REGEX_CATEGORIES[category] + "\n"
            else:
                final_regex += f"    # raw regex: {category}" + "\n"
                final_regex += "    "+category + "\n"
            final_regex += "  )"+"\n"
    final_regex = indent+final_regex.replace("\n","\n"+indent)
    return final_regex

    
# Dummy for now
_REGEXIFY_REGEX = re.compile(expand(SHOW),flags=re.VERBOSE)
_REGEXIFY_REGEX_PLAYER = re.compile(expand(PLAYER),flags=re.VERBOSE)
show_regex = expand(SHOW)
def regexify(line):
    groupdict = _REGEXIFY_REGEX.match(line).groupdict()
    groupdict['players'] = [m.groupdict()
        for m in _REGEXIFY_REGEX_PLAYER.finditer(groupdict['players'])]
    return groupdict

def regexify_uncompiled(line):
    gd = re.match(f'\(show \d+ \(\(b\) (?P<bx>{FLOAT}) (?P<by>{FLOAT}) (?P<bvx>{FLOAT}) (?P<bvy>{FLOAT})\).*',line).groupdict()
    return gd



_LISTIFY_PAD_BRACKETS = re.compile(r"([()])") # matches ( or ) as a group
def listify(line):
    line_tokens = _LISTIFY_PAD_BRACKETS.sub(r' \1 ',line,count=0).strip().split()
    def build_tree(tokens):
        tree = []
        while tokens:
            token, *tokens = tokens
            if token == "(":
                subtree, tokens = build_tree(tokens)
                tree.append(subtree)
            elif token == ")":
                break
            else:
                tree.append(token)
        return tree, tokens
    tree, _ =  build_tree(line_tokens)
    return tree


_ASTIFY_LOCALS_DICT = {x:x for x in "show r l v h f s b c".split()}
def astify(line):
    return eval(line.replace(' ',','),_ASTIFY_LOCALS_DICT)

if __name__ == "__main__":
    # parser internals test run
    test_line = None
    def long_test(function,maxlines=6000):
        global test_line
        results = [None] * 6000
        with open("20180621130004-CYRUS2018_0-vs-HELIOS2018_1.rcg") as f:
            i = 0
            for i,line in enumerate(filter(lambda l:l.startswith("(show"),f.readlines())):
                if i >= maxlines:
                    break
                #function(line)
                test_line = line
                results[i] = function(line)
        return results
        #import pdb;pdb.set_trace()

    def timeit(foo):
        from timeit import timeit
        return timeit(foo,number=1,globals=globals())

    print("regexify:",timeit("long_test(regexify,6000)"))
    #print("regexify_uncompiled:",timeit("long_test(regexify,500)"))
    print("listify:",timeit("long_test(listify,6000)"))
    print("astify:",timeit("long_test(astify,6000)"))
    if not test_line:
        timeit("long_test((lambda x:...),20)")

