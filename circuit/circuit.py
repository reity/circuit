"""Circuit graph/expression library.

Minimal native Python library for building and working with
logical circuits.
"""

from __future__ import annotations
from typing import Sequence
import doctest
from math import log2
from itertools import product
from parts import parts

class operation(tuple):
    """
    The list of binary logical operations represented as
    the output columns of truth tables where the input
    column pairs are sorted in ascending order:
    * (0,0,0,0) is FALSE
    * (0,0,0,1) is AND
    * (0,0,1,0) is NIMP (i.e., >)
    * (0,0,1,1) is FST (first/left-hand input)
    * (0,1,0,0) is NIF (i.e., <)
    * (0,1,0,1) is SND (second/right-hand input)
    * (0,1,1,0) is XOR (i.e., !=)
    * (0,1,1,1) is OR
    * (1,0,0,0) is NOR
    * (1,0,0,1) is XNOR (i.e., ==)
    * (1,0,1,0) is NSND (negation of second input)
    * (1,0,1,1) is IF (i.e., >=)
    * (1,1,0,0) is NFST (negation of first input)
    * (1,1,0,1) is IMP (i.e., <=)
    * (1,1,1,0) is NAND
    * (1,1,1,1) is TRUE
    """

    names = {
        (0,1): 'id',
        (1,0): 'not',
        (0,0,0,0): 'false',
        (0,0,0,1): 'and',
        (0,0,1,0): 'nimp',
        (0,0,1,1): 'fst',
        (0,1,0,0): 'nif',
        (0,1,0,1): 'snd',
        (0,1,1,0): 'xor',
        (0,1,1,1): 'or',
        (1,0,0,0): 'nor',
        (1,0,0,1): 'xnor',
        (1,0,1,0): 'nsnd',
        (1,0,1,1): 'if',
        (1,1,0,0): 'nfst',
        (1,1,0,1): 'imp',
        (1,1,1,0): 'nand',
        (1,1,1,1): 'true'
    }

    def __call__(self: operation, *arguments) -> int:
        """
        Apply the operator to an input tuple.

        >>> operation((1,0))(1)
        0
        >>> operation((1,0,0,1))(0,0)
        1
        >>> operation((1,0,0,1))(1,1)
        1
        >>> operation((1,0,0,1))(1,0)
        0
        >>> operation((1,0,0,1))(0,1)
        0
        >>> operation((1,0,0,1,0,1,0,1))(1,1,0)
        0
        """
        if len(arguments) == 1:
            return self[[0, 1].index(arguments[0])]
        elif len(arguments) == 2:
            return self[[(0,0),(0,1),(1,0),(1,1)].index(tuple(arguments))]
        else:
            inputs = list(product(*[(0,1)]*self.arity()))
            return self[inputs.index(tuple(arguments))]

    def name(self: operation) -> str:
        """
        Typical name for the operator.

        >>> operation((1,0,0,1)).name()
        'xnor'
        """
        return dict(operation.names)[self]

    def arity(self) -> int:
        """Arity of the operator."""
        return int(log2(len(self)))

# Concise synonyms for common operations.
operation.id_ = operation((0,1))
operation.not_ = operation((1,0))
operation.false_ = operation((0,0,0,0))
operation.and_ = operation((0,0,0,1))
operation.nimp_ = operation((0,0,1,0))
operation.fst_ = operation((0,0,1,1))
operation.nif_ = operation((0,1,0,0))
operation.snd_ = operation((0,1,0,1))
operation.xor_ = operation((0,1,1,0))
operation.or_ = operation((0,1,1,1))
operation.nor_ = operation((1,0,0,0))
operation.xnor_ = operation((1,0,0,1))
operation.nsnd_ = operation((1,0,1,0))
operation.if_ = operation((1,0,1,1))
operation.nfst_ = operation((1,1,0,0))
operation.imp_ = operation((1,1,0,1))
operation.nand_ = operation((1,1,1,0))
operation.true_ = operation((1,1,1,1))

# Concise synonym for class.
op = operation

