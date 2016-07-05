.. include:: shared_text.txt

.. _quip-example-simple-analysis-1:

Example: "Simple Test"
======================

.. note:: |testdatawarn|

This example uses data in the "simple_test" directory. It demostrates typical
analysis situations that do not involve mosaic.

Copy test data to your own directory::

    $ cp -R /internal/data2/quip_data/simple_test /my/local/dir

Change directory to where your own test data are::

    $ cd /my/local/dir/simple_test/inputs

Fix the paths in XML file::

    $ sed 's/\/internal\/data2\/quip_data/\/my\/local\/dir/g' /internal/data2/quip_data/simple_test/inputs/operation_file_001.xml > operation_file_001.xml

Start QUIP (select optional arguments given in square brackets)::

    $ quip operation_file_001.xml [-g +300+150] [--nocopy] [--loglevel=10]

You can now use QUIP global and local plugins to analyze and modify the images
(also see :ref:`quip-doc-ginga-files`).
To save your changes and produce output files for WEx:

#. Click on :ref:`doc_savequip` global plugin tab.
#. Choose at least 1 image to keep/save.
#. Click the "Save" button. If there are no error messages, output
   files will be written.
#. |exitquip|

To see all available output files listing::

    $ ls /my/local/dir/simple_test/outputs

|gingadebuglog| To see Ginga log file::

    $ emacs /my/local/dir/simple_test/outputs/ginga.log
