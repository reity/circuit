"""
Minimal native Python library for building and working with
logical circuits (both as expressions and as graphs).
"""
from __future__ import annotations
from typing import Sequence, Optional, Union, Callable
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
        if is_output and operation != op.id_:
            raise ValueError("output gates must correspond to the identity operation")

        if inputs is not None:
            for gi in inputs:
                if gi.is_output:
                    raise ValueError(
                        "output gates cannot be designated as inputs into other gates"
                    )

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

        :param other: Gate to be designated as an output gate of this gate.

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
        Mark all gates reachable from the supplied gate via recursive traversal
        of input gate references.

        :param g: Gate from which to mark all reachable gates (via input references).

        >>> c = circuit()
        >>> g0 = c.gate(op.id_, is_input=True)
        >>> g1 = c.gate(op.id_, is_input=True)
        >>> g2 = c.gate(op.and_, [g0, g1])
        >>> g3 = c.gate(op.id_, [g2], is_output=True)
        >>> gates.mark(g3)
        >>> all(g.is_marked for g in [g0, g1, g2, g3])
        True
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

        >>> gs = gates([])
        >>> g0 = gs(op.id_, is_input=True)
        >>> g1 = gs(op.id_, is_input=True)
        >>> g2 = gs(op.and_, [g0, g1])
        >>> g3 = gs(op.id_, [g2], is_output=True)
        >>> len(gs)
        4

        Only a gate with an identity operation can be designated as an output gate.

        >>> g4 = gs(op.not_, [g2], is_output=True)
        Traceback (most recent call last):
          ...
        ValueError: output gates must correspond to the identity operation

        A gate designated as an output gate cannot be an input into another gate.

        >>> g4 = gs(op.not_, [g3])
        Traceback (most recent call last):
          ...
        ValueError: output gates cannot be designated as inputs into other gates
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

    def input(self: signature, input: Sequence[Sequence[int]]) -> Sequence[int]:
        """
        Convert an input organized in a way that matches the signature's input
        format into a flat list of bits.

        :param input: Input bit vector that matches signature.

        >>> s = signature(input_format=[2, 3])
        >>> s.input([[1, 0], [0, 1, 1]])
        [1, 0, 0, 1, 1]
        """
        if self.input_format is None:
            return input
        elif not isinstance(input, list) or\
             not all(
                 (isinstance(bs, list) and all(isinstance(b, int) for b in bs))
                 for bs in input
             ):
            raise TypeError('input must be a list of integer lists')
        elif [len(bs) for bs in input] == self.input_format:
            return [b for bs in input for b in bs]
        else:
            raise ValueError('input format does not match signature')

    def output(self: signature, output: Sequence[int]) -> Sequence[Sequence[int]]:
        """
        Convert a flat list of output bits into a format that
        matches the signature's output format specification.

        :param output: Flat output bit vector to convert (according to signature).

        >>> s = signature(output_format=[2, 3])
        >>> list(s.output([1, 0, 0, 1, 1]))
        [[1, 0], [0, 1, 1]]
        """
        if self.output_format is None:
            return output
        else:
            return list(parts(output, length=self.output_format))