class gate():
    """
    Data structure for an individual circuit logic gate.
    """

    def __init__(
            self: gate, operation: operation = None,
            inputs: Sequence[gate] = None, outputs: Sequence[gate] = None,
            is_input: bool = False, is_output: bool = False
        ):
        self.operation = operation
        self.inputs = [] if inputs is None else inputs
        self.outputs = [] if outputs is None else outputs
        self.index = None
        self.is_input = is_input
        self.is_output = is_output
        self.is_marked = False

        # Designate this new gate as an output gate for
        # each of its input gates.
        for ig in self.inputs:
            ig.output(self)

    def output(self: gate, other: gate):
        """Designate another gate as an output gate of this gate."""
        if not any(o is other for o in self.outputs):
            self.outputs = self.outputs + [other]

class gates(list):
    """
    Data structure for a gate collection that appears in a circuit.
    """

    @staticmethod
    def mark(g: gate):
        """Mark all gates reachable from the input gate."""
        if not g.is_marked:
            g.is_marked = True
            for ig in g.inputs:
                gates.mark(ig)

    def __call__(
            self: gates, operation: operation = None,
            inputs: Sequence[gate] = None, outputs: Sequence[gate] = None,
            is_input: bool = False, is_output: bool = False
        ):
        """Add a gate to this collection of gates."""
        g = gate(operation, inputs, outputs, is_input, is_output)
        g.index = len(self)
        self.append(g)
        return g

class signature():
    """
    Data structure for a circuit signatures.

    >>> s = signature()
    >>> s.input([1, 2, 3])
    [1, 2, 3]
    >>> s.output([1, 2, 3])
    [1, 2, 3]
    >>> signature(['a', 'b'], [1])
    Traceback (most recent call last):
      ...
    TypeError: signature input format must be a list of integers
    >>> signature([2], ['c'])
    Traceback (most recent call last):
      ...
    TypeError: signature output format must be a list of integers
    """

    def __init__(
            self: signature,
            input_format: Sequence[int] = None,
            output_format: Sequence[int] = None
        ):
        if input_format is not None and (\
               not isinstance(input_format, list) or\
               not all(isinstance(i, int) for i in input_format)\
           ):
            raise TypeError('signature input format must be a list of integers')
        self.input_format = input_format

        if output_format is not None and (\
               not isinstance(output_format, list) or\
               not all(isinstance(o, int) for o in output_format)\
           ):
            raise TypeError('signature output format must be a list of integers')
        self.output_format = output_format

    def input(self: signature, input):
        """
        Convert an input organized in a way that matches the
        signature's input format into a flat list of bits.
        """
        if self.input_format is None:
            return input
        elif not isinstance(input, list) or\
             not all(\
                 isinstance(bs, list) and all(isinstance(b, int)\
                 for b in bs) for bs in input\
             ):
            raise TypeError('input must be a list of integer lists')
        elif [len(bs) for bs in input] == self.input_format:
            return [b for bs in input for b in bs]
        else:
            raise ValueError('input format does not match signature')

    def output(self: signature, output):
        """
        Convert a flat list of output bits into a format that
        matches the signature's output format specification.
        """
        if self.output_format is None:
            return output
        else:
            return parts(output, length = self.output_format)

