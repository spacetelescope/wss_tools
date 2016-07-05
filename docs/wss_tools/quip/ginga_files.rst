.. include:: shared_text.txt

.. _quip-doc-ginga-files:

Ginga Configuration Files
=========================

.. warning:: |gingahomewarn|

To accomodate the different behaviors of QUIP based on the given operation
type (see :ref:`doc_using_quip`), Ginga configuration files are separated into
three categories below:

+--------+----------------------------------------------------------------+
|Category|Description                                                     |
+========+================================================================+
|ALL     |All operation types.                                            |
+--------+----------------------------------------------------------------+
|ANALYSIS|Non-mosaic operation types.                                     |
+--------+----------------------------------------------------------------+
|MOSAIC  |Operation types that involve mosaicking, i.e., ``THUMBNAIL`` and|
|        |``SEGMENT_ID``.                                                 |
+--------+----------------------------------------------------------------+

The table below lists
`custom Ginga configuration files <https://github.com/STScI-JWST/wss_tools/tree/master/wss_tools/quip/config>`_
that are installed installed and used by QUIP:

+----------------------------+--------+---------------------------------------+
|Filename                    |Category|Description                            |
+============================+========+=======================================+
|general.cfg                 |ALL     |Sets general behaviors, particularly   |
|                            |        |unlimited image cache size and certain |
|                            |        |header keywords. Also enables primary  |
|                            |        |header inheritance.                    |
+----------------------------+--------+---------------------------------------+
|channel_Image.cfg.normalmode|ANALYSIS|Sets default pan, zoom, and auto-levels|
+----------------------------+--------+behaviors. One of these will be copied |
|channel_Image.cfg.mosaicmode|MOSAIC  |to channel_Image.cfg on start up.      |
+----------------------------+--------+---------------------------------------+
|ginga_config.py.normalmode  |ANALYSIS|Starts any relevant global or local    |
+----------------------------+--------+plugin(s).                             |
|ginga_config.py.segment_id  |MOSAIC  |One of these will be copied to         |
|                            |        |ginga_config.py on start up.           |
|ginga_config.py.thumbnail   |        |                                       |
+----------------------------+--------+---------------------------------------+
|plugin_Contents.cfg         |ALL     |Customizes the associated global       |
|                            |        |plugin.                                |
|plugin_Thumbs.cfg           |        |                                       |
+----------------------------+--------+---------------------------------------+
|plugin_SaveImage.cfg        |ANALYSIS|Customizes SaveImage and               |
|                            |        |:ref:`doc_savequip` global plugins.    |
+----------------------------+--------+---------------------------------------+
|plugin_Cuts.cfg             |ALL     |Customizes the associated local plugin.|
|                            |        |                                       |
|plugin_FBrowser.cfg         |        |                                       |
+----------------------------+--------+---------------------------------------+
|plugin_Mosaic.cfg           |MOSAIC  |Customizes Mosaic and                  |
|                            |        |:ref:`doc_mosaicauto` local plugins.   |
+----------------------------+--------+---------------------------------------+
