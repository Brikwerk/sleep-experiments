import time
import math
import random
import multiprocessing as mp
from multiprocessing import Process, Value


def stress(idx, exit_value):
    print(f"Starting Stress on CPU {idx}")
    while bool(exit_value.value) is not True:
        math.sqrt(random.getrandbits(32))


class StressTest():

    def __init__(self):
        self.exit_value = Value('b', False, lock=False)

    def start(self):
        for i in range(0, mp.cpu_count()):
            Process(target=stress, args=(i, self.exit_value)).start()
    
    def stop(self):
        self.exit_value.value = True


if __name__ == "__main__":
    stest = StressTest()
    stest.start()
    time.sleep(10)
    stest.stop()