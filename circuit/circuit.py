###############################################################################
## 
## circuit.py
##
##   Minimal pure Python library for building and working with circuit
##   graphs/expressions.
##
##   Web:     github.com/lapets/circuit
##
##

import doctest
import operator

###############################################################################
##

# A CircuitError is a general-purpose catch-all for any usage error.
class CircuitError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class circuit():
    """
    Class for circuits.

    >>> circuit('x')
    x
    >>> (circuit('x') + circuit('x'))(1, 2)
    3
    >>> (circuit('x') + circuit('x') * circuit('x'))(1, 2, 3)
    7
    """
    def __init__(self, s = (lambda cs: 'x'), 
                       f = None, arity = 1, 
                       cs = [], 
                       ops = {'add':operator.add, 'mul':operator.mul}
                ):
        sf = (lambda cs: s) if type(s) is str else s # Display string to function.
        for (k,v) in {'s':sf, 'f':f, 'arity':arity, 'cs':cs, 'ops':ops}.items():
            setattr(self, k, v)

    def __add__(self, oth):
        return circuit((lambda cs: '('+str(cs[0])+' + '+str(cs[1])+')'), 
                       self.ops['add'], self.arity + oth.arity, [self, oth], self.ops)

    def __mul__(self, oth):
        return circuit((lambda cs: '('+str(cs[0])+' * '+str(cs[1])+')'), 
                       self.ops['mul'], self.arity + oth.arity, [self, oth], self.ops)

    def __call__(self, *args):
        if self.arity == 1:
            return args[0]
        (vs, i) = ([], 0)
        for c in self.cs:
            vs.append(c(*args[i : i + c.arity]))
            i += c.arity
        return self.f(*vs)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return self.s(self.cs)

if __name__ == "__main__": 
    doctest.testmod()

## eof