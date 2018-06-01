"""Module to handle I/O for files specific to QUIP."""

# STDLIB
import os
import xml.etree.ElementTree as ET

# THIRD-PARTY
from astropy.utils.data import get_pkg_data_filename
from astropy.utils.xml.validate import validate_schema

# LOCAL
from ..utils.io import _etree_to_dict, _get_timestamp

__all__ = ['input_xml', 'validate_input_xml', 'validate_output_out_xml',
           'validate_output_log_xml', 'quip_out_dict', 'QUIPLog',
           'QUIPLogEntry']


def _validate_xml(filename, schema=''):
    """Validate XML against given schema using
    :func:`astropy.utils.xml.validate.validate_schema`.
    Schema must exist in package data.

    """
    schemafile = get_pkg_data_filename(os.path.join('data', schema))
    return validate_schema(filename, schemafile)


# -------------- #
# INPUT FROM WEx #
# -------------- #

def input_xml(filename):
    """Ingest input XML from WEx.

    Parameters
    ----------
    filename : str
        XML filename.

    Returns
    -------
    out_dict : dict
        XML structure converted to Python dictionary.

    """
    out_dict = _etree_to_dict(
        ET.parse(filename).getroot())['QUIP_OPERATION_FILE']
    images = out_dict['IMAGES']['IMAGE_PATH']
    if not isinstance(images, list):
        out_dict['IMAGES']['IMAGE_PATH'] = [images]
    return out_dict


def validate_input_xml(filename):
    """Validate schema for QUIP Operation File (``quip_operation_file.xsd``).
    """
    return _validate_xml(filename, schema='quip_operation_file.xsd')


# -------------- #
# OUTPUTS TO WEx #
# -------------- #

def validate_output_out_xml(filename):
    """Validate schema for QUIP Out File (``quip_out.xsd``)."""
    return _validate_xml(filename, schema='quip_out.xsd')


def validate_output_log_xml(filename):
    """Validate schema for QUIP Log File (``quip_activity_log.xsd``)."""
    return _validate_xml(filename, schema='quip_activity_log.xsd')


def _get_quip_info():
    """Return dictionary with QUIP metadata."""
    from .main import __taskname__, _operational  # Avoid circular import

    try:
        from ..version import version
    except ImportError:
        version = 'unknown'

    return {'@creator': __taskname__, '@version': version,
            '@operational': _operational}


def quip_out_dict(images=[]):
    """Create a dictionary that can be converted to QUIP Out XML.

    Parameters
    ----------
    images : list
        List of full path to output images.

    Returns
    -------
    out_dict : dict
        Dictionary to be converted to XML by
        :func:`~wss_tools.utils.io.output_xml`.

    """
    d = {'OUTPUT_IMAGES': {'IMAGE_PATH': images}}
    d.update(_get_timestamp())
    d.update(_get_quip_info())
    return {'QUIP_OUT': d}


class QUIPLog(object):
    """Class to handle QUIP actions to document in log file
    and image history.

    Attributes
    ----------
    creation_time : dict
        Metadata for when this object was created.

    quip_info : dict
        Metadata related to QUIP software.

    log_entries : list
        List of `QUIPLogEntry`.

    """
    def __init__(self):
        self.creation_time = _get_timestamp()
        self.quip_info = _get_quip_info()
        self.log_entries = []

    def add_entry(self, *args):
        """Add new `QUIPLogEntry`."""
        self.log_entries.append(QUIPLogEntry(*args))

    def xml_dict(self):
        """Create a dictionary that can be converted to QUIP Output Log XML.

        Returns
        -------
        out_dict : dict
            Dictionary to be converted to XML by
            :func:`~wss_tools.utils.io.output_xml`.

        """
        d = {'LOG_ENTRY': []}
        d.update(self.creation_time)
        d.update(self.quip_info)

        # Insert log entries
        for i, en in enumerate(self.log_entries, 1):
            en_d = {'@id': i}
            en_d.update(en.xml_dict)

            # DISABLED: Because description is now already the image name
            # en_d['ENTRY_DESCRIPTION'] = '{0}: {1}'.format(
            #     en.imname, en_d['ENTRY_DESCRIPTION'])

            d['LOG_ENTRY'].append(en_d)

        return {'QUIP_ACTIVITY_LOG': d}


class QUIPLogEntry(object):
    """Class to handle each log entry for `QUIPLog`.

    Parameters
    ----------
    date_str, time_str : str
        Timestamp for the entry.

    imname : str
        Image name the entry is associated to.

    descrip : str
        Short description.

    data : str
        Entry contents. Only single line supported for now.

    etype : {'status', 'warning', 'error', 'data'}
        Entry type.

    Attributes
    ----------
    imname
        Same as input.

    xml_dict : dict
        Dictionary for :meth:`QUIPLog.xml_dict`.

    Raises
    ------
    ValueError
        Invalid entry type.

    """
    def __init__(self, date_str, time_str, imname, descrip, data, etype):
        _valid_etypes = ('status', 'warning', 'error', 'data')

        if etype not in _valid_etypes:
            raise ValueError('Invalid entry type ({0}), must be one of '
                             '{1}'.format(etype, _valid_etypes))
        self.imname = imname
        self.xml_dict = {
            'ENTRY_DESCRIPTION': descrip,
            'ENTRY_DATA': data,
            '@type': etype,
            '@date': date_str,
            '@time': time_str}
