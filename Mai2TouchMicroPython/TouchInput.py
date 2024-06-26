import MPRConfig
import usb_cdc
from adafruit_mpr121 import MPR121
from busio import I2C

#TODO check if data received from host is actually in the form of readable
# bytes as outlined in adafruit library
#TODO sanity check if types from various methods actually correspond
# (binary and hex representation of integers please check especially from
# mpr121.touched())

class TouchInput:
    def __init__(self, mprA: MPR121, mprB: MPR121, mprC: MPR121, i2c: I2C) -> None:
        # define mprs
        self.mprA, self.mprB, self.mprC = mprA, mprB, mprC
        self.MPRs = [mprA, mprB, mprC]
        self.i2c = i2c
        self.config_mode = True
        # define commands
        self.RSET  = 69 # E
        self.HALT  = 76 # L
        self.STAT  = 65 # A
        self.Ratio = 114 # r
        self.Sens  = 107 # k

    # main loop
    def loop(self) -> None:
        self.receiveCommand()
        None if self.config_mode else self.sendInput()

    # define all the commands and what they do to the MPR
    def commandRSET(self) -> None:
        MPRConfig.resetMPR(self.mprA)
        MPRConfig.resetMPR(self.mprB)
        MPRConfig.resetMPR(self.mprC)

    def commandHALT(self) -> None:
        MPRConfig.stopMPR(self.mprA)
        MPRConfig.stopMPR(self.mprB)
        MPRConfig.stopMPR(self.mprC)
        MPRConfig.configMPR(self.mprA)
        MPRConfig.configMPR(self.mprB)
        MPRConfig.configMPR(self.mprC)
        self.config_mode = True

    def commandSTAT(self) -> None:
        self.config_mode = False
        MPRConfig.runMPR(self.mprA)
        MPRConfig.runMPR(self.mprB)
        MPRConfig.runMPR(self.mprC)

    # touchscreen ratio and sensitivity
    def setTouchscreenRK(self, packet: bytearray) -> None:
        # set ratio for the sensors
        MPRConfig.setSpecificSensorThreshold(packet[2], packet[4], packet[3], self.mprA, self.mprB, self.mprC)
        # f string evaluates to something along the lines of '(LAr2)' (see readme)
        usb_cdc.data.write(f'({"".join([chr(char) for char in packet[1:5]])})')

    # receving commands from host / game
    def receiveCommand(self) -> None:
        packet = bytearray(6)   # self contained data packet to this function
        length = 0
        # read bytes sequentially if available
        while usb_cdc.data.in_waiting:
            read = usb_cdc.data.read(1)
            # print(usb_cdc.data.read())
            if not read:
                print("empty")
                continue
            read = read[0]
            #print(read)
            if read == b'{':
                length = 0
            if read == b'}':
                break
            if length < 6:
                packet[length] = read   # fill packet with read bytes
                length += 1     # increment length corresponding to packet byte
        # which command to run based off received data
        if length == 6:     # check if command received is a config command
            usb_cdc.console.write(f'length: {length}, command: {packet[3]}, \n')
            self.i2c.try_lock() # must be in locked mode to config
            if packet[3] == self.RSET:
                usb_cdc.console.write("reset\n")
                self.commandRSET()
            elif packet[3] == self.HALT:
                usb_cdc.console.write("halt\n")
                self.commandHALT()
            elif packet[3] == self.STAT:
                usb_cdc.console.write("stat\n")
                self.commandSTAT()
            elif packet[3] == self.Ratio or packet[3] == self.Sens:
                usb_cdc.console.write("ts set\n")
                self.setTouchscreenRK(packet)
            self.i2c.unlock()
        # reset
        length = 0
        for i in range(6):
            packet[i] = 0

    def sendInput(self) -> None:
        # append all touchdata from each mpr to each other
        touchData = 0
        touchData = (touchData | self.mprC.touched()) << 12  # D7 to E8
        touchData = (touchData | self.mprB.touched()) << 12  # B5 to D6
        touchData = (touchData | self.mprA.touched())    # A1 to B4
        # use bytearray to store touched data, initialise with (
        send = bytearray(b'(')
        # write touch data for every sensor fit into 7 sequential bytes, 5 LSB for each byte
        for b in range(7):
            send.append(touchData & 0b11111)
            touchData >>= 5
        # print(send)     # test print
        send.append(ord(')'))
        # write touch data to host
        usb_cdc.data.write(bytes(send))
