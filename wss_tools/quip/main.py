"""QUIP driver.

The main program takes QUIP Operation XML file from WEx.
Then, it starts Ginga with custom plugins.
For more information, see :ref:`running-quip-doc`.

"""
# STDLIB
import glob
import multiprocessing
import os
import platform
import shutil
import sys
from functools import partial

# THIRD-PARTY
from astropy.io import fits
from astropy.utils.data import get_pkg_data_filenames

# GINGA and STGINGA
from ginga.rv import main as gmain
from ginga.misc.Bunch import Bunch
from stginga.utils import scale_image

# LOCAL
from . import qio

# Suppress logging "no handlers" message from Ginga
import logging
logging.raiseExceptions = False
try:
    logging.lastResort = None
except AttributeError:
    pass

__all__ = ['main', 'get_ginga_plugins', 'copy_ginga_files', 'set_ginga_config',
           'shrink_input_images']
__taskname__ = 'QUIP'
_operational = 'false'  # 'true' or 'false'
_tempdirname = 'quipcache'  # Sub-dir to store temporary intermediate files
_iswin = platform.system() == 'Windows'
_home = None
QUIP_DIRECTIVE = None  # Store info from input XML
QUIP_LOG = None  # Store info for output log XML

# Set HOME directory
if 'HOME' in os.environ:
    _home = os.environ['HOME']
elif _iswin:
    _home = os.path.join(os.environ['HOMEDRIVE'], os.environ['HOMEPATH'])
else:
    raise ValueError('Cannot find HOME directory')


def main(args):
    """Driver for command line script.

    First argument must be the QUIP Operation XML file.
    Other command line options are as accepted by Ginga, *except* for:

    * ``--mosaic-thumb-size`` can be used to specify desired width in pixels
      for individual images to be mosaicked in ``THUMBNAIL`` mode.
      If not given, the default width is 500 pixels. For Segment ID,
      the value is 256 regardless of this setting.
    * ``--n-cores`` can be used to specify the number of CPU cores used when
      rescaling images in ``THUMBNAIL`` mode. If not given, all available
      cores will be used.
    * ``--nocopy`` can be used with QUIP to instruct
      it to *not* copy its Ginga files to user's HOME directory.
    * ``--log=filename``, if given in command line, will be ignored
      because QUIP always writes Ginga's log to ``ginga.log`` in the
      output directory provided by QUIP Operation XML file.

    Parameters
    ----------
    args : list of str
        Command line arguments.

    Raises
    ------
    OSError
        Input XML does not exist.

    ValueError
        Input XML fails to validate built-in schema.
        Validation is skipped for Windows.

    """
    from stginga.gingawrapper import _locate_plugin
    global QUIP_DIRECTIVE, QUIP_LOG

    inputxml = args.pop(0)

    if not os.path.exists(inputxml):
        raise OSError('{0} does not exist'.format(inputxml))

    # Validate input XML (compare return code and display stderr if fails).
    # Skipped for Windows because no xmllint.
    if not _iswin:
        schema_v = qio.validate_input_xml(inputxml)
        if schema_v[0] != 0:
            raise ValueError(schema_v[2])

    if '--nocopy' in args:
        nocopy = True
        args.pop(args.index('--nocopy'))
    else:
        nocopy = False

    # Copy Ginga files to HOME directory
    if not nocopy:
        copy_ginga_files()

    thumb_width = 500
    n_cores = None

    for i, a in enumerate(args):
        # Ignore any custom log file provided by user
        if a.startswith('--log='):
            args.pop(i)
        # Custom width for THUMBNAIL mode
        elif a.startswith('--mosaic-thumb-size='):
            args.pop(i)
            try:
                thumb_width = int(a.split('=')[1])
            except Exception:
                pass  # Use default
        # Num cores for THUMBNAIL mode
        elif a.startswith('--n-cores='):
            args.pop(i)
            try:
                n_cores = int(a.split('=')[1])
            except Exception:
                pass  # Use default

    # Extract info from input XML
    QUIP_DIRECTIVE = qio.input_xml(inputxml)
    gingalog = os.path.join(
        QUIP_DIRECTIVE['OUTPUT']['OUTPUT_DIRECTORY'], 'ginga.log')
    images = QUIP_DIRECTIVE['IMAGES']['IMAGE_PATH']
    op_type = QUIP_DIRECTIVE['OPERATION_TYPE'].lower()

    # Create hidden temporary directory, in case we need it later.
    # This is NOT automatically deleted.
    tempdir = os.path.join(
        os.path.dirname(os.path.abspath(inputxml)), _tempdirname)
    if not os.path.exists(tempdir):
        os.mkdir(tempdir)

    # Initialize info for log XML.
    # Do this here for time stamp and avoid circular import.
    QUIP_LOG = qio.QUIPLog()

    # No point keeping Ginga log from last run
    if os.path.exists(gingalog):
        os.remove(gingalog)

    if op_type == 'thumbnail':
        cfgmode = 'mosaicmode'
        ginga_config_py_sfx = op_type
        sci_ext = ('SCI', 1)

        # Science array can have different EXTNAME values:
        #   SCI (JWST/HST) or IMAGE (test)
        # Assume first image is representative of all the rest.
        with fits.open(images[0]) as pf:
            if sci_ext not in pf:
                sci_ext = ('IMAGE', 1)

        # Auto guess the number of CPU cores needed.
        if n_cores is None:
            n_cores = min(multiprocessing.cpu_count(), len(images))

        images = shrink_input_images(
            images, ext=sci_ext, new_width=thumb_width, n_cores=n_cores,
            outpath=tempdir)

    elif op_type == 'segment_id':
        cfgmode = 'mosaicmode'
        ginga_config_py_sfx = op_type
        images = _segid_mosaics(images, outpath=tempdir, sw_sca_size=256)

    else:  # different kinds of analysis
        cfgmode = 'normalmode'
        ginga_config_py_sfx = cfgmode

    # Add custom plugins.
    # NOTE: There was a bug with setting this in ginga_config.py,
    #       so we do this here instead.
    global_plugins, local_plugins = get_ginga_plugins(ginga_config_py_sfx)
    gmain.plugins += global_plugins
    gmain.plugins += local_plugins

    # Set Ginga config file(s)
    set_ginga_config(mode=cfgmode, gcfg_suffix=ginga_config_py_sfx)

    # Auto start core global plugins
    for gplgname in ('ChangeHistory', ):
        gplg = _locate_plugin(gmain.plugins, gplgname)
        gplg.start = True

    # Start Ginga
    sys_args = ['ginga', '--log={0}'.format(gingalog)] + args + images
    gmain.reference_viewer(sys_args)


