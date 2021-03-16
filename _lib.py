"""Functions shared by the EML utilities
"""
import argparse
import io
import logging
import os
import pathlib
import pprint
import sys

import lxml.etree

block_set = set()

log = logging.getLogger(__name__)

# Max number of unique values we allow for the contents of an element before we no longer
# consider it to be a possible limited vocabulary, and stop tracking it.
MAX_VOCABULARY = 200


THIS_PATH = pathlib.Path(__file__).parent.resolve()
DEFAULT_EML_ROOT_DIR = THIS_PATH / '__all_eml'


class _HelpFormatter(
    argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter
):
    pass


class ArgumentParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super(ArgumentParser, self).__init__(
            formatter_class=_HelpFormatter,
            *args,
            **kwargs,
        )


def eml_path_gen(root_path):
    """Yield paths to all *.eml files under {root_path}"""
    file_count = 0
    for root_path, dir_list, file_list in os.walk(root_path):
        for file_name in file_list:
            file_path = pathlib.Path(root_path, file_name)
            if file_path.suffix == ".xml":
                yield file_path
                file_count += 1
                if not file_count % 100:
                    print(f"Processed EML files: {file_count}", file=sys.stderr)


def get_element_dict(frag_el):
    """Return a dict of elements to text contents. Includes all elements that contain
    text and are below the {frag_el} in the DOM."""
    d = {}
    for el in frag_el.xpath(".//*"):
        text = first(el, "text()")
        if text is not None:
            text = text.strip()
            if text:
                d.setdefault(el.tag, dict()).setdefault(text, 0)
                d[el.tag][text] += 1
    return d


def get_eml_tree(eml_path):
    return lxml.etree.parse(eml_path.as_posix())


def first(el, xpath):
    """Return the first match to the xpath if there was a match, else None. Can this be
    done directly in xpath 1.0?
    """
    res_el = el.xpath(f"({xpath})[1]")
    try:
        res_str = res_el[0]
    except IndexError:
        res_str = None
    # log.debug(f"first() -> {res_str}")
    return res_str


def has(el, xpath):
    return first(el, xpath) is not None


def pretty_format_fragment(root_el):
    if not isinstance(root_el, list):
        root_el = [root_el]
    buf = io.BytesIO()
    for e in root_el:
        # e.xpath("//*[local-name() = 'Body']")
        buf.write(lxml.etree.tostring(e, pretty_print=True))
    return buf.getvalue().decode("utf-8")


def merge_dict_set(dst_d, src_d):
    for el_name, text_dict in src_d.items():
        if el_name not in block_set:
            for text, count in text_dict.items():
                d = dst_d.setdefault(el_name, dict())
                d.setdefault(text, 0)
                d[text] += count
            if len(dst_d[el_name]) > MAX_VOCABULARY:
                plog(
                    {
                        "el_name": el_name,
                        "unique": len(dst_d),
                    },
                    "Exceeded MAX_VOCABULARY",
                    log.debug,
                )
                del dst_d[el_name]
                block_set.add(el_name)


def plog(obj, msg=None, logger=log.info):
    if lxml.etree.iselement(obj):
        obj_str = pretty_format_fragment(obj)
    else:
        obj_str = pprint.pformat(obj)
    logger("-" * 100)
    if msg:
        logger(f"{msg}:")
    tuple(
        map(logger, tuple(f"  {line}" for line in obj_str.splitlines())),
    )
    logger("")


def xpath(root_el, path_str, full_path=False):
    if not path_str.startswith(".//"):
        path_str = ".//" + path_str
    el_list = root_el.xpath(path_str)
    if full_path:
        el_list = [(el, get_el_path(root_el.getroot(), el)) for el in el_list]
    return el_list


def get_dt_filename(dt_el):
    return first(dt_el, ".//physical/objectName/text()")


def get_el_path(root_el, el):
    tree = lxml.etree.ElementTree(root_el)
    return tree.getelementpath(el)


class EMLError(Exception):
    def __init__(self, msg, xml_frag=None):
        self.xml_frag = xml_frag
        super(EMLError, self).__init__(msg)
