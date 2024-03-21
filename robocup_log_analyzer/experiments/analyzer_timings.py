import sys
sys.path.extend((['../']))

import functools
from analysing_tools.parser.rcg_parser import RcgParser
from analysing_tools.parser.rcl_parser import RclParser
from timeit import timeit


def parse_rcg_and_rcl():
    rcg_file = "../20180621130004-CYRUS2018_0-vs-HELIOS2018_1.rcg"
    rcl_file = "../20180621130004-CYRUS2018_0-vs-HELIOS2018_1.rcl"
    with open(rcg_file) as file:
        rcg = RcgParser(file).rcg
    with open(rcl_file) as file:
        rcl = RclParser(file).rcl

    return rcg, rcl


def time_all_analyzer(rcg, rcl, repetitions=1) -> None:
    from analysing_tools.analysis import analyzer

    tackle_time = timeit(functools.partial(analyzer.get_tackle_times, rcl.tackles, rcg.team1.name, rcg.team2.name),
                         number=repetitions, globals=globals())
    field_half_time = timeit(functools.partial(analyzer.analyze_ball_field_half_ratio, rcg.balls, rcg.team1.name,
                                               rcg.team2.name),
                             number=repetitions, globals=globals())
    ref_dec_time = timeit(functools.partial(analyzer.count_referee_decisions, rcl.decisions, rcg.team1.name,
                                            rcg.team2.name),
                          number=repetitions, globals=globals())
    possession_time = timeit(functools.partial(analyzer.analyze_possession_percentage, rcl.decisions, rcl.kicks,
                                               rcg.team1.name, rcg.team2.name),
                             number=repetitions, globals=globals())
    count_pass_time = timeit(functools.partial(analyzer.count_passes_and_missed_passes, rcl.kicks, rcg.team1.name,
                                               rcg.team2.name),
                             number=repetitions, globals=globals())
    dribbings_time = timeit(functools.partial(analyzer.count_successful_and_unsuccessful_dribblings, rcl.kicks,
                                              rcg.team1.name, rcg.team2.name),
                            number=repetitions, globals=globals())
    goals_time = timeit(functools.partial(analyzer.get_goals_per_half_and_timing, rcl.decisions, rcg.team1.name,
                                          rcg.team2.name),
                        number=repetitions, globals=globals())
    shots_time = timeit(functools.partial(analyzer.analyse_shot, rcl.kicks, rcg.balls, rcg.team1.name, rcg.team2.name),
                        number=repetitions, globals=globals())

    print(f"tackle time: {tackle_time}")
    print(f"field half time: {field_half_time}")
    print(f"referee decision time: {ref_dec_time}")
    print(f"possession time: {possession_time}")
    print(f"count passes time: {count_pass_time}")
    print(f"dribble time: {dribbings_time}")
    print(f"goals time: {goals_time}")
    print(f"shots time: {shots_time}")


def time_all_passes(rcg, rcl, repetitions=1) -> None:
    from analysing_tools.extraction import kick_filter
    from analysing_tools.analysis import passes

    single_kicks = kick_filter.get_singular_kicks(rcl.kicks)  # kick_filter.get_successful_kicks(rcl.kicks))
    single_tackles = kick_filter.get_singular_tackles(rcl.tackles)  # kick_filter.get_successful_tackles(rcl.tackles))

    prepare_kicks_time = timeit(functools.partial(kick_filter.get_singular_kicks, rcl.kicks),
                                number=repetitions, globals=globals())
    prepare_tackles_time = timeit(functools.partial(kick_filter.get_singular_tackles, rcl.tackles),
                                  number=repetitions, globals=globals())

    passes_time = timeit(functools.partial(passes.pass_chain, single_kicks, single_tackles, rcg.team1.name,
                                           rcg.team2.name),
                         number=repetitions, globals=globals())
    pass_chain_time = timeit(functools.partial(passes.count_passes, rcl.kicks, rcg.balls, rcg.team1.name,
                                               rcg.team2.name),
                             number=repetitions, globals=globals())

    print(f"prepare time: {prepare_kicks_time+ prepare_tackles_time}")
    print(f"count passes time: {passes_time}")
    print(f"pass chain time: {pass_chain_time}")


def time_all_dribblings(rcg, rcl, repetitions=1) -> None:
    timeit(0, number=repetitions, globals=globals())


# def time_offside(rcg, rcl, repetitions=1) -> None:
#     timeit(0, number=repetitions, globals=globals())

def pretty_header_values(header_words):
    symbol = '-'
    symbol_len = 10
    longest = max([len(w) for w in header_words])
    symbol_len += longest // 2
    return symbol, symbol_len


def pretty_header_string(header_word, symbol, symbol_len):
    half_word_len = len(header_word) // 2
    prefix_len = symbol_len - half_word_len
    suffix_len = symbol_len - half_word_len
    if suffix_len + prefix_len + len(header_word) < symbol_len * 2:
        suffix_len += 1
    elif suffix_len + prefix_len + len(header_word) > symbol_len * 2:
        prefix_len -= 1
    return f"{symbol * prefix_len}{header_word}{symbol * suffix_len}"


def main():
    symbol, symbol_len = pretty_header_values(["PARSING", "ANALYZER", "PASSES", "DRIBBLINGS", "OFFSIDE"])

    REPETISIONS = 100
    print(pretty_header_string("PARSING", symbol, symbol_len))
    rcg, rcl = parse_rcg_and_rcl()
    print(pretty_header_string("ANALYZER", symbol, symbol_len))
    time_all_analyzer(rcg, rcl, REPETISIONS)
    print(pretty_header_string("PASSES", symbol, symbol_len))
    time_all_passes(rcg, rcl, REPETISIONS)
    print(pretty_header_string("DRIBBLINGS", symbol, symbol_len))
    # time_all_dribblings(rcg, rcl, REPETISIONS)
    print(pretty_header_string("OFFSIDE", symbol, symbol_len))
    # time_offside(rcg, rcl, REPETISIONS)


if __name__ == '__main__':
    main()
