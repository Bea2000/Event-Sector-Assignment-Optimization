import os
import sys


class LockPrint:

    def lock(self):
        self.inital_state = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def unlock(self):
        sys.stdout.close()
        sys.stdout = self.inital_state


def gprint(*x):
    print(f'{" " * 15}{" ".join(x)}')
