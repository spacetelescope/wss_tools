"""Module to handle I/O for files specific to QUIP."""

# STDLIB
import os
import warnings
import xml.etree.ElementTree as ET

# THIRD-PARTY
from astropy.utils.data import get_pkg_data_filename
from astropy.utils.xml.validate import validate_schema

# LOCAL
from ..utils.io import _etree_to_dict, _get_timestamp

__all__ = ['input_xml', 'validate_input_xml', 'QUIPOpFile',
           'validate_output_out_xml', 'validate_output_log_xml',
           'quip_out_dict', 'QUIPLog', 'QUIPLogEntry']


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


class QUIPOpFile:
    """Class to handle generation of QUIP Operation File.

    Parameters
    ----------
    op_type : {'MIMF', 'SEGMENT_ID', 'THUMBNAIL'}
        Operation type.

    outdir : str
        Output directory for the QUIP operation.
        This is used only for the population of the ``OUTPUT`` fields
        in the QUIP Operation File.

    correction_id : str
        Correction ID. Default value is arbitrary.

    create_outdir : bool
        Create the given ``outdir`` directory tree if it does not exist.

    Raises
    ------
    ValueError
        Invalid operation type.

    Examples
    --------
    Create a QUIP Operation File from scratch:

    >>> import glob
    >>> import os
    >>> from wss_tools.quip.qio import QUIPOpFile
    >>> opfile = QUIPOpFile('THUMBNAIL', '/my/path/quip')
    >>> opfile.input_files = list(map(os.path.abspath, glob.iglob('*.fits')))
    >>> opfile.write_xml('/my/path/opsfile/operation_file_001.xml')

    """
    def __init__(self, op_type, outdir, correction_id='R2017061401',
                 create_outdir=True):
        valid_op_types = ('MIMF', 'SEGMENT_ID', 'THUMBNAIL')

        if op_type not in valid_op_types:
            raise ValueError(
                f"Valid operation types: {','.join(valid_op_types)}")

        if create_outdir and not os.path.exists(outdir):
            os.makedirs(outdir)

        self.op_type = op_type
        self.outdir = os.path.abspath(outdir)
        self.correction_id = correction_id
        self.creation_time = _get_timestamp()
        self.quip_info = _get_quip_info()
        self._files = []

    @property
    def input_files(self):
        """List of input data filenames, with absolute paths."""
        return self._files

    @input_files.setter
    def input_files(self, filelist):
        if isinstance(filelist, str):
            filelist = [filelist]
        elif not isinstance(filelist, (list, tuple)):
            raise ValueError('input_files must be a str or list of str')

        self._files = []  # Reset

        for filename in filelist:
            # Too strict? Should we allow dummy filenames?
            if os.path.isfile(filename):
                self._files.append(filename)
            else:
                warnings.warn(f'Excluded {filename}; not a valid file',
                              UserWarning)

    def xml_dict(self):
        """Create a dictionary that can be converted to
        QUIP Operation File XML.

        Returns
        -------
        out_dict : dict
            Dictionary to be converted to XML by :meth:`write_xml`.

        """
        log_file_path = os.path.join(
            self.outdir, f'{self.correction_id}_quip_activity_log.xml')
        out_file_path = os.path.join(
            self.outdir, f'{self.correction_id}_quip_out.xml')

        d = {'@xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
             '@xsi:noNamespaceSchemaLocation': 'quip_operation_file.xsd'}
        d.update(self.creation_time)
        d.update(self.quip_info)
        d['CORRECTION_ID'] = self.correction_id
        d['OPERATION_TYPE'] = self.op_type
        d['IMAGES'] = {'IMAGE_PATH': self.input_files}
        d['OUTPUT'] = {'OUTPUT_DIRECTORY': self.outdir,
                       'LOG_FILE_PATH': log_file_path,
                       'OUT_FILE_PATH': out_file_path}

        return {'QUIP_OPERATION_FILE': d}

    def write_xml(self, filename):
        """Write the QUIP Operation File XML file.
        This is really just a convenience method that calls
        :func:`~wss_tools.utils.io.output_xml`.

        Parameters
        ----------
        filename : str
            Output XML file.

        Raises
        ------
        OSError
            Output file exists.

        """
        from ..utils.io import output_xml
        output_xml(self.xml_dict(), filename)


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


class QUIPLog:
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
            # en_d['ENTRY_DESCRIPTION'] = f'{en.imname}: {en_d['ENTRY_DESCRIPTION']}'  # noqa

            d['LOG_ENTRY'].append(en_d)

        return {'QUIP_ACTIVITY_LOG': d}


class QUIPLogEntry:
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
            raise ValueError(f'Invalid entry type ({etype}), must be one of '
                             f'{_valid_etypes}')
        self.imname = imname
        self.xml_dict = {
            'ENTRY_DESCRIPTION': descrip,
            'ENTRY_DATA': data,
            '@type': etype,
            '@date': date_str,
            '@time': time_str}
