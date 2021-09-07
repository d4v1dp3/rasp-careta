from time import sleep
from smbus2 import SMBus, i2c_msg

DATA_OFFSET = 32768
DATA_SCALE = 120.0


class SFM3300(object):

    def __init__(self, channel=1, address=0x40):
        self.address = address
        self.channel = channel
        self.bus = SMBus(self.channel)

        self.reset()
        sleep(1)
        self.setup()
        sleep(0.1)
        self.readRawData()
        sleep(0.01)

    def reset(self):
        msg = i2c_msg.write(self.address, [0x20, 0x00])
        self.bus.i2c_rdwr(msg)

    def setup(self):
        msg = i2c_msg.write(self.address, [0x10, 0x00])
        self.bus.i2c_rdwr(msg)

    def readRawData(self):
        msg = i2c_msg.read(self.address, 3)
        self.bus.i2c_rdwr(msg)
        b = list(msg)
        return (b[0] << 8) | b[1]

    def readFlow(self):
        return (self.readRawData() - DATA_OFFSET) / DATA_SCALE
