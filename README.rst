=======
circuit
=======

Pure-Python library for building and working with logical circuits.

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

.. |coveralls| image:: https://coveralls.io/repos/github/reity/circuit/badge.svg?branch=main
   :target: https://coveralls.io/github/reity/circuit?branch=main
   :alt: Coveralls test coverage summary.

Installation and Usage
----------------------
This library is available as a `package on PyPI <https://pypi.org/project/circuit>`__::

    python -m pip install circuit

The library can be imported in the usual way::

    import circuit
    from circuit import *

Examples
^^^^^^^^
This library makes it possible to programmatically construct logical circuits consisting of interconnected logic gates. The functions corresponding to individual logic gates are represented using the `logical <https://pypi.org/project/logical>`__ library. In the example below, a simple conjunction circuit is constructed, and its input and output gates (corresponding to the logical unary identity function) are created and designated as such::

    >>> from circuit import circuit, op
    >>> c = circuit()
    >>> g0 = c.gate(op.id_, is_input=True)
    >>> g1 = c.gate(op.id_, is_input=True)
    >>> g2 = c.gate(op.and_, [g0, g1])
    >>> g3 = c.gate(op.id_, [g2], is_output=True)
    >>> c.count() # Number of gates in the circuit.
    4

The gate list associated with a circuit can be converted into a concise human-readable format, enabling manual inspection of the circuit::

    >>> c.gate.to_legible()
    (('id',), ('id',), ('and', 0, 1), ('id', 2))

.. |evaluate| replace:: ``evaluate``
.. _evaluate: https://circuit.readthedocs.io/en/2.0.0/_source/circuit.html#circuit.circuit.circuit.evaluate

The circuit accepts two input bits (represented as integers) and can be evaluated on any list of two bits using the |evaluate|_ method. The result is a bit vector that includes one bit for each output gate::

    >>> c.evaluate([0, 1])
    [0]
    >>> [list(c.evaluate(bs)) for bs in [[0, 0], [0, 1], [1, 0], [1, 1]]]
    [[0], [0], [0], [1]]

.. |gate| replace:: ``gate``
.. _gate: https://circuit.readthedocs.io/en/2.0.0/_source/circuit.html#circuit.circuit.circuit.gate

Note that the order of the output bits corresponds to the order in which the output gates were originally introduced using the |gate|_ method. It is possible to specify the signature of a circuit (*i.e.*, the organization of input gates and output gates into distinct bit vectors of specific lengths) at the time the circuit object is created::

    >>> from circuit import signature
    >>> c = circuit(signature([2], [1]))
    >>> g0 = c.gate(op.id_, is_input=True)
    >>> g1 = c.gate(op.id_, is_input=True)
    >>> g2 = c.gate(op.not_, [g0])
    >>> g3 = c.gate(op.not_, [g1])
    >>> g4 = c.gate(op.xor_, [g2, g3])
    >>> g5 = c.gate(op.not_, [g4])
    >>> g6 = c.gate(op.id_, [g4], is_output=True)
    >>> [list(c.evaluate([bs])) for bs in [[0, 0], [0, 1], [1, 0], [1, 1]]]
    [[[0]], [[1]], [[1]], [[0]]]

It is also possible to remove all internal gates from which an output gate cannot be reached (such as ``g5`` in the example above). Doing so does not change the order of the input gates or the order of the output gates::

    >>> c.count()
    7
    >>> c.prune_and_topological_sort_stable()
    >>> c.count()
    6

Development
-----------
All installation and development dependencies are fully specified in ``pyproject.toml``. The ``project.optional-dependencies`` object is used to `specify optional requirements <https://peps.python.org/pep-0621>`__ for various development tasks. This makes it possible to specify additional options (such as ``docs``, ``lint``, and so on) when performing installation using `pip <https://pypi.org/project/pip>`__::

    python -m pip install .[docs,lint]

Documentation
^^^^^^^^^^^^^
The documentation can be generated automatically from the source files using `Sphinx <https://www.sphinx-doc.org>`__::

    python -m pip install .[docs]
    cd docs
    sphinx-apidoc -f -E --templatedir=_templates -o _source .. && make html

Testing and Conventions
^^^^^^^^^^^^^^^^^^^^^^^
All unit tests are executed and their coverage is measured when using `pytest <https://docs.pytest.org>`__ (see the ``pyproject.toml`` file for configuration details)::

    python -m pip install .[test]
    python -m pytest

Alternatively, all unit tests are included in the module itself and can be executed using `doctest <https://docs.python.org/3/library/doctest.html>`__::

    python circuit/circuit.py -v

Style conventions are enforced using `Pylint <https://pylint.pycqa.org>`__::

    python -m pip install .[lint]
    python -m pylint circuit

Contributions
^^^^^^^^^^^^^
In order to contribute to the source code, open an issue or submit a pull request on the `GitHub page <https://github.com/reity/circuit>`__ page for this library.

Versioning
^^^^^^^^^^
Beginning with version 0.2.0, the version number format for this library and the changes to the library associated with version number increments conform with `Semantic Versioning 2.0.0 <https://semver.org/#semantic-versioning-200>`__.

Publishing
^^^^^^^^^^
This library can be published as a `package on PyPI <https://pypi.org/project/circuit>`__ by a package maintainer. First, install the dependencies required for packaging and publishing::

    python -m pip install .[publish]

Ensure that the correct version number appears in ``pyproject.toml``, and that any links in this README document to the Read the Docs documentation of this package (or its dependencies) have appropriate version numbers. Also ensure that the Read the Docs project for this library has an `automation rule <https://docs.readthedocs.io/en/stable/automation-rules.html>`__ that activates and sets as the default all tagged versions. Create and push a tag for this version (replacing ``?.?.?`` with the version number)::

    git tag ?.?.?
    git push origin ?.?.?

Remove any old build/distribution files. Then, package the source into a distribution archive using the `wheel <https://pypi.org/project/wheel>`__ package::

    rm -rf build dist *.egg-info
    python -m build --sdist --wheel .

Finally, upload the package distribution archive to `PyPI <https://pypi.org>`__ using the `twine <https://pypi.org/project/twine>`__ package::

    python -m twine upload dist/*
