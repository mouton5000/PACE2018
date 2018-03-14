import sys
import random
import time

DEBUG = False

if len(sys.argv) > 2:
    SEED = int(sys.argv[2])
else:
    SEED = 4321

random.seed(SEED)

_START_TIME = time.time()
_MAX_TIME = 120


def timer_end():
    return time.time() - _START_TIME > _MAX_TIME