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
    def __init__(self, s = (lambda cs: 'x'), f = None, a = 1, cs = []):
        sf = (lambda cs: s) if type(s) is str else s # Display string to function.
        for (k,v) in {'s':sf, 'f':f, 'a':a, 'cs':cs}.items():
            setattr(self, k, v)

    def __add__(self, oth):
        return circuit((lambda cs: '('+str(cs[0])+' + '+str(cs[1])+')'), operator.add, self.a + oth.a, [self, oth])

    def __mul__(self, oth):
        return circuit((lambda cs: '('+str(cs[0])+' * '+str(cs[1])+')'), operator.mul, self.a + oth.a, [self, oth])

    def __call__(self, *args):
        if self.a == 1:
            return args[0]
        (vs, i) = ([], 0)
        for c in self.cs:
            vs.append(c(*args[i : i + c.a]))
            i += c.a
        return self.f(*vs)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return self.s(self.cs)

if __name__ == "__main__": 
    doctest.testmod()

## eof