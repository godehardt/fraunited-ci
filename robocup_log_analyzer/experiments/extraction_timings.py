import sys
sys.path.extend((['../']))

import functools
from analysing_tools.parser.rcg_parser import RcgParser
from analysing_tools.parser.rcl_parser import RclParser
from timeit import repeat
from statistics import mean


def parse_rcg_and_rcl():
    rcg_file = "../20180621130004-CYRUS2018_0-vs-HELIOS2018_1.rcg"
    rcl_file = "../20180621130004-CYRUS2018_0-vs-HELIOS2018_1.rcl"
    with open(rcg_file) as file:
        rcg = RcgParser(file).rcg
    with open(rcl_file) as file:
        rcl = RclParser(file).rcl

    return rcg, rcl


def time_all_kick_filter(rcl, repetitions=1):
    from analysing_tools.extraction import kick_filter
    single_kicks_time = repeat(functools.partial(kick_filter.get_singular_kicks, rcl.kicks),
                               number=1, repeat=repetitions, globals=globals())
    single_tackles_time = repeat(functools.partial(kick_filter.get_singular_tackles, rcl.tackles),
                                 number=1, repeat=repetitions, globals=globals())

    print(f"single kicks time: {mean(single_kicks_time)}")
    print(f"single tackles time: {mean(single_tackles_time)}")


def time_all_player_reformat(rcg, repetitions=1):
    from analysing_tools.extraction import player_reformat

    order_time = repeat(functools.partial(player_reformat.get_player_list_ordered_by_time, rcg.players),
                        number=1, repeat=repetitions, globals=globals())

    order_time_fast = repeat(functools.partial(player_reformat.get_player_list_ordered_by_time_fast, rcg.players),
                             number=1, repeat=repetitions, globals=globals())

    print(f"player order time: {mean(order_time)}")
    print(f"player order time fast: {mean(order_time_fast)}")
    print(f"fast is : {mean(order_time) - mean(order_time_fast)} seconds faster")


def main():
    REPETISIONS = 100
    print("----------PARSING----------")
    rcg, rcl = parse_rcg_and_rcl()
    print("--------KICK_FILTER--------")
    time_all_kick_filter(rcl, REPETISIONS)
    print("-------PLAYER_REFORMAT-----")
    # temp_time(rcg, REPETISIONS)
    time_all_player_reformat(rcg, REPETISIONS)


if __name__ == '__main__':
    main()