class circuit():
    """
    Data structure for an instance of a circuit.

    :param sig: Signature (input and output bit vector lengths) for the circuit.

    >>> c = circuit()
    >>> c.count()
    0
    >>> g0 = c.gate(op.id_, is_input=True)
    >>> g1 = c.gate(op.id_, is_input=True)
    >>> g2 = c.gate(op.and_, [g0, g1])
    >>> g3 = c.gate(op.id_, [g2], is_output=True)
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
    4
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
    6
    >>> [list(c.evaluate([bs])) for bs in [[0, 0], [0, 1], [1, 0], [1, 1]]]
    [[[0]], [[1]], [[1]], [[0]]]

    Circuits can contain constant gates that take no inputs (corresponding to
    one of the two nullary logical operations). This also implies that circuits
    that take no inputs can be defined an evaluated.

    >>> c = circuit()
    >>> g0 = c.gate(op.nt_)
    >>> g1 = c.gate(op.nf_)
    >>> g2 = c.gate(op.or_, [g0, g1])
    >>> g3 = c.gate(op.id_, [g2], is_output=True)
    >>> c.evaluate([])
    [1]

    A signature can be used to indicate that a circuit takes no inputs. Note that
    if a signature is supplied, an input that contains not bits must still be
    supplied to the :obj:`circuit.evaluate` method.

    >>> c = circuit(signature([0], [1]))
    >>> g0 = c.gate(op.nt_)
    >>> g1 = c.gate(op.nf_)
    >>> g2 = c.gate(op.or_, [g0, g1])
    >>> g3 = c.gate(op.id_, [g2], is_output=True)
    >>> c.evaluate([[]])
    [[1]]

    Circuits may also have input gates or internal gates that have no path to any
    gate that has been designated as an output gate. Such gates may or may not
    have outgoing connections to other gates (*i.e.*, they may be *non-sinks* or
    they may be *sinks*). This implies that circuits that consist of two or more
    disconnected components are permitted.

    >>> c = circuit()
    >>> g0 = c.gate(op.id_, is_input=True) # Input (non-sink) with no path to output.
    >>> g1 = c.gate(op.id_, is_input=True) # Input (sink) with no path to output.
    >>> g2 = c.gate(op.not_, [g0]) # Internal gate (non-sink) with no path to output.
    >>> g3 = c.gate(op.and_, [g0, g2]) # Internal gate (sink) no path to output.
    >>> g4 = c.gate(op.nt_)
    >>> g5 = c.gate(op.nf_)
    >>> g6 = c.gate(op.or_, [g4, g5])
    >>> g7 = c.gate(op.id_, [g6], is_output=True)

    When evaluating a circuit, the input bit vector must include a bit for every
    input gate (even if some of those gates have no paths to an output gate).

    >>> c.evaluate([0, 1])
    [1]

    Pruning a circuit will remove interior gates that have no path to any output
    gate, but will not remove any input gates (preserving the circuit's signature).

    >>> c.count()
    8
    >>> c.prune_and_topological_sort_stable()
    >>> c.count()
    6
    >>> [g.operation.name() for g in c.gate]
    ['id', 'id', 'nt', 'nf', 'or', 'id']
    """
    def __init__(self: circuit, sig: Optional[signature] = None):
        self.gate = gates([])
        self.signature = signature() if sig is None else sig

    def count(self: circuit, predicate: Callable[[gate], bool] = lambda _: True) -> int:
        """
        Count the number of gates that satisfy the supplied predicate.

        :param predicate: Function that distinguishes certain gate objects.

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
        >>> g5 = c.gate(op.id_, [g2], is_output=True)
        >>> c.count()
        6
        >>> c.prune_and_topological_sort_stable()
        >>> c.count()
        4
        >>> [g.operation.name() for g in c.gate]
        ['id', 'id', 'not', 'id']
        """
        # Collect all gates that feed directly into the identity gates
        # with no outputs; these are the effective output gates after
        # pruning.
        gate_output = []
        for g in self.gate:
            if len(g.outputs) == 0 and g.operation == op.id_ and g.is_output:
                gate_output.append(g)

        # Mark all gates that reach the output.
        for g in self.gate:
            g.is_marked = False
        for g in gate_output:
            gates.mark(g)

        index_old_to_new = {}
        gate_ = [] # New gates to replace old gates.

        # Collect and prune the input gates at the beginning.
        for (index, g) in enumerate(self.gate):
            if len(g.inputs) == 0 and g.is_input:
                index_old_to_new[index] = len(gate_)
                gate_.append(g)

        # Collect and prune the non-input/non-output gates in the interior.
        for (index, g) in enumerate(self.gate):
            if all([
                (len(g.inputs) > 0 or g.operation in logical.nullary),
                (len(g.outputs) > 0),
                (not g.is_input and not g.is_output),
                g.is_marked
            ]):
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

    def evaluate(
            self: circuit,
            input: Union[Sequence[int], Sequence[Sequence[int]]]
        ) -> Union[Sequence[int], Sequence[Sequence[int]]]:
        """
        Evaluate the circuit on an input organized in a way that
        matches the circuit signature's input format, and return
        an output that matches the circuit signature's output format.

        :param input: Input bit vector or bit vectors.

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
        wire = (
            self.signature.input(input) + \
            (
                [None] * \
                self.count(
                    # Create empty wire entries for any gates with inputs and any constant
                    # (nullary operation) gates.
                    lambda g: len(g.inputs) > 0 or g.operation in logical.nullary
                )
            )
        )

        # Evaluate the gates.
        for g in self.gate:
            if len(g.inputs) > 0 or g.operation in logical.nullary:
                wire[g.index] =\
                    g.operation(*[wire[ig.index] for ig in g.inputs])

        return self.signature.output(
            wire[
                -self.count(lambda g: len(g.outputs) == 0 and g.is_output):
            ]
        )

if __name__ == "__main__":
    doctest.testmod() # pragma: no cover
