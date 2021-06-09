# coding=utf-8
# This is a sample Python script.

from heartrate import HeartRateMonitor
from temp import TempMonitor

import bluetooth
import time

BLUE_PORT = 1


if __name__ == '__main__':
    print('sensor heart rate...')
    hrm = HeartRateMonitor(False, False)
    hrm.start_sensor()

    print('sensor temperature...')
    tmp = TempMonitor(False)
    tmp.start_sensor()

    print('bluetooth service')
    server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

    port = 1
    server_sock.bind(("", port))
    server_sock.listen(1)

    print("waiting....")

    client_sock, address = server_sock.accept()

    print("Accepted connection from ", address)

    error = False
    try:
        while not error:
            print("TMP:{}".format(tmp.temp))
            print("BMP:{0}, SPO2:{1}".format(hrm.bpm, hrm.spo2))

            try:
                client_sock.sendall("#{0},{1},{2},{3},{4},{5},{6},{7},{8}~".format(hrm.spo2, 0, 0, tmp.temp, hrm.bpm, 0, 0, 0, 0))
            except Exception:
                error = True
                print('error socket')
            time.sleep(5)
    except KeyboardInterrupt:
        print('keyboard interrupt detected, exiting...')

    client_sock.close()
    server_sock.close()

    hrm.stop_sensor()
    tmp.stop_sensor()
    print('sensor stoped!')
