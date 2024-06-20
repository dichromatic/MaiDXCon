import MPRConfig
import usb_cdc

#TODO check if data received from host is actually in the form of readable 
# bytes as outlined in adafruit library
#TODO sanity check if types from various methods actually correspond 
# (binary and hex representation of integers please check especially from
# mpr121.touched())

# define commands
RSET  = bytes('E', 'ascii') # E
HALT  = bytes('L', 'ascii') # L
STAT  = bytes('A', 'ascii') # A
Ratio = bytes('r', 'ascii') # r
Sens  = bytes('k', 'ascii') # k

# define data packet for configuration mode
packet = [bytes('', 'ascii')] * 6
config_mode = True

# enable serial port
usb_cdc.enable(console = True, data = True)
usb_cdc.data.timeout(0)
MPRs = [MPRConfig.mprA, MPRConfig.mprB, MPRConfig.mprC]

# main loop
def loop() -> None:
    receiveCommand()
    None if config_mode else sendInput()

# define all the commands and what they do to the MPR
def commandRSET() -> None:
    for mpr in MPRs:
        MPRConfig.resetMPR(mpr)

def commandHALT() -> None:
    for mpr in MPRs:
        MPRConfig.stopMPR(mpr)
    for mpr in MPRs:
        MPRConfig.configMPR(mpr)
    config_mode = True

def commandSTAT() -> None:
    config_mode = False
    for mpr in MPRs:
        MPRConfig.runMPR(mpr)

# touchscreen ratio and sensitivity
def setTouchscreenRK() -> None:
    # set ratio for the sensors
    MPRConfig.setSpecificSensorThreshold(packet[2], packet[4], packet[3])
    # excuse the unreadability but this writes the packet into the serial device character by character as bytes encoded as ascii
    # f string evaluates to something along the lines of '(LAr2)' (see readme)
    usb_cdc.data.write(bytes(f'({packet[1]}{packet[2]}{packet[3]}{packet[4]})'), 'ascii')

# receving inputs from host
def receiveCommand() -> None:
    length = 0
    # read bytes sequentially if available
    while usb_cdc.data.in_waiting():
        read = usb_cdc.data.read()
        if read == bytes('{', 'ascii'):
            length = 0
        if read == bytes('}', 'ascii'):
            break
        length += 1     # increment length corresponding to packet byte
        packet[length] = read   # fill packet with read bytes
        usb_cdc.console.write(bytes(f'packet: \n{packet}'))
    # which command to run based off received data
    if length == 5:
        if packet[3] == RSET:
            commandRSET()
        elif packet[3] == HALT:
            commandHALT()
        elif packet[3] == STAT:
            commandSTAT()
        elif packet[3] == Ratio or packet[3] == Sens:
            setTouchscreenRK()
    # reset
    length = 0
    packet = [bytes('', 'ascii')] * 6

def sendInput() -> None:
    # get all touch data simultaneously from mpr.touched(), leftshift by 12 will give 1-12 which one has been touched
    touchData = 0
    touchData = (touchData | mprC.touched()) << 12  # D7 to E8
    touchData = (touchData | mprB.touched()) << 12  # B5 to D6
    touchData = (touchData | mprA.touched())    # A1 to B4

    # write touch data to host
    usb_cdc.data.write(bytes('(', 'ascii'))
    # write touch data for every sensor fit into 7 sequential bytes, 5 LSB for each byte
    for b in range(7):
        usb_cdc.data.write(bytes(touchData & 0b11111))
        touchData >>= 5
    usb_cdc.data.write(bytes(')', 'ascii'))