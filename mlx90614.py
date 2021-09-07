from smbus2 import SMBus
import time

class MLX90614():

    MLX90614_TA    = 0x06
    MLX90614_TOBJ1 = 0x07

    def __init__(self, address = 0x5a, bus = 1):
        self.address = address
        self.bus = SMBus(bus)

    def readValue(self, registerAddress):
        error = None
        for i in range(3):
            try:
                return self.bus.read_word_data(self.address, registerAddress)
            except IOError as e:
                error = e
                time.sleep(0.1)
                return 0

    def shutdown(self):
        self.bus.close()

    def valueToCelcius(self, value):
        if value == 0:
            return 0
        return -273.15 + (value * 0.02)

    def readObjectTemperature(self):
        value = self.readValue(self.MLX90614_TOBJ1)
        return self.valueToCelcius(value)

    def readAmbientTemperature(self):
        value = self.readValue(self.MLX90614_TA)
        return self.valueToCelcius(value)