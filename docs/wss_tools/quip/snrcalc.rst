.. _doc_snrcalc:

SNRCalc
=======

This local plugin is only used in ``ANALYSIS`` mode, as defined in
:ref:`quip-doc-ginga-files`.

It is very much like :ref:`SNRCalc in stginga <stginga:local-plugin-snrcalc>`
except that SBR lower limits are customized based on QUIP operation type
("Stage Name") in use, as tabulated below. The limits are used to determine
whether the image being analyzed is acceptable. These numbers are
subject to change:

.. image:: images/sbr_limits_20150519.png
    :width: 600 px
    :alt: SBR lower limits
