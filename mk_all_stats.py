#!/usr/bin/env python

"""Create a set of predefined aggregation files concurrently.

Configured directly in the source.
"""
import subprocess
import logging
import sys

import lib

STAT_TUP = (
    ('stats-datatable-only.pickle', './/dataTable'),
    ('stats-below-datatable.pickle', './/dataTable//*'),
    ('stats-below-attribute.pickle', './/attributeList/attribute//*'),
    ('stats-all-elements.pickle', './/*'),
)

log = logging.getLogger(__name__)


def main():
    parser = lib.ArgumentParser(
        description=__doc__,
    )
    parser.parse_args()

    for pickle_path, xpath_str in STAT_TUP:
        print(f'{pickle_path} {xpath_str}')

        cmd_list = [
            './mk_stats.py',
            pickle_path,
            xpath_str,
        ]
        subprocess.Popen(cmd_list, stdout=subprocess.PIPE)


if __name__ == '__main__':
    sys.exit(main())
