#!/usr/bin/env python

# language=markdown
"""Create an intermediate file containing statistics for a collection of EML docs.

The tool applies an XPath to each of the EML docs in the collection and generates some
basic aggregates, including the unique strings and counts of occurences for each of the
matched elements. The result is written to an intermedia file which is used later by
another tool to further filter the data and print final results.

As the intermediate file is expensive to create for large collections of EML doc, we
store it with the utilities themselves, instead of in /tmp (which is not persistent
across reboots).
"""

import logging
import pathlib
import pickle
import sys
import time

import _lib

THIS_PATH = pathlib.Path(__file__).parent.resolve()

log = logging.getLogger(__name__)


def main():
    parser = _lib.ArgumentParser(
        description=__doc__,
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
        'pickle',
        default='stats.pickle',
        help='Stats pickle file',
    )
    parser.add_argument(
        'xpath',
        help='Selection for the elements to track',
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

    args = parser.parse_args()
    start_ts = time.time()

    try:
        result_dict = proc_all(args.eml_root, args.xpath)
    except _lib.EMLError as e:
        log.error(str(e))
        _lib.plog(e.xml_frag, 'EML fragment', log.error)
    except Exception:
        log.exception('Unhandled exception')
    else:
        pickle_path = pathlib.Path(args.pickle).with_suffix('.pickle')
        result_dict['__args'] = vars(args)
        pickle_path.write_bytes(pickle.dumps(result_dict))
        log.info(f'Wrote statistics to {pickle_path.as_posix()}')

        m, s = divmod(time.time() - start_ts, 60)
        log.info(f'Elapsed: {int(m)}m {int(s)}s')

    return 0


def proc_all(eml_root_path, root_xpath):
    dst_el_dict = {}

    for eml_path in _lib.eml_path_gen(eml_root_path):
        proc_eml(eml_path, root_xpath, dst_el_dict)
        # shared.merge_dict_set(dst_el_dict, el_dict)

    return dst_el_dict


def proc_eml(eml_path, root_xpath, dst_el_dict):
    log.debug('-' * 100)
    log.debug(eml_path)

    root_el = _lib.get_eml_tree(eml_path)
    el_list = _lib.xpath(root_el, root_xpath, full_path=True)

    for el, el_path in el_list:
        text = (getattr(el, 'text', '') or '').strip()
        # if text or :
        # log.debug(f'url: {shared.get_dt_url(el)}')
        # log.debug(f'filename: {shared.get_dt_filename(el)}')

        # el_dict = shared.get_element_dict(el)
        # shared.merge_dict_set(D, el_dict)
        #     el = shared.get_el(el)
        el = el.tag
        dst_el_dict.setdefault(el, {'tag_count': 0, 'unique_count': {}})
        dst_el_dict[el]['unique_count'].setdefault(text, 0)
        dst_el_dict[el]['tag_count'] += 1
        dst_el_dict[el]['unique_count'][text] += 1

    # return D


if __name__ == '__main__':
    sys.exit(main())
