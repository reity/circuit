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
    Class for representing circuit signatures (*i.e.*, the input and output
    bit vector formats associated with evaluation of a circuit).

    :param input_format: List of bit vector lengths of inputs.
    :param output_format: List of bit vector lengths of outputs.

    An instance of this class can be used (1) to convert circuit evaluation
    inputs from the specific signature-compatible format into a flattened
    list of bits and (2) to convert the flat list of bits obtained as a
    circuit evaluation output into a signature-compatible format. If a
    :obj:`circuit` instance has been assigned a signature, conversion of
    inputs and outputs is performed automatically by the :obj:`evaluate`
    method.

    >>> s = signature([2, 2], [3, 1])
    >>> s.input([[1, 0], [0, 1]])
    [1, 0, 0, 1]
    >>> s.output([1, 1, 0, 0])
    [[1, 1, 0], [0]]

    If no formats are supplied, the signature methods expect that inputs
    and outputs are flat lists or tuples of integers that represent bits.

    >>> s = signature()
    >>> s.input([1, 0, 1])
    [1, 0, 1]
    >>> s.input((1, 0, 1))
    [1, 0, 1]
    >>> s.input([[1], [1], [1]])
    Traceback (most recent call last):
      ...
    TypeError: input must be a list or tuple of integers
    >>> s.input([2, 3, 4])
    Traceback (most recent call last):
      ...
    ValueError: each bit must be represented by 0 or 1
    >>> s.output([1, 0, 1])
    [1, 0, 1]
    >>> s.output((1, 0, 1))
    [1, 0, 1]

    The conversion methods also perform checks to ensure that the input
    has valid format, types, and values.

    >>> s.input({1, 2, 3})
    Traceback (most recent call last):
      ...
    TypeError: input must be a list or tuple of integers
    >>> s = signature([2], [1])
    >>> s.input([[2], [3], [4]])
    Traceback (most recent call last):
      ...
    ValueError: each bit must be represented by 0 or 1

    Signature specifications must be lists or tuples of integers, where
    each integer represents the length of an input or output bit vector.

    >>> signature(['a', 'b'], [1])
    Traceback (most recent call last):
      ...
    TypeError: signature input format must be a tuple or list of integers
    >>> signature([2], ['c'])
    Traceback (most recent call last):
      ...
    TypeError: signature output format must be a tuple or list of integers
    """
    def __init__(
            self: signature,
            input_format: Sequence[int] = None,
            output_format: Sequence[int] = None
        ):
        if input_format is not None and ( \
               not isinstance(input_format, (tuple, list)) or \
               not all(isinstance(i, int) for i in input_format) \
           ):
            raise TypeError(
                'signature input format must be a tuple or list of integers'
            )
        self.input_format = list(input_format) if input_format is not None else None

        if output_format is not None and ( \
               not isinstance(output_format, (tuple, list)) or \
               not all(isinstance(o, int) for o in output_format) \
           ):
            raise TypeError(
                'signature output format must be a tuple or list of integers'
            )
        self.output_format = list(output_format) if output_format is not None else None

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
            if (
                not isinstance(input, (tuple, list)) or \
                not all(isinstance(b, int) for b in input)
            ):
                raise TypeError('input must be a list or tuple of integers')
            if not all(b in (0, 1) for b in input):
                raise ValueError('each bit must be represented by 0 or 1')
            return list(input)
        elif not isinstance(input, (tuple, list)) or \
             not all(
                 (isinstance(bs, (tuple, list)) and all(isinstance(b, int) for b in bs))
                 for bs in input
             ):
            raise TypeError('input must be a list or tuple of integer lists')
        elif not all(all(b in (0, 1) for b in bs) for bs in input):
            raise ValueError('each bit must be represented by 0 or 1')
        elif [len(bs) for bs in input] == self.input_format:
            return [b for bs in input for b in bs] # Flatten the bit vector.
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
            return list(output)
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
    >>> g3 = c.gate(op.or_, [g0, g1]) # Example of gate that can be pruned.
    >>> g4 = c.gate(op.id_, [g2], is_output=True)
    >>> c.count()
    5

    An instance can be evaluated on any list of bits using the :obj:`evaluate`
    method. The result is a bit vector that includes one bit for each output
    gate.

    >>> [list(c.evaluate(bs)) for bs in [[0, 0], [0, 1], [1, 0], [1, 1]]]
    [[0], [0], [0], [1]]

    Using the :obj:`prune_and_topological_sort_stable` method, it is
    possible to remove all internal gates from a circuit from which an output
    gate cannot be reached. Doing so does not change the order of the input
    gates or the order of the output gates.

    >>> c.prune_and_topological_sort_stable()
    >>> c.count()
    4
    >>> [list(c.evaluate(bs)) for bs in [[0, 0], [0, 1], [1, 0], [1, 1]]]
    [[0], [0], [0], [1]]

    It is possible to specify the signature of a circuit using the :obj:`signature`
    class.

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

    Specifying a signature changes the required format for input bit vectors.
    Rather than a list of integers, the input should consist of a *list* of
    lists of integers (one list of integers for each input). Thus, an input for
    the above circuit would be ``[[0, 1]]`` rather than ``[0, 1]`` (because the
    circuit expects one input having two bits). Specifying a signature similarly
    changes the output format in the same manner, as some circuits may have a
    signature that indicates that the output consists of some number of bit
    vectors, each having a specific length. The circuit above has one output:
    a bit vector having a single bit. Thus, the outputs are of the form ``[[1]]``.

    >>> [list(c.evaluate(bss)) for bss in [[[0, 0]], [[0, 1]], [[1, 0]], [[1, 1]]]]
    [[[0]], [[1]], [[1]], [[0]]]
    >>> [list(c.evaluate(bss)) for bss in [[[0, 0]], [[0, 1]], [[1, 0]], [[1, 1]]]]
    [[[0]], [[1]], [[1]], [[0]]]

    The circuit in the example below is identical to the one in the example above,
    but has a different signature. Notice that inputs to the :obj:`evaluate` method
    must have a format that conforms to the circuit's signature. In the example
    below, the inputs now consist of two bit vectors. Thus, what was above an input
    of the form ``[[0, 1]]`` must instead be ``[[0], [1]]`` (*i.e.*, two inputs each
    having one bit).

    >>> c = circuit(signature([1, 1], [1]))
    >>> g0 = c.gate(op.id_, is_input=True)
    >>> g1 = c.gate(op.id_, is_input=True)
    >>> g2 = c.gate(op.not_, [g0])
    >>> g3 = c.gate(op.not_, [g1])
    >>> g4 = c.gate(op.xor_, [g2, g3])
    >>> g5 = c.gate(op.id_, [g4], is_output=True)
    >>> [list(c.evaluate(bss)) for bss in [[[0], [0]], [[0], [1]], [[1], [0]], [[1], [1]]]]
    [[[0]], [[1]], [[1]], [[0]]]

    The signature of a circuit instance ``c`` is stored in the attribute
    ``c.signature``. It is possible to update the signature for a circuit by
    assigning the signature to this attribute. The example below reverts the
    signature of the circuit ``c`` defined above to the default (*i.e.*, one
    input and one output).

    >>> c.signature = signature()
    >>> [list(c.evaluate(bs)) for bs in [[0, 0], [0, 1], [1, 0], [1, 1]]]
    [[0], [1], [1], [0]]

    Circuits can contain constant gates that take no inputs (corresponding to
    one of the two nullary logical operations). This also implies that circuits
    that take no inputs can be defined and evaluated.

    >>> c = circuit()
    >>> g0 = c.gate(op.nt_)
    >>> g1 = c.gate(op.nf_)
    >>> g2 = c.gate(op.or_, [g0, g1])
    >>> g3 = c.gate(op.id_, [g2], is_output=True)
    >>> c.evaluate([])
    [1]

    A signature can also be used to indicate that a circuit takes no inputs.
    Note that if a signature is supplied for such a circuit, a list of inputs
    containing one input that contains no bits must still be supplied in the
    list of inputs to the :obj:`evaluate` method.

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
        If no predicate is supplied, the total number of gates in the
        circuit is returned.

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
        >>> c.count()
        6
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

        >>> c.evaluate([0, 0])
        Traceback (most recent call last):
          ...
        TypeError: input must be a list or tuple of integer lists

        If a signature has been specified for the circuit, any attempt
        to evaluate the circuit on an input that does not conform to the
        signature raises an exception.

        >>> c.evaluate([[0, 0, 0]])
        Traceback (most recent call last):
          ...
        ValueError: input format does not match signature
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