def get_ginga_plugins(op_type):
    """Obtain relevant custom plugins from ``stginga`` and ``wss_tools``
    for the given QUIP operation type.

    Parameters
    ----------
    op_type : {'normalmode', 'segment_id', 'thumbnail'}
        QUIP operation type. Normal mode covers anything that is
        neither SEGMENT_ID nor THUMBNAIL.

    Returns
    -------
    global_plugins : list
        List of custom Ginga global plugins to load.

    local_plugins : list
        List of custom Ginga local plugins to load.

    """
    stg_pfx = 'stginga.plugins'
    wss_pfx = 'wss_tools.quip.plugins'
    global_plugins = [
        Bunch(module='AboutQUIP', tab='AboutQUIP', workspace='left',
              category='Custom', ptype='global', pfx=wss_pfx)]

    if op_type == 'segment_id':
        local_plugins = []
        # Add special plugin for segment ID annotations
        global_plugins += [
            Bunch(module='SegIDHelper', tab='SegIDHelper', workspace='left',
                  category='Custom', ptype='global', pfx=wss_pfx)]
    elif op_type == 'thumbnail':
        local_plugins = [
            Bunch(module='MosaicAuto', workspace='dialogs',
                  category='Custom', ptype='local', pfx=wss_pfx)]
    else:  # normalmode
        global_plugins += [
            Bunch(module='SaveQUIP', tab='SaveQUIP', workspace='right',
                  category='Custom', ptype='global', pfx=wss_pfx)]
        local_plugins = [
            Bunch(module='BackgroundSub', workspace='dialogs',
                  category='Custom', ptype='local', pfx=stg_pfx),
            Bunch(module='BadPixCorr', workspace='dialogs',
                  category='Custom', ptype='local', pfx=stg_pfx),
            Bunch(module='DQInspect', workspace='dialogs',
                  category='Custom', ptype='local', pfx=stg_pfx),
            Bunch(module='SNRCalc', workspace='dialogs',
                  category='Custom', ptype='local', pfx=wss_pfx)]

    return global_plugins, local_plugins


def _do_copy(src, dst, verbose=False):
    """Copy file."""
    if os.path.exists(dst):
        os.remove(dst)
    shutil.copyfile(src, dst)
    if verbose:
        print(src, '->', dst)


def copy_ginga_files(verbose=False):
    """Copy Ginga configuration files to HOME directory.

    Parameters
    ----------
    verbose : bool
        Print info to screen.

    """
    # NOTE: There is no need to copy plugins here anymore.
    #
    # Copy configuration files.
    dstpath = os.path.join(_home, '.ginga')
    if not os.path.exists(dstpath):
        os.makedirs(dstpath)
    for filename in get_pkg_data_filenames('config', pattern='*.*'):
        _do_copy(filename, os.path.join(dstpath, os.path.basename(filename)),
                 verbose=verbose)


