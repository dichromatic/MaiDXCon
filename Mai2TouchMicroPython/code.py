import adafruit_mpr121
import board
import usb_cdc
import time
from TouchInput import TouchInput
from MPRConfig import configMPR

# here we initialise the MPRs, configurate them based on Mai2Touch spec and then 
# pass it to TouchInput to start listening to the game

# set serial timeout 
usb_cdc.data.timeout = 0

# create i2c bus, get the addresses of the mprs
i2c = board.I2C()
i2c.try_lock()  # lock to scan
addresses = i2c.scan()
i2c.unlock()    # unlock
print(i2c)
print(addresses)

# initialise MPR121 objects out of the i2c bus and the addresses where the mprs are
mprA = adafruit_mpr121.MPR121(i2c, addresses[0])
mprB = adafruit_mpr121.MPR121(i2c, addresses[1])
mprC = adafruit_mpr121.MPR121(i2c, addresses[2])
i2c.try_lock()  # lock to config
print(mprA, mprB, mprC)

# config mprs by spec
configMPR(mprA)
configMPR(mprA)
configMPR(mprA)
i2c.unlock()    # unlock to start touch inputs

# start main touch input loop
touchInput = TouchInput(mprA, mprB, mprC, i2c)
while True:
    touchInput.loop()