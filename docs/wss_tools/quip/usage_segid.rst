.. include:: shared_text.txt

.. _quip-example-segid-1:

Example: Segment ID
===================

.. note:: |testdatawarn|

This example demonstrates a QUIP operation mode, ``SEGMENT_ID``, that
specializes in displaying each NIRCam mosaic separately so they can be compared
by blinking on the display. As described by Marshall Perrin, *"The user can
quickly page through the 19 NIRCam mosaics and see 'OK, so this blob in SCA A2
changed position when we moved segment 10, and this other blob in SCA B4
changed position when we moved segment 12'."*

The mosaic uses thumbnails similar to
:ref:`Mosaic of Thumbnails <quip-example-thumbnail-1>` but each mosaic only
holds images from different detectors of the same exposure.
All the input images are expected to advance to the next step in WEx;
Therefore, QUIP will not produce any output files.
To aid the blinking, Ginga's auto-levels behavior is turned off.

Copy test data to your own directory::

    $ cp -R /internal/data2/quip_data/segid_test /my/local/dir

Change directory to where your own test data are::

    $ cd /my/local/dir/segid_test/inputs

Fix the paths in XML file::

    $ sed 's/\/internal\/data2\/quip_data/\/my\/local\/dir/g' /internal/data2/quip_data/segid_test/inputs/operation_file_001.xml > operation_file_001.xml

Start QUIP (select optional arguments given in square brackets)::

    $ quip operation_file_001.xml [-g +300+150] [--nocopy] [--loglevel=10]

Behind the scenes, for each exposure, QUIP creates a scaled-down NIRCam mosaic
from all the detectors using `~wss_tools.utils.mosaic.NircamMosaic`.
Each exposure is grouped by the same file prefix, assuming
`standard JWST naming convention <https://confluence.stsci.edu/download/attachments/40187238/DMS_Level_1_and_2_Data_Product_Design_120706.pdf>`_.
The scaling is set such that each NIRCam SW exposure is 100 pixels.
The mosaics are saved under a hidden sub-directory named ``.quipcache`` within
the same directory as the "QUIP Operation File".
If mosaics already exist from a previous run, they are *not* regenerated.

Due to all the pre-processing above, Ginga might take a few seconds to start
up. But when it does, you will see the mosaics displayed. To inspect the
mosaics:

#. Blink them using the green up and down arrow icons (bottom left).
   Another option is to use the  :ref:`ginga:sec-plugins-blink` local plugin.
   You can also use :ref:`ginga:sec-plugins-thumbs` or
   :ref:`ginga:sec-plugins-contents` global plugins by clicking on the desired
   image thumbnail or name.
#. If you need to rescale the display, click on :ref:`ginga:sec-plugins-info`
   tab on the left, enter "Cut Low/High" values, and press "Cut Levels".
   Scaling is fixed for all images.
#. |exitquip|

Note that no XML or FITS file will be generated. This is because shortlisting
and modification of images are not allowed in this mode.

|gingadebuglog| To see Ginga log file::

    $ emacs /my/local/dir/segid_test/outputs/ginga.log
