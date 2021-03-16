#!/usr/bin/env python

# language=markdown
"""Apply an XPath to an EML doc and list the matched elements.

This tool is based on lxml, which is also the library we use in the tool that generates
aggregates from the full collection of EML docs. Though XPath is standardized, there are
many versions of the spec, and each implementation has its own idiosyncrazies. Using
this (or another lxml based tool) should guarantee that the results match those obtained
by the aggregation tool, and so is a good way to create and check the queries before
using them in lengthy aggregations.
"""

import logging
import pathlib
import sys

import lxml.etree

import _lib

log = logging.getLogger(__name__)


def main():
    parser = _lib.ArgumentParser(
        description=__doc__,
    )
    parser.add_argument(
        'xpath',
        help='Selection for the elements to track',
    )
    parser.add_argument(
        'eml_path',
        metavar='path',
        help='Path to EML doc to which the xpath will be apply',
    )
    parser.add_argument(
        '--only-text',
        action='store_true',
        help='Only print elements which have text content',
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

    try:
        proc(args.xpath, pathlib.Path(args.eml_path), args.only_text)
    except _lib.EMLError as e:
        log.error(str(e))
        _lib.plog(e.xml_frag, 'EML fragment', log.error)
    except Exception:
        log.exception('Unhandled exception')

    return 0


def proc(xpath_str, eml_path, only_text):
    log.debug('-' * 100)
    log.debug(eml_path)

    root_el = _lib.get_eml_tree(eml_path)
    el_list = root_el.xpath(xpath_str)

    for el in el_list:
        if lxml.etree.iselement(el):
            if (not only_text) or el.is_text:
                text_str = (getattr(el, 'text', '') or '').strip()
                if (not only_text) or text_str:
                    tree = lxml.etree.ElementTree(root_el.getroot())
                    log.info(f'{tree.getelementpath(el)}: {text_str}')
        else:
            log.info(el)


if __name__ == '__main__':
    sys.exit(main())
