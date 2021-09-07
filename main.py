# coding=utf-8
# This is a sample Python script.

from heartrate import HeartRateMonitor
from temp import TempMonitor
from resp import RespMonitor

import bluetooth
import time
import numpy as np

BLUE_ENABLE = True
BLUE_PORT = 1

if __name__ == '__main__':

    #print('sensor heart rate...')
    hrm = HeartRateMonitor(False, False)
    hrm.start_sensor()

    #print('sensor temperature...')
    tmp = TempMonitor(False)
    tmp.start_sensor()

    #print('sensor flow...')
    resp = RespMonitor(False)
    resp.start_sensor()

    if BLUE_ENABLE:
        print('bluetooth service')
        server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

        port = 1
        server_sock.bind(("", port))
        server_sock.listen(1)

        print("waiting....")

        while True:
            try:
                client_sock, address = server_sock.accept()

                print("Accepted connection from ", address)

                error = False

                while not error:
                    print("TMP:{0} RESP{1}:".format(tmp.temp, resp.frec))
                    print("BMP:{0}, SPO2:{1}".format(hrm.bpm, hrm.spo2))

                    try:
                        client_sock.sendall(
                            "#{0},{1},{2},{3},{4},{5},{6},{7},{8}~".format(hrm.spo2,
                                                                           int(resp.frec),
                                                                           0,
                                                                           tmp.temp,
                                                                           int(hrm.bpm),
                                                                           0,
                                                                           0,
                                                                           0,
                                                                           0))
                    except Exception:
                        error = True
                        print('error socket')
                    time.sleep(5)
                client_sock.close()
            except KeyboardInterrupt:
                print('keyboard interrupt detected, exiting...')
                break

        server_sock.close()
    else:
         for i in range(0,60):
            print("TMP:{0}, BMP:{1}, SPO2:{2}, RESP:{3}".format(tmp.temp, hrm.bpm, hrm.spo2, resp.frec))

            time.sleep(1)

    hrm.stop_sensor()
    tmp.stop_sensor()
    resp.stop_sensor()
    print('sensor stoped!')
