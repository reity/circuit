"""Circuit graph/expression library.

Minimal native Python library for building and working with
logical circuits.
"""

from __future__ import annotations
from typing import Sequence
from parts import parts
import doctest

class operation(tuple):
    """
    The list of binary logical operations represented as
    the output columns of truth tables where the input
    column pairs are sorted in ascending order:
    * (0,0,0,0) is FALSE
    * (0,0,0,1) is AND
    * (0,0,1,0) is NIF (i.e., >)
    * (0,0,1,1) is FST (first/left-hand input)
    * (0,1,0,0) is NIMP (i.e., <)
    * (0,1,0,1) is SND (second/right-hand input)
    * (0,1,1,0) is XOR (i.e., !=)
    * (0,1,1,1) is OR
    * (1,0,0,0) is NOR
    * (1,0,0,1) is XNOR (i.e., ==)
    * (1,0,1,0) is NSND (negation of second input)
    * (1,0,1,1) is  IF (i.e., >=)
    * (1,1,0,0) is NFST (negation of first input)
    * (1,1,0,1) is IMP (i.e., <=)
    * (1,1,1,0) is NAND
    * (1,1,1,1) is TRUE
    The cases FALSE, FST, SND, NSND, NFST, and TRUE are not
    generally of interest and so do not have dedicated symbols
    and names.
    """

    names = {
        (0,1): 'id',
        (1,0): 'not',
        (0,0,0,1): 'and',
        (0,0,1,0): 'nif',
        (0,1,0,0): 'nimp',
        (0,1,1,0): 'xor',
        (0,1,1,1): 'or',
        (1,0,0,0): 'nor',
        (1,0,0,1): 'xnor',
        (1,0,1,1): 'if',
        (1,1,0,1): 'imp',
        (1,0,0,0): 'nand',
    }

    def __call__(self, *arguments):
        if len(arguments) == 1:
            return self[[0, 1].index(arguments[0])]
        elif len(arguments) == 2:
            return self[[(0,0),(0,1),(1,0),(1,1)].index(tuple(arguments))]

    def name(self):
        return dict(operation.names)[self]

# Concise synonyms for common operations.
operation.id_ = operation((0,1))
operation.not_ = operation((1,0))
operation.and_ = operation((0,0,0,1))
operation.nif_ = operation((0,0,1,0))
operation.nimp_ = operation((0,1,0,0))
operation.xor_ = operation((0,1,1,0))
operation.or_ = operation((0,1,1,1))
operation.nor_ = operation((1,0,0,0))
operation.xnor_ = operation((1,0,0,0))
operation.if_ = operation((1,0,1,1))
operation.imp_ = operation((1,1,0,1))
operation.nand_ = operation((1,0,0,0))

# Concise synonym for class.
op = operation 

class gate():
    """
    Data structure for an individual circuit logic gate.
    """

    def __init__(self, operation = None, 
                 inputs = None, outputs = None,
                 io = False):
        self.operation = operation
        self.inputs = [] if inputs is None else inputs
        self.outputs = [] if outputs is None else outputs
        self.index = None
        self.io = io

    def output(self, other):
        self.outputs = self.outputs + [other]

class gates(list):
    """
    Data structure for a gate collection that appears in a circuit.
    """

    def __call__(self, operation = None, 
                 inputs = None, outputs = None,
                 io = False):
        g = gate(operation, inputs, outputs, io)
        g.index = len(self)
        self.append(g)
        return g

class signature():
    """
    Data structure for a circuit signatures.
    """

    def __init__(self, input_format = None, output_format = None):
        self.input_format = input_format
        self.output_format = output_format

    def input(self, input):
        if self.input_format is None:
            return input
        elif isinstance(input, list) and\
             isinstance(self.input_format, list) and\
             [len(bs) for bs in input] == self.input_format:
            return [b for bs in input for b in bs]
        else:
            raise ValueError("input format does not match signature")

    def output(self, output):
        if self.output_format is None:
            return output
        elif isinstance(self.input_format, list):
            return parts(output, length = self.input_format)
        else:
            raise ValueError("output format in signature is not valid")

class circuit():
    """
    Data structure for an instance of a circuit.
    """

    def __init__(self):
        self.gate = gates([])
        self.signature = signature()

    def count(self, predicate):
        return len([() for g in self.gate if predicate(g)])

    def prune_and_topological_sort_stable(self):
        index_old_to_new = {}
        gate = []

        # Collect all gates that feed directly into the identity gates
        # with no outputs that have `io` set to `True`; these are the
        # effective output gates after pruning.
        gate_output = []
        for g in self.gate:
            if len(g.outputs) == 0 and g.operation == op.id_ and g.io:
                g.inputs[0].io = True
                gate_output.append(g.inputs[0])

        # Collect and prune the input gates at the beginning.
        for (index, g) in enumerate(self.gate):
            if len(g.inputs) == 0 and len(g.outputs) > 0 and g.io:
                index_old_to_new[index] = len(gate)
                gate.append(g)

        # Collect and prune the non-input/non-output gates in the middle.
        for (index, g) in enumerate(self.gate):
            if len(g.inputs) > 0 and len(g.outputs) > 0 and not g.io:
                index_old_to_new[index] = len(gate)
                gate.append(g)

        # Collect the new output gates at the end.
        for g in gate_output:
            index_old_to_new[g.index] = len(gate)
            gate.append(g)

        # Update the index information to reflect the new order.
        for g in gate:
            g.index = index_old_to_new[g.index]

        self.gate = gate

    def evaluate(self, input):
        """Evaluate the circuit on an input bit vector."""
        input = self.signature.input(input)
        wire = input + [None]*(self.count(lambda g: len(g.inputs) > 0))

        # Evaluate the gates.
        for g in self.gate:
            if len(g.inputs) > 0:
                wire[g.index] =\
                    g.operation(*[wire[ig.index] for ig in g.inputs])

        return self.signature.output(wire[-self.count(lambda g: len(g.outputs) == 0):])

if __name__ == "__main__":
    doctest.testmod()
