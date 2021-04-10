#!/usr/bin/env python

# language=markdown
"""Filter and pretty-print aggregated query results

This reads aggregated query results from an intermediate file created by another tool,
applies simple filters as defined by the command line parameters, and pretty prints the
results. Since it works against previously created aggregations, it enables filters to
be quickly checked and adjusted when examining the results.
"""

import logging
import pathlib
import pickle
import sys

import lib

log = logging.getLogger(__name__)

DEFAULT_MIN_OCCURENCES = 0  # 10
DEFAULT_MIN_VALUES = 0  # 3
DEFAULT_MAX_LENGTH = 100  # 20
DEFAULT_TOP_VALUES = 100


def main():
    parser = lib.ArgumentParser(
        description=__doc__,
    )
    parser.add_argument(
        'pickle',
        help='Stats pickle file',
    )
    parser.add_argument(
        '--values',
        type=int,
        default=DEFAULT_MIN_VALUES,
        help='Only print elements with at least this number of unique values',
    )
    parser.add_argument(
        '--occurences',
        type=int,
        default=DEFAULT_MIN_OCCURENCES,
        help='Only print values with at least this number of occurences',
    )
    parser.add_argument(
        '--length',
        type=int,
        default=DEFAULT_MAX_LENGTH,
        help='Only print values that are shorter than this',
    )
    parser.add_argument(
        '--top',
        type=int,
        default=DEFAULT_TOP_VALUES,
        help='Only print the top N values for each element',
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Debug level logging',
    )
    args = parser.parse_args()

    logging.basicConfig(
        format='%(levelname)8s %(message)s',
        level=logging.DEBUG if args.debug else logging.INFO,
        stream=sys.stdout,
    )

    pickle_path = pathlib.Path(args.pickle)
    stats_dict = pickle.loads(pickle_path.read_bytes())

    lib.plog(
        stats_dict.get('__args', 'unk'),
        'Stats were genereated with params',
        log.debug,
    )

    try:
        del stats_dict['__args']
    except KeyError:
        pass

    lib.plog(stats_dict.keys(), 'Keys in stats dict', log.debug)

    # plog(stats_dict)

    def k(x):
        # print(x)
        return -x[1]

    for el_path, tag_dict in stats_dict.items():
        printed_count = 0
        if len(tag_dict) >= args.values:
            first = True
            for text_str, value_count in sorted(
                tag_dict['unique_count'].items(), key=k
            ):
                if value_count >= args.occurences and len(text_str) <= args.length:
                    if first:
                        log.debug('')
                        log.debug(f'{tag_dict["tag_count"]:8} {el_path}:')
                        first = False

                    log.debug(f'    {value_count:8} {text_str}')
                    printed_count += 1
                    if args.top > 0 and args.top == printed_count:
                        break
    return 0


if __name__ == '__main__':
    sys.exit(main())
