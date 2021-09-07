# -*-coding:utf-8-*-

from max30102 import MAX30102
import threading
#import hrcalc
import hrcalc4 as hrcalc
import time
import numpy as np
from datetime import datetime

class HeartRateMonitor(object):
    LOOP_TIME = 0.04

    def __init__(self, print_raw=False, print_result=False):
        self.bpm = 0
        self.spo2 = 0
        if print_raw is True:
            print('IR, Red')
        if print_result is True:
            print('BPM,SpO2')
        self.print_raw = print_raw
        self.print_result = print_result

    def run_sensor(self):
        sensor = MAX30102()
        ir_data = []
        red_data = []

        #now = datetime.now()
        #dt_string = now.strftime("%d-%m-%Y_%H:%M:%S")
        #f = open("{0}.txt".format(dt_string), "w")
        #f.write("IR,Red\n")
        # run until told to stop
        count = 0
        while not self._thread.stopped:
            # check if any data is available
            num_bytes = sensor.get_data_present()
            if num_bytes > 0:
                # grab all the data and stash it into arrays
                while num_bytes > 0:
                    red, ir = sensor.read_fifo()
                    #f.write("{0},{1}\n".format(ir,red))
                    num_bytes -= 1
                    ir_data.append(ir)
                    red_data.append(red)
                    count += 1
                    if self.print_raw:
                        print("{0}, {1}".format(ir, red))

                while len(ir_data) > 100:
                    ir_data.pop(0)
                    red_data.pop(0)

                if len(ir_data) == 100 and count >= 24:
                    count = 0
                    bpm, valid_bpm, spo2, valid_spo2 = hrcalc.calc_hr_and_spo2(ir_data, red_data)
                    self.bpm = bpm
                    if valid_bpm:
                        if self.print_result:
                            print("BMP:{0}, SPO2:{1}".format(self.bpm, spo2))
                    #else:
                        #if self.print_result:
                            #print("Finger not detected")
                    if valid_spo2:
                        self.spo2 = spo2
                    else:
                        self.spo2 = 0
            time.sleep(self.LOOP_TIME)
        #f.close()
        sensor.shutdown()

    def start_sensor(self):
        self._thread = threading.Thread(target=self.run_sensor)
        self._thread.stopped = False
        self._thread.start()

    def stop_sensor(self, timeout=2.0):
        self._thread.stopped = True
        self.bpm = 0
        self.spo2 = 0
        self._thread.join(timeout)