def set_ginga_config(mode='normalmode', gcfg_suffix='normalmode',
                     verbose=False):
    """Replace Ginga files in HOME directory with the
    appropriate version for the given mode.

    This must be run *after* :func:`copy_ginga_files`, not before.
    For a list of affected configuration files, see
    :ref:`quip-doc-ginga-files`.

    "normalmode" is set such that all images are always in cache.
    This is useful if you want to do background subtraction etc.
    in Ginga. However, it is not sustainable if there are too many
    images opened at the same time. The auto-levels behavior is
    same as Ginga default.

    "mosaicmode" is designed such that only certain number of images
    will be processed, although all images are still always cached.
    As a result, it is prone to memory problem if run in "normalmode".
    The auto-levels behavior is disabled by default to allow
    blinking the images all at the same scale.

    Parameters
    ----------
    mode : {'normalmode', 'mosaicmode'}
        Mode of analysis.

    gcfg_suffix : {'normalmode', 'thumbnail', 'segment_id'}
        Associated ``ginga_config.py`` to use. This is slightly
        different from ``mode`` because "mosaicmode" can have
        different requirements depending on operation type.

    verbose : bool
        Print info to screen.

    """
    path = os.path.join(_home, '.ginga')

    # Copy ginga_config.py
    sfx = '.' + gcfg_suffix
    src = os.path.join(path, 'ginga_config.py' + sfx)
    _do_copy(src, src.replace(sfx, ''), verbose=verbose)

    # Copy other Ginga files
    sfx = '.' + mode
    for src in glob.iglob(os.path.join(path, '*' + sfx)):
        _do_copy(src, src.replace(sfx, ''), verbose=verbose)


# Iterable (infile) must be last argument.
def _shrink_one(outpath, ext, new_width, debug, kwargs, infile):
    with fits.open(infile) as pf:
        old_width = pf[ext].data.shape[1]  # (ny, nx)

    # Shrink it.
    if old_width > new_width:
        path, fname = os.path.split(infile)

        # Skipping instead of just returning the input image
        # because want to avoid mosaicking large images.
        if os.path.abspath(path) == outpath:
            print('Input and output directories are the same: '
                  '{0}; Skipping {1}'.format(outpath, fname))
            outfile = ''
        else:
            outfile = os.path.join(outpath, fname)
            zoom_factor = new_width / old_width
            scale_image(infile, outfile, zoom_factor, **kwargs)

    # Input already small enough.
    else:
        outfile = infile
        if debug:
            print('{0} has width {1} <= {2}; Using input '
                  'file'.format(infile, old_width, new_width))

    return outfile


def shrink_input_images(images, outpath='', new_width=500, n_cores=1,
                        **kwargs):
    """Shrink input images for mosaic, if necessary.

    The shrunken images are not deleted on exit;
    User has to remove them manually.

    Parameters
    ----------
    images : list
        List of input image files.

    outpath : str
        Output directory. This must be different from input
        directory because image names remain the same.

    new_width : int
        Width of the shrunken image. Height will be scaled accordingly.
        Because this will be converted into a zoom factor for
        :func:`~stginga.utils.scale_image`, requested width might not
        be the exact one that you get but should be close.

    n_cores : int
        Number of CPU cores to use.

    kwargs : dict
        Optional keywords for :func:`~stginga.utils.scale_image`.

    Returns
    -------
    outlist : list
        List of images to use. If shrunken, the list will include
        the new image in the ``outpath`` (same filename).
        If the input is already small enough, shrinking process is
        skipped and the list will contain the input image instead.

    """
    outpath = os.path.abspath(outpath)
    debug = kwargs.get('debug', False)

    # Use same extension as scale image.
    if 'ext' in kwargs:
        ext = kwargs['ext']
    else:
        ext = ('SCI', 1)
        kwargs['ext'] = ext

    func = partial(_shrink_one, outpath, ext, new_width, debug, kwargs)

    if n_cores < 2:  # No multiprocessing
        outlist = [s for s in map(func, images) if s]
    else:
        with multiprocessing.Pool(n_cores) as p:
            result = p.map(func, images)
        outlist = [s for s in result if s]

    return outlist


def _segid_mosaics(images, sw_sca_size=256, **kwargs):
    """Generate a scaled-down NIRCam mosaic for each exposure.

    The mosaics are not deleted on exit;
    User has to remove them manually.

    Parameters
    ----------
    images : list
        List of input image files.

    kwargs
        See :meth:`~wss_tools.utils.mosaic.NircamMosaic.make_mosaic`.

    Returns
    -------
    thumbnails : list
        List of scaled-down mosaics in output directory.

    """
    from ..utils.mosaic import NircamMosaic
    m = NircamMosaic(sw_sca_size=sw_sca_size)
    return m.make_mosaic(images, **kwargs)


def _main():
    """Run from command line."""
    if len(sys.argv) <= 1:
        print('USAGE: quip operation_file.xml [--mosaic-thumb-size=500] '
              '[--n-cores=8] [--nocopy] [--help]')
    elif '--help' in sys.argv:
        from ginga.rv.main import reference_viewer
        reference_viewer(['ginga', '--help'])
    elif '--version' in sys.argv:
        try:
            from ..version import version
        except ImportError:
            version = 'unknown'
        print('{0} v{1}'.format(__taskname__, version))
    else:
        main(sys.argv[1:])
