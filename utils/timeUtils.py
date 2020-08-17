import time
import sys
import random


_tick = sys.getswitchinterval()


def sleepWithSwitchInterval(num):
    time.sleep(_tick * random.randint(1, num))
