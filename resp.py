import threading
from sfm3300 import SFM3300
import breatrate
import time
import numpy as np

class RespMonitor(object):
    LOOP_TIME = 0.1

    def __init__(self, print_raw=False, print_result=False):
        self.frec = 0.0
        self.flow = 0
        self.print_raw = print_raw
        self.print_result = print_result

    def run_sensor(self):
        sensor = SFM3300()
        flow_data = np.zeros(200).tolist()

        if self.print_raw is True:
            print('RESP')

        while not self._thread.stopped:
            self.flow = sensor.readFlow()

            flow_data.append(self.flow)
            if self.print_raw:
                print("{0}".format(self.flow))

            while len(flow_data) > 200:
                flow_data.pop(0)

            #if False:
            if len(flow_data) == 200:
                self.frec = breatrate.frequency_breath(flow_data)

            time.sleep(self.LOOP_TIME)



    def start_sensor(self):
        self._thread = threading.Thread(target=self.run_sensor)
        self._thread.stopped = False
        self._thread.start()

    def stop_sensor(self, timeout=2.0):
        self._thread.stopped = True
        self.frec = 0
        self._thread.join(timeout)