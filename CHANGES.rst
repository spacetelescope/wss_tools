1.2 (unreleased)
----------------

This requires Python 3.7 or later. [#74]

* Added ``--n-cores`` option for multiprocessing in downsampling images
  in ``THUMBNAIL`` mode. [#72]
* Default size of THUMBNAIL images has increased from 100 to 500. [#72]
* Fixed ``quip_activity_log.xsd`` so that it can validate
  ``quip_activity_log.xml`` properly. [#75]

1.1 (2020-02-03)
----------------

* New ``SegIDHelper`` plugin. [#47]
* Size of NIRCam SW images in Segment ID mode is now larger. [#47]
* New functionality to generate operation files. [#55]
* Infrastructure update in accordance to Astropy APE 17. [#65]

1.0 (2018-11-08)
----------------

Python 2 is no longer supported.

* Up the mosaic limit for saving using ``SaveImage``. [#41]

0.5 (2018-02-14)
----------------

This is the last release to support Python 2.

* Updated ``astropy_helpers`` to v2.0.5.
* Compatibility with Ginga 2.7 and ``stginga`` 0.3.

0.3 (2016-07-08)
----------------

First release of refactored QUIP that uses ``stginga`` and Ginga.
