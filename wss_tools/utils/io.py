"""Module to handle I/O for files."""

# STDLIB
import os
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime
from xml.dom import minidom

__all__ = ['output_xml']


# --------------------- #
# GENERIC XML FUNCTIONS #
# --------------------- #

# https://stackoverflow.com/questions/7684333/converting-xml-to-dictionary-using-elementtree
def _etree_to_dict(t):
    """Convert XML element tree to dictionary."""
    d = {t.tag: {} if t.attrib else None}
    children = list(t)
    if children:
        dd = defaultdict(list)
        for dc in map(_etree_to_dict, children):
            for k, v in dc.items():
                dd[k].append(v)
        d = {t.tag: {k: v[0] if len(v) == 1 else v for k, v in dd.items()}}
    if t.attrib:
        d[t.tag].update(('@' + k, v) for k, v in t.attrib.items())
    if t.text:
        text = t.text.strip()
        if children or t.attrib:
            if text:
                d[t.tag]['#text'] = text
        else:
            d[t.tag] = text
    return d


# https://code.activestate.com/recipes/573463-converting-xml-to-dictionary-and-back/
def _dict_to_etree(parent, dictitem):
    """Convert dictionary to XML element tree."""
    assert not isinstance(dictitem, list)

    if isinstance(dictitem, dict):
        for (tag, child) in dictitem.items():
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


# https://stackoverflow.com/questions/17402323/use-xml-etree-elementtree-to-write-out-nicely-formatted-xml-files
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
        raise OSError(f'{filename} exists')

    with open(filename, 'w') as fout:
        fout.write(reparsed.toprettyxml(indent='    '))


# -------------- #
# OUTPUTS TO WEx #
# -------------- #

def _get_timestamp():
    """Return dictionary with UTC timestamp metadata."""
    d = datetime.utcnow()
    return {'@date': d.strftime('%Y-%m-%dZ'),
            '@time': d.strftime('%H:%M:%S.%fZ')}
