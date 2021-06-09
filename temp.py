# -*-coding:utf-8-*-

from mlx90614 import MLX90614

import time
import threading


class TempMonitor(object):
    LOOP_TIME = 1.0

    def __init__(self, print_result=False):
        self.temp = 0
        self.print_result = print_result

    def run_sensor(self):
        sensor = MLX90614()

        while not self._thread.stopped:
            self.temp = sensor.readObjectTemperature()
            if self.print_result:
                print("TEMP:{0}".format(self.temp))
            time.sleep(self.LOOP_TIME)
        sensor.shutdown()

    def start_sensor(self):
        self._thread = threading.Thread(target=self.run_sensor)
        self._thread.stopped = False
        self._thread.start()

    def stop_sensor(self, timeout=2.0):
        self._thread.stopped = True
        self.temp = 0
        self._thread.join(timeout)
