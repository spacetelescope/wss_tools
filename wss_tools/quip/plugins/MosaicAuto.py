"""Automatic mosaic global plugin for QUIP."""
from __future__ import absolute_import, division, print_function

# STDLIB
import os

# GINGA
from ginga.util.toolbox import generate_cfg_example

# STGINGA
from stginga.plugins.MosaicAuto import MosaicAuto as MosaicAutoParent

# LOCAL
from wss_tools.quip.main import QUIP_DIRECTIVE
from wss_tools.quip.qio import quip_out_dict
from wss_tools.utils.io import output_xml

__all__ = []


class MosaicAuto(MosaicAutoParent):
    """Mosaic with option to highlight individual component."""

    def save_imlist(self):
        """Save selected image filename(s) to QUIP OUT XML only
        (no Activity Log).
        If no image selected, no output is generated.

        """
        if QUIP_DIRECTIVE is None:
            s = 'Invalid QUIP operation file!'
            self.logger.error(s)
            self.update_status(s)
            return

        imlist = self.get_selected_paths()

        if len(imlist) == 0:
            s = 'No image selected!'
            self.logger.error(s)
            self.update_status(s)
            return

        orig_images = QUIP_DIRECTIVE['IMAGES']['IMAGE_PATH']
        outfile = QUIP_DIRECTIVE['OUTPUT']['OUT_FILE_PATH']
        keep_list = []
        ignored_list = []

        # Get full path of images to keep and ensure uniqueness for images
        # with multiple mosaicked extensions.
        for im in imlist:
            basefname = os.path.basename(im)
            realpath = ''
            is_found = False

            # Get the path to actual input, not the shrunken version
            for orig_im in orig_images:
                if basefname in orig_im:
                    realpath = orig_im
                    is_found = True
                    break

            if is_found:
                keep_list.append(realpath)
            else:
                self.logger.error('{0} not found in operation file'.format(im))
                ignored_list.append(im)

        images = sorted(set(keep_list))
        self.logger.info('Saving {0}'.format(outfile))

        # Save QUIP out file XML
        try:
            output_xml(quip_out_dict(images=images), outfile)
        except OSError as e:
            s = str(e)
            self.logger.error(s)
            self.update_status('ERROR: ' + s)
            return

        if len(ignored_list) > 0:
            self.logger.info('Ignored {0}'.format(','.join(ignored_list)))
            extra_msg = ', ignored file(s)'
        else:
            extra_msg = ''

        self.update_status('Image list saved' + extra_msg)


# Replace module docstring with config doc for auto insert by Sphinx.
# In the future, if we need the real docstring, we can append instead of
# overwrite.
__doc__ = generate_cfg_example(
    'plugin_Mosaic', cfgpath='config', package='wss_tools.quip')
