#!/usr/bin/env python

# language=markdown
"""Check EML type derivation algrithm performance.

This applies a type derivation procedure to all available EML docs and captures the
results. This can be used for checking current procedures or investigating new ones.
"""

import logging
import pathlib
import sys
import types

import eml_types
import eml_utils.lib as eml_lib
import eml_utils.util as util

THIS_PATH = pathlib.Path(__file__).parent.resolve()
SRC_ROOT_PATH = THIS_PATH / '___data'
# SRC_ROOT_PATH = THIS_PATH / '___samples'


log = logging.getLogger(__name__)


def main():
    parser = eml_lib.ArgumentParser(
        description=__doc__,
    )
    parser.add_argument(
        '--eml-root',
        metavar='path',
        type=pathlib.Path,
        default=SRC_ROOT_PATH,
        help="""Path to root of directory tree to search for EML docs 
            (extension must be \'.xml\')
        """,
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
    counter = util.Counter()

    try:
        proc_all(args.eml_root, counter)
    except eml_lib.EMLError as e:
        log.error(str(e))
        eml_lib.plog(e.xml_frag, 'EML fragment', log.error)
    except Exception:
        log.exception('Unhandled exception')

    return 0


def proc_all(eml_root_path, counter):
    for eml_path in eml_lib.eml_path_gen(eml_root_path):
        proc_eml(eml_path, counter)


def proc_eml(eml_path, counter):
    log.debug('-' * 100)
    log.debug(eml_path.as_posix())

    try:
        dt_list = eml_types.get_data_table_list(eml_path)
    except Exception as e:
        log.error(
            f'No dataTables in EML. Error="{repr(e)}". path="{eml_path.as_posix()}"'
        )
        return

    for dt_el in dt_list:
        type_list = eml_types.get_profiling_types(dt_el)
        counter.count('total_columns', '_TOTAL_COLUMNS', inc_int=len(type_list))
        counter.count('total_columns', '_TOTAL_CSV')

        for type_dict in type_list:
            # eml_lib.plog(type_dict, 'type_dict', log.info)
            type_dict = types.SimpleNamespace(**type_dict)
            # counter.count(id_str='', key=type_dict.attribute_name, detail_obj='')
            counter.count(id_str='', key=type_dict.type_str, detail_obj='')
            # counter.count(id_str='', key=type_dict.storage_type, detail_obj='')
            # counter.count(id_str='', key=type_dict.iso_date_format_str, detail_obj='')
            # counter.count(id_str='', key=type_dict.c_date_format_str, detail_obj='')
            # counter.count(id_str='', key=type_dict.number_type, detail_obj='')
            # counter.count(id_str='', key=type_dict.numeric_domain, detail_obj='')


if __name__ == '__main__':
    sys.exit(main())
