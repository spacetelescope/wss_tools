"""
Mosaic with option to highlight individual component.

**Plugin Type: Local**

``MosaicAuto`` is a local plugin, which means it is associated with a
channel. An instance can be opened for each channel.

**Usage**

.. note::

    When you are loading, say, hundreds of thumbnails, make sure they are all
    loaded in :ref:`ginga:sec-plugins-contents` first before clicking the
    "Create Mosaic" button.

This local plugin is only used in ``MOSAIC`` mode, as defined in
:ref:`quip-doc-ginga-files`; particularly, the ``THUMBNAIL`` operation type.

It is very much like
:ref:`MosaicAuto in stginga <stginga:local-plugin-mosaicauto>` except that
the image list associated with the selected footprint(s) is written out to
"QUIP Out" as given by the "QUIP Operation File".

"""
# STDLIB
import os

# STGINGA
from stginga.plugins.MosaicAuto import MosaicAuto as MosaicAutoParent

# LOCAL
from wss_tools.quip.main import QUIP_DIRECTIVE
from wss_tools.quip.qio import quip_out_dict
from wss_tools.utils.io import output_xml

__all__ = ['MosaicAuto']


class MosaicAuto(MosaicAutoParent):

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
                self.logger.error(f'{im} not found in operation file')
                ignored_list.append(im)

        images = sorted(set(keep_list))
        self.logger.info(f'Saving {outfile}')

        # Save QUIP out file XML
        try:
            output_xml(quip_out_dict(images=images), outfile)
        except OSError as e:
            s = str(e)
            self.logger.error(s)
            self.update_status('ERROR: ' + s)
            return

        if len(ignored_list) > 0:
            self.logger.info(f"Ignored {','.join(ignored_list)}")
            extra_msg = ', ignored file(s)'
        else:
            extra_msg = ''

        self.update_status('Image list saved' + extra_msg)


# Append module docstring with config doc for auto insert by Sphinx.
from ginga.util.toolbox import generate_cfg_example  # noqa
if __doc__ is not None:
    __doc__ += generate_cfg_example(
        'plugin_Mosaic', cfgpath='config', package='wss_tools.quip')
