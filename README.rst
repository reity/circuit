=======
circuit
=======

Minimal native Python library for building and working with logical circuits.

|pypi| |readthedocs| |actions| |coveralls|

.. |pypi| image:: https://badge.fury.io/py/circuit.svg
   :target: https://badge.fury.io/py/circuit
   :alt: PyPI version and link.

.. |readthedocs| image:: https://readthedocs.org/projects/circuit/badge/?version=latest
   :target: https://circuit.readthedocs.io/en/latest/?badge=latest
   :alt: Read the Docs documentation status.

.. |actions| image:: https://github.com/reity/circuit/workflows/lint-test-cover-docs/badge.svg
   :target: https://github.com/reity/circuit/actions/workflows/lint-test-cover-docs.yml
   :alt: GitHub Actions status.

.. |coveralls| image:: https://coveralls.io/repos/github/reity/circuit/badge.svg?branch=master
   :target: https://coveralls.io/github/reity/circuit?branch=master
   :alt: Coveralls test coverage summary.

Package Installation and Usage
------------------------------
The package is available on `PyPI <https://pypi.org/project/circuit/>`_::

    python -m pip install circuit

The library can be imported in the usual way::

    import circuit
    from circuit import *

Examples
^^^^^^^^
This library make it possible to programmatically construct logical circuits consisting of interconnected logic gates. The functions corresponding to individual logic gates are represented using the `logical <https://pypi.org/project/logical/>`_ library. In the example below, a simple conjunction circuit is constructed, and its input and output gates (corresponding to the logical unary identity function) are created and designated as such::

    >>> from circuit import circuit, op
    >>> c = circuit()
    >>> g0 = c.gate(op.id_, is_input=True)
    >>> g1 = c.gate(op.id_, is_input=True)
    >>> g2 = c.gate(op.and_, [g0, g1])
    >>> g3 = c.gate(op.id_, [g2], is_output=True)
    >>> c.count() # Number of gates in the circuit.
    4

The circuit accepts two input bits (represented as integers) and can be evaluated on any list of two bits using the ``evaluate`` method. The result is a bit vector that includes one bit for each output gate.

    >>> c.evaluate([0, 1])
    [0]
    >>> [list(c.evaluate(bs)) for bs in [[0, 0], [0, 1], [1, 0], [1, 1]]]
    [[0], [0], [0], [1]]

Note that the order of the output bits corresponds to the order in which the output gates were originally introduced using the ``gate`` method. It is possible to specify the signature of a circuit (*i.e.*, the number of input gates and the number of output gates) at the time the circuit object is created::

    >>> from circuit import signature
    >>> c = circuit(signature([2], [1]))
    >>> g0 = c.gate(op.id_, is_input=True)
    >>> g1 = c.gate(op.id_, is_input=True)
    >>> g2 = c.gate(op.not_, [g0])
    >>> g3 = c.gate(op.not_, [g1])
    >>> g4 = c.gate(op.xor_, [g2, g3])
    >>> g5 = c.gate(op.id_, [g4], is_output=True)
    >>> [list(c.evaluate([bs])) for bs in [[0, 0], [0, 1], [1, 0], [1, 1]]]
    [[[0]], [[1]], [[1]], [[0]]]

It is also possible to remove all internal gates from a circuit from which an output gate cannot be reached. Doing so does not change the order of the input gates or the order of the output gates::

    >>> c.count()
    6
    >>> c.prune_and_topological_sort_stable()
    >>> c.count()
    5

Documentation
-------------
.. include:: toc.rst

The documentation can be generated automatically from the source files using `Sphinx <https://www.sphinx-doc.org/>`_::

    cd docs
    python -m pip install -r requirements.txt
    sphinx-apidoc -f -E --templatedir=_templates -o _source .. ../setup.py && make html

Testing and Conventions
-----------------------
All unit tests are executed and their coverage is measured when using `pytest <https://docs.pytest.org/>`_ (see ``setup.cfg`` for configuration details)::

    python -m pip install pytest pytest-cov
    python -m pytest

Alternatively, all unit tests are included in the module itself and can be executed using `doctest <https://docs.python.org/3/library/doctest.html>`_::

    python circuit/circuit.py -v

Style conventions are enforced using `Pylint <https://www.pylint.org/>`_::

    python -m pip install pylint
    python -m pylint circuit

Contributions
-------------
In order to contribute to the source code, open an issue or submit a pull request on the `GitHub page <https://github.com/reity/circuit>`_ page for this library.

Versioning
----------
Beginning with version 0.2.0, the version number format for this library and the changes to the library associated with version number increments conform with `Semantic Versioning 2.0.0 <https://semver.org/#semantic-versioning-200>`_.

Publishing
----------
This library can be published as a `package on PyPI <https://pypi.org/project/circuit/>`_ by a package maintainer. Install the `wheel <https://pypi.org/project/wheel/>`_ package, remove any old build/distribution files, and package the source into a distribution archive::

    python -m pip install wheel
    rm -rf dist *.egg-info
    python setup.py sdist bdist_wheel

Next, install the `twine <https://pypi.org/project/twine/>`_ package and upload the package distribution archive to PyPI::

    python -m pip install twine
    python -m twine upload dist/*
