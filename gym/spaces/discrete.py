import numpy as np
from gym import Space

class Discrete(Space):
    """
    {0,1,...,n-1}
    """
    def __init__(self, n, np_random=None):
        if np_random is None:
            np_random = np.random
        self.np_random = np_random
        self.n = n
    def sample(self):
        return self.np_random.randint(self.n)
    def contains(self, x):
        if isinstance(x, int):
            as_int = x
        elif isinstance(x, (np.generic, np.ndarray)) and (x.dtype.kind in np.typecodes['AllInteger'] and x.shape == ()):
            as_int = int(x)
        else:
            return False
        return as_int >= 0 and as_int < self.n
    def __repr__(self):
        return "Discrete(%d)" % self.n
    def __eq__(self, other):
        return self.n == other.n
