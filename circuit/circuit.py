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
    """
    def __init__(self):
        pass

if __name__ == "__main__": 
    doctest.testmod()

## eof