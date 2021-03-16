#!/usr/bin/env python

# language=markdown
"""Create set of sample EML documents.

This creates a set of symlinks into a directory tree holding EML documents. The EML
documents to which the symlinks are created, are selected randomly from the full set of
docs available in the tree.

The directory in which the symlinks are created can then be used instead of the full
tree when it's sufficient to process only a randomly selected subset instead of the full
collection of EML docs.

The symlinks are created as relative if possible. Relative symlinks will not break if
they are in the same subtree, and the whole subtree is moved to another location.
"""
import logging
import os
import pathlib
import random
import sys

import _lib

THIS_PATH = pathlib.Path(__file__).parent.resolve()
DEFAULT_SAMPLE_COUNT = 100
DEFAULT_SAMPLE_ROOT_DIR = THIS_PATH / 'samples'


log = logging.getLogger(__name__)


def main():
    parser = _lib.ArgumentParser(
        description=__doc__,
    )
    parser.add_argument(
        '--sample-count',
        type=int,
        default=DEFAULT_SAMPLE_COUNT,
        help='Number of symlinks to create',
    )
    parser.add_argument(
        '--eml-root',
        metavar='path',
        type=pathlib.Path,
        default=_lib.DEFAULT_EML_ROOT_DIR,
        help="""Path to root of directory tree to search for EML docs 
            (extension must be \'.xml\')
        """,
    )
    parser.add_argument(
        '--sample-root',
        type=pathlib.Path,
        default=DEFAULT_SAMPLE_ROOT_DIR,
        help='Directory in which to create the symlinks. Created if it does not exist',
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

    if not args.sample_root.exists():
        args.sample_root.mkdir(parents=True)

    path_list = list(_lib.eml_path_gen(args.eml_root))
    log.info(f'All count: {len(path_list)}')
    sample_list = random.sample(path_list, args.sample_count)
    for src_path in sample_list:
        dst_path = args.sample_root / src_path.name

        if args.sample_root.is_relative_to(args.eml_root):
            dst_path = dst_path.relative_to(src_path)

        log.info(f'{dst_path} -> {src_path}')

        try:
            os.symlink(src_path, dst_path)
        except EnvironmentError as e:
            print(e)
            return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
