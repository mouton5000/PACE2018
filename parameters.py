import sys
import random

DEBUG = False

if len(sys.argv) > 2:
    SEED = int(sys.argv[2])
else:
    SEED = 4321

random.seed(SEED)
