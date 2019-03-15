.. _quip-example-opfile-gen-1:

Example: Generate QUIP Operation File
=====================================

When you are using QUIP outside of WEx, you might run into the situation
where you wish to manually generate your own QUIP Operation File.

The example below assumes the following directory structure with existing
data files::

    /my/path/
        inputs/
            image1.fits
            image2.fits

It also assumes the following desired outputs. The output *directory* will
be automatically created by the example below, if it does not yet exist.
While, the output *files* are to be created by QUIP itself, depending on what
you actually do in your session (not by the example here)::

    /my/path/
        quip/
            ginga.log
            image1_quip.fits
            R2017061401_quip_activity_log.xml
            R2017061401_quip_out.xml

To create a new QUIP Operation File in the same directory as input images, say,
for the use case of :ref:`quip-example-simple-analysis-1`:

>>> import glob
>>> import os
>>> from wss_tools.quip.qio import QUIPOpFile
>>> opfile = QUIPOpFile('ANALYSIS', '/my/path/quip')
>>> opfile.input_files = list(map(os.path.abspath, glob.iglob(
...     '/my/path/inputs/image*.fits')))
>>> opfile.input_files
['/my/path/inputs/image1.fits',
 '/my/path/inputs/image2.fits']
>>> opfile.write_xml('/my/path/inputs/operation_file_001.xml')

This would generate a QUIP Operation File that looks something like this::

    <?xml version="1.0" ?>
    <QUIP_OPERATION_FILE creator="QUIP" ...>
        <CORRECTION_ID>R2017061401</CORRECTION_ID>
        <OPERATION_TYPE>ANALYSIS</OPERATION_TYPE>
        <IMAGES>
            <IMAGE_PATH>/my/path/inputs/image1.fits</IMAGE_PATH>
            <IMAGE_PATH>/my/path/inputs/image2.fits</IMAGE_PATH>
        </IMAGES>
        <OUTPUT>
            <OUTPUT_DIRECTORY>/my/path/quip</OUTPUT_DIRECTORY>
            <LOG_FILE_PATH>/my/path/quip/R2017061401_quip_activity_log.xml</LOG_FILE_PATH>
            <OUT_FILE_PATH>/my/path/quip/R2017061401_quip_out.xml</OUT_FILE_PATH>
        </OUTPUT>
    </QUIP_OPERATION_FILE>

Once you have the QUIP Operation File, you can proceed to use QUIP like this::

    $ cd /my/path/inputs
    $ quip operation_file_001.xml
