import MPRConfig
import usb_cdc

#TODO check if data received from host is actually in the form of readable 
# bytes as outlined in adafruit library
#TODO sanity check if types from various methods actually correspond 
# (binary and hex representation of integers please check especially from
# mpr121.touched())

class TouchInput
    def __init__(self, mprA: MPR121, mprB: MPR121, mprC: MPR121, i2c: I2C) -> None:
        # define mprs
        self.mprA, self.mprB, self.mprC = mprA, mprB, mprC
        self.MPRs = [mprA, mprB, mprC]
        self.i2c = i2c
        self.config_mode = True
        # define commands
        self.RSET  = bytes('E', 'ascii') # E
        self.HALT  = bytes('L', 'ascii') # L
        self.STAT  = bytes('A', 'ascii') # A
        self.Ratio = bytes('r', 'ascii') # r
        self.Sens  = bytes('k', 'ascii') # k

    # main loop
    def loop(self, mprList: list) -> None:
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
    def setTouchscreenRK(self, packet: list) -> None:
        # set ratio for the sensors
        MPRConfig.setSpecificSensorThreshold(packet[2], packet[4], packet[3])
        # excuse the unreadability but this writes the packet into the serial device character by character as bytes encoded as ascii
        # f string evaluates to something along the lines of '(LAr2)' (see readme)
        usb_cdc.data.write(f'({packet[1]}{packet[2]}{packet[3]}{packet[4]})')

    # receving inputs from host
    def receiveCommand(self) -> None:
        packet = [bytes('', 'ascii')] * 6   # self contained data packet to this function
        length = 0
        # read bytes sequentially if available
        while usb_cdc.data.in_waiting:
            read = usb_cdc.data.read()
            if read == bytes('{', 'ascii'):
                length = 0
            if read == bytes('}', 'ascii'):
                break
            length += 1     # increment length corresponding to packet byte
            packet[length] = read   # fill packet with read bytes
            usb_cdc.console.write(f'packet: \n{packet}')
        # which command to run based off received data
        if length == 5:     # check if command received is a config command
            self.i2c.try_lock() # must be in locked mode to config
            if packet[3] == self.RSET:
                self.commandRSET()
            elif packet[3] == self.HALT:
                self.commandHALT()
            elif packet[3] == self.STAT:
                self.commandSTAT()
            elif packet[3] == self.Ratio or packet[3] == self.Sens:
                self.setTouchscreenRK(packet)
            self.i2c.unlock()
        # reset
        length = 0
        packet = [bytes('', 'ascii')] * 6

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
        print(send)     # test print
        send.append(ord(')'))
        # write touch data to host
        usb_cdc.data.write(bytes(send))