.. _quip-installation:

Installation
============

Anaconda is the recommended Python distribution for ``wss_tools``.
If you do not have it already,
`download Miniconda <https://docs.conda.io/en/latest/miniconda.html>`_ and install it
(Python 3.7+ only). The instructions below
assume you do *not* want ``wss_tools`` in your default Anaconda environment
(``base``), but if you do want it, you can skip the part where you create a
new ``conda`` environment.

In a Bash shell, create a new ``conda`` environment for ``wss_tools`` using
Python 3 and then switch to that environment
(skip this if you want to use default ``base`` environment, but using ``base``
is not recommended)::

    conda create -n wssenv python=3.8
    conda activate wssenv

In that same environment, install the following dependencies from the
``conda-forge`` channel::

    conda install astropy -c conda-forge
    conda install scipy -c conda-forge
    conda install pyqt -c conda-forge
    conda install matplotlib -c conda-forge
    conda install pillow -c conda-forge
    conda install ginga -c conda-forge
    conda install stginga -c conda-forge

.. warning::

    ``AboutQUIP`` and ``MosaicAuto`` are broken for Ginga 2.6.3,
    see https://github.com/spacetelescope/wss_tools/issues/25 .
    If you encounter this issue, use ``conda update ginga`` to update Ginga.

Now, you can install ``wss_tools`` using ``pip`` (there was a concious decision
not to include it in Anaconda nor PyPI)::

    pip install git+https://github.com/spacetelescope/wss_tools.git@master

If you wish to use ``wss_tools`` that is released instead of the development
version, replace ``@master`` with ``@<version>``, where ``<version>`` is the
desired release version.

Dependencies installed using ``conda install`` above can be updated from time
to time using ``conda update <packagename>`` command as needed. As for those
installed using ``pip``, use ``pip install <packagename> -U`` to upgrade to a
new version.

When you are done with ``wss_tools``, you can switch back to ``base`` Anaconda
environment by deactivating the ``wssenv`` environment (skip this if you are
using the default ``base`` environment)::

    conda deactivate
