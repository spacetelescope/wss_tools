"""Module to handle I/O for files."""
from __future__ import absolute_import, division, print_function

# STDLIB
import os
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime
from xml.dom import minidom

# THIRD-PARTY
from astropy.utils.data import get_pkg_data_filename
from astropy.utils.xml.validate import validate_schema

__all__ = ['output_xml', 'validate_xml']


# --------------------- #
# GENERIC XML FUNCTIONS #
# --------------------- #

# http://stackoverflow.com/questions/7684333/converting-xml-to-dictionary-using-elementtree
def _etree_to_dict(t):
    """Convert XML element tree to dictionary."""
    d = {t.tag: {} if t.attrib else None}
    children = list(t)
    if children:
        dd = defaultdict(list)
        for dc in map(_etree_to_dict, children):
            for k, v in dc.iteritems():
                dd[k].append(v)
        d = {t.tag: {k: v[0] if len(v) == 1 else v for k, v in dd.iteritems()}}
    if t.attrib:
        d[t.tag].update(('@' + k, v) for k, v in t.attrib.iteritems())
    if t.text:
        text = t.text.strip()
        if children or t.attrib:
            if text:
                d[t.tag]['#text'] = text
        else:
            d[t.tag] = text
    return d


# http://code.activestate.com/recipes/573463-converting-xml-to-dictionary-and-back/
def _dict_to_etree(parent, dictitem):
    """Convert dictionary to XML element tree."""
    assert not isinstance(dictitem, list)

    if isinstance(dictitem, dict):
        for (tag, child) in dictitem.iteritems():
            if str(tag) == '#text':
                parent.text = str(child)
            elif str(tag).startswith('@'):
                parent.attrib[str(tag)[1:]] = str(child)
            elif isinstance(child, list):
                # iterate through the array and convert
                for listchild in child:
                    elem = ET.Element(tag)
                    parent.append(elem)
                    _dict_to_etree(elem, listchild)
            else:
                elem = ET.Element(tag)
                parent.append(elem)
                _dict_to_etree(elem, child)
    else:
        parent.text = str(dictitem)


# http://stackoverflow.com/questions/17402323/use-xml-etree-elementtree-to-write-out-nicely-formatted-xml-files
def output_xml(xmldict, filename):
    """Write given dictionary to XML.

    Parameters
    ----------
    xmldict : dict
        Dictionary to be converted.

    filename : str
        Output XML file.

    Raises
    ------
    OSError
        Output file exists.

    """
    roottag = list(xmldict)[0]
    root = ET.Element(roottag)
    _dict_to_etree(root, xmldict[roottag])

    rough_string = ET.tostring(root, 'utf-8')
    reparsed = minidom.parseString(rough_string)

    if os.path.exists(filename):
        raise OSError('{0} exists'.format(filename))

    with open(filename, 'w') as fout:
        fout.write(reparsed.toprettyxml(indent='    '))


def validate_xml(filename, schema=''):
    """Validate XML against given schema using
    :func:`astropy.utils.xml.validate.validate_schema`.
    Schema must exist in package data.

    """
    schemafile = get_pkg_data_filename(os.path.join('data', schema))
    return validate_schema(filename, schemafile)


# -------------- #
# OUTPUTS TO WEx #
# -------------- #

def _get_timestamp():
    """Return dictionary with UTC timestamp metadata."""
    d = datetime.utcnow()
    return {'@date': d.strftime('%Y-%m-%dZ'),
            '@time': d.strftime('%H:%M:%S.%fZ')}
