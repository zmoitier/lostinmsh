.. https://sphinx-tutorial.readthedocs.io/cheatsheet/

Welcome to lostinmsh's documentation!
=====================================

The Python toolbox ``lostinmsh`` (*LOcally STructured polygonal INterface MeSH*), is a package using GMSH to construct locally structured triangular meshes of polygons which are useful for sign changing PDE problem.

**Camille Cavalho**
    *Univ Lyon, INSA Lyon, UJM, UCBL, ECL, CNRS UMR 5208, ICJ, F-69621, France*

    *Department of Applied Mathematics, University of California Merced, 5200 North Lake Road, Merced, CA 95343, USA*

**Zoïs Moitier**
    *IDEFIX, Inria, ENSTA Paris, Institut Polytechnique de Paris, 91120 Palaiseau, France*

Installation
------------

Use `pip <https://pip.pypa.io/en/stable/>`_

.. code-block:: shell

       $ pip install lostinmsh

or clone the repository

.. code-block:: shell

       $ git clone https://github.com/zmoitier/lostinmsh.git

and then you can locally install it via `flit <https://flit.pypa.io/en/stable/>`_

.. code-block:: shell

       $ flit install --symlink


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   examples
   user_interface


.. Indices and tables
.. ==================

.. * :ref:`genindex`
.. * :ref:`modindex`
.. * :ref:`search`
