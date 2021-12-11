"""
Minimal native Python library for building and working with
logical circuits (both as expressions and as graphs).
"""
from __future__ import annotations
from typing import Sequence
import doctest
from parts import parts
from logical import logical

# Synonyms (also exported).
operation = logical
op = logical

class gate:
    """
    Data structure for an individual circuit logic gate.

    :param operation: Logical operation that the gate represents.
    :param inputs: List of input gate object references.
    :param outputs: List of output gate object references.
    :param is_input: Flag indicating if this is an input gate for a circuit.
    :param is_output: Flag indicating if this is an output gate for a circuit.
    """
    def __init__(
            self: gate, operation: op = None,
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
        """
        Designate another gate as an output gate of this gate.

        >>> c = circuit()
        >>> g0 = c.gate(op.id_, is_input=True)
        >>> g1 = c.gate(op.id_, is_input=True)
        >>> g2 = c.gate(op.and_, [g0, g1])
        >>> g3 = c.gate(op.id_, [g2], is_output=True)
        >>> g2.output(g3) # Confirm this is idempotent.
        >>> c.count()
        4
        """
        if not any(o is other for o in self.outputs):
            self.outputs = self.outputs + [other]

class gates(list):
    """
    Data structure for a gate collection that appears in a circuit.
    """
    @staticmethod
    def mark(g: gate):
        """
        Mark all gates reachable from the input gate.
        """
        if not g.is_marked:
            g.is_marked = True
            for ig in g.inputs:
                gates.mark(ig)

    def __call__(
            self: gates, operation: op = None,
            inputs: Sequence[gate] = None, outputs: Sequence[gate] = None,
            is_input: bool = False, is_output: bool = False
        ):
        """
        Add a gate to this collection of gates.

        :param operation: Logical operation that the gate represents.
        :param inputs: List of input gate object references.
        :param outputs: List of output gate object references.
        :param is_input: Flag indicating if this is an input gate for a circuit.
        :param is_output: Flag indicating if this is an output gate for a circuit.
        """
        g = gate(operation, inputs, outputs, is_input, is_output)
        g.index = len(self)
        self.append(g)
        return g

class signature:
    """
    Data structure for a circuit signature.

    :param input_format: List of bit vector lengths of inputs.
    :param output_format: List of bit vector lengths of outputs.

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

    An instance can be evaluated on any list of bits using the :obj:`evaluate`
    method. The result is a bit vector that includes one bit for each output
    gate.

    >>> [list(c.evaluate(bs)) for bs in [[0, 0], [0, 1], [1, 0], [1, 1]]]
    [[0], [0], [0], [1]]

    It is also possible to remove all internal gates from a circuit from which
    an output gate cannot be reached. Doing so does not change the order of the
    input gates or the order of the output gates.

    >>> c.prune_and_topological_sort_stable()
    >>> c.count()
    3
    >>> [list(c.evaluate(bs)) for bs in [[0, 0], [0, 1], [1, 0], [1, 1]]]
    [[0], [0], [0], [1]]

    It is also possible to specify the signature of a circuit using the
    :obj:`signature` class.

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
    """
    def __init__(self: circuit, sig: signature = None):
        self.gate = gates([])
        self.signature = signature() if sig is None else sig

    def count(self: circuit, predicate=lambda _: True) -> int:
        """
        Count the number of gates that satisfy the supplied predicate.

        >>> c = circuit(signature([2], [1]))
        >>> g0 = c.gate(op.id_, is_input=True)
        >>> g1 = c.gate(op.id_, is_input=True)
        >>> g2 = c.gate(op.not_, [g0])
        >>> g3 = c.gate(op.not_, [g1])
        >>> g4 = c.gate(op.xor_, [g2, g3])
        >>> g5 = c.gate(op.id_, [g4], is_output=True)
        >>> c.count(lambda g: g.operation == op.id_)
        3
        """
        return len([() for g in self.gate if predicate(g)])

    def prune_and_topological_sort_stable(self: circuit):
        """
        Prune any gates from which an output gate cannot be reached
        and topologically sort the gates (with input gates all in
        their original order at the beginning and output gates all
        in their original order at the end).

        >>> c = circuit(signature([2], [1]))
        >>> g0 = c.gate(op.id_, is_input=True)
        >>> g1 = c.gate(op.id_, is_input=True)
        >>> g2 = c.gate(op.not_, [g0])
        >>> g3 = c.gate(op.not_, [g1])
        >>> g4 = c.gate(op.xor_, [g2, g3])
        >>> g5 = c.gate(op.id_, [g4], is_output=True)
        >>> c.count()
        6
        >>> c.prune_and_topological_sort_stable()
        >>> c.count()
        5
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

        >>> c = circuit()
        >>> g0 = c.gate(op.id_, is_input=True)
        >>> g1 = c.gate(op.id_, is_input=True)
        >>> g2 = c.gate(op.and_, [g0, g1])
        >>> g3 = c.gate(op.id_, [g2], is_output=True)
        >>> list(c.evaluate([0, 1]))
        [0]

        It is also possible to evaluate a circuit that has a signature
        specified. Note that in this case, the inputs and outputs must
        be lists of lists (to reflect that there are multiple inputs).

        >>> c = circuit(signature([2], [1]))
        >>> g0 = c.gate(op.id_, is_input=True)
        >>> g1 = c.gate(op.id_, is_input=True)
        >>> g2 = c.gate(op.and_, [g0, g1])
        >>> g3 = c.gate(op.id_, [g2], is_output=True)
        >>> list(c.evaluate([[0, 1]]))
        [[0]]

        Any attempt to evaluate a circuit on an invalid input raises
        an exception.

        >>> c.evaluate([[0, 0, 0]])
        Traceback (most recent call last):
          ...
        ValueError: input format does not match signature
        >>> c.evaluate([0, 0])
        Traceback (most recent call last):
          ...
        TypeError: input must be a list of integer lists
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
