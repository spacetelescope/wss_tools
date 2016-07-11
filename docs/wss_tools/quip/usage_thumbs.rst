.. include:: shared_text.txt

.. _quip-example-thumbnail-1:

Example: Mosaic of Thumbnails
=============================

.. note:: |testdatawarn|

This example demonstrates a QUIP operation mode, ``THUMBNAIL``, that
specializes in displaying a mosaic of thumbnails based on their WCS values.
The mosaic does not account for detector distortions. If images overlap, the
newer image will cover the older one. The sole purpose of this mode is for
user to quickly look at which images to keep for the next processing step in
WEx. Like :ref:`Segment ID <quip-example-segid-1>`, auto-levels behavior is
turned off but it is irrelevant here.

Copy test data to your own directory::

    $ cp -R /internal/data2/quip_data/nircam_test /my/local/dir

Change directory to where your own test data are::

    $ cd /my/local/dir/nircam_test/inputs

Fix the paths in XML file::

    $ sed 's/\/internal\/data2\/quip_data/\/my\/local\/dir/g' /internal/data2/quip_data/nircam_test/inputs/operation_file_001.xml > operation_file_001.xml

Start QUIP (select optional arguments given in square brackets)::

    $ quip operation_file_001.xml [-g +300+150] [--nocopy] [--loglevel=10]

Behind the scenes, QUIP resizes the images to smaller thumbnails and save them
under a sub-directory named ``quipcache`` within the same directory as
the "QUIP Operation File".
The scaling is set to shrink to a width of 100 pixels, more or less.
If an image is already small enough, its thumbnail is *not* generated, but
rather QUIP would just use the original input image.
If thumbnails already exist from a previous run, they are *not* regenerated.

Due to all the pre-processing above, Ginga might take a few seconds to start
up. To create the mosaic and produce output file for WEx:

#. :ref:`doc_mosaicauto` local plugin should already be loaded for you.
   If you don't see it, click on the "Dialogs" tab. If it is not there, you
   will have to start it manually by looking for it under "Operation" menu,
   where all the loaded Ginga local plugins reside.
#. Click on "Create Mosaic" to create a mosaic from the thumbnail images based
   on their WCS values. When it is done, you will see the mosaic displayed.
#. Select one or more images from the list to highlight their footprints on the
   mosaic.
#. If you need to rescale the display, click on :ref:`ginga:sec-plugins-info`
   tab on the left, enter "Cut Low/High" values, and press "Cut Levels".
#. Once you have selected the images to keep, click "Save Selection" under the
   :ref:`doc_mosaicauto` plugin.
#. |exitquip|

To see all available output files listing::

    $ ls /my/local/dir/nircam_test/outputs

Note that "QUIP Out" XML file (i.e., the image list) will be generated.
There are no "QUIP Activity Log" XML file nor output FITS images because
modification of images are not allowed in this mode.

|gingadebuglog| To see Ginga log file::

    $ emacs /my/local/dir/nircam_test/outputs/ginga.log