class circuit():
    """
    Data structure for an instance of a circuit.

    >>> c = circuit()
    >>> c.count()
    0
    >>> g0 = c.gate(op.id_, is_input=True)
    >>> g1 = c.gate(op.id_, is_input=True)
    >>> g2 = c.gate(op.and_, [g0, g1])
    >>> g3 = c.gate(op.id_, [g2], is_output=True)
    >>> g2.output(g3) # Confirm this is idempotent.
    >>> c.count()
    4
    >>> [list(c.evaluate(bs)) for bs in [[0, 0], [0, 1], [1, 0], [1, 1]]]
    [[0], [0], [0], [1]]
    >>> c.prune_and_topological_sort_stable()
    >>> c.count()
    3
    >>> [list(c.evaluate(bs)) for bs in [[0, 0], [0, 1], [1, 0], [1, 1]]]
    [[0], [0], [0], [1]]

    >>> c = circuit(signature([2], [1]))
    >>> c.count()
    0
    >>> g0 = c.gate(op.id_, is_input=True)
    >>> g1 = c.gate(op.id_, is_input=True)
    >>> g2 = c.gate(op.not_, [g0])
    >>> g3 = c.gate(op.not_, [g1])
    >>> g4 = c.gate(op.xor_, [g2, g3])
    >>> g5 = c.gate(op.id_, [g4], is_output=True)
    >>> c.count()
    6
    >>> [list(c.evaluate([bs])) for bs in [[0, 0], [0, 1], [1, 0], [1, 1]]]
    [[[0]], [[1]], [[1]], [[0]]]
    >>> c.prune_and_topological_sort_stable()
    >>> c.count()
    5
    >>> [list(c.evaluate([bs])) for bs in [[0, 0], [0, 1], [1, 0], [1, 1]]]
    [[[0]], [[1]], [[1]], [[0]]]
    >>> c.evaluate([[0, 0, 0]])
    Traceback (most recent call last):
      ...
    ValueError: input format does not match signature
    >>> c.evaluate([0, 0])
    Traceback (most recent call last):
      ...
    TypeError: input must be a list of integer lists
    """

    def __init__(self: circuit, sig: signature = None):
        self.gate = gates([])
        self.signature = signature() if sig is None else sig

    def count(self: circuit, predicate=lambda _: True) -> int:
        """Count the number of gates that satisfy the supplied predicate."""
        return len([() for g in self.gate if predicate(g)])

    def prune_and_topological_sort_stable(self: circuit):
        """
        Prune any gates from which an output gate cannot be reached
        and topologically sort the gates (with input gates all in
        their original order at the beginning and output gates all
        in their original order at the end).
        """

        # Collect all gates that feed directly into the identity gates
        # with no outputs; these are the effective output gates after
        # pruning.
        gate_output = []
        for g in self.gate:
            if len(g.outputs) == 0 and g.operation == op.id_ and g.is_output:
                g.inputs[0].is_output = True
                gate_output.append(g.inputs[0])

        # Mark all gates that reach the output.
        for g in self.gate:
            g.is_marked = False
        for g in gate_output:
            gates.mark(g)

        index_old_to_new = {}
        gate_ = [] # New gates to replace old gates.

        # Collect and prune the input gates at the beginning.
        for (index, g) in enumerate(self.gate):
            if len(g.inputs) == 0 and len(g.outputs) > 0 and g.is_input:
                index_old_to_new[index] = len(gate_)
                gate_.append(g)

        # Collect and prune the non-input/non-output gates in the middle.
        for (index, g) in enumerate(self.gate):
            if len(g.inputs) > 0 and len(g.outputs) > 0 and\
               not g.is_input and not g.is_output and\
               g.is_marked:
                index_old_to_new[index] = len(gate_)
                gate_.append(g)

        # Collect the new output gates at the end.
        for g in gate_output:
            g.outputs = [] # This is now an output, so remove its outputs.
            index_old_to_new[g.index] = len(gate_)
            gate_.append(g)

        # Update the index information to reflect the new order.
        for g in gate_:
            g.index = index_old_to_new[g.index]

        self.gate = gate_

    def evaluate(self: circuit, input):
        """
        Evaluate the circuit on an input organized in a way that
        matches the circuit signature's input format, and return
        an output that matches the circuit signature's output format.
        """
        input = self.signature.input(input)
        wire = input + [None]*(self.count(lambda g: len(g.inputs) > 0))

        # Evaluate the gates.
        for g in self.gate:
            if len(g.inputs) > 0:
                wire[g.index] =\
                    g.operation(*[wire[ig.index] for ig in g.inputs])

        return self.signature.output(wire[-self.count(lambda g: len(g.outputs) == 0):])

if __name__ == "__main__":
    doctest.testmod() # pragma: no cover
