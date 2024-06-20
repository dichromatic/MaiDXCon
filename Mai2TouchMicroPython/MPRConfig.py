from adafruit_mpr121 import MPR121
from MPRAddresses import * # should be fine, only importing variables
from micropython import const
import board
import busio

# create i2c bus (this implementation uses stemma qt) and assign MPRs
i2c = board.STEMMA_I2C()
addresses = [hex(address) for address in i2c.scan()]
mprA = MPR121(i2c, addresses[0])
mprB = MPR121(i2c, addresses[1])
mprC = MPR121(i2c, addresses[2])

# base instructions to write to the registers on the MPR, similar to the Adafruit MPR121 python library
def resetMPR(mpr: MPR121) -> None:
    # write to reset register
    writeToRegisterStopped(mpr, MPR121_SOFTRESET, 0x63)

def stopMPR(mpr: MPR121) -> None:
    # write to electrode configuration register to deactivate all 12 electrodes
    writeToRegisterStopped(mpr, MPR121_ECR, 0x0)

def runMPR(mpr: MPR121) -> None:
    # write to electrode configuration register to activate all 12 electrodes
    writeToRegisterStopped(mpr, MPR121_ECR, 0x8f)

def configMPR(mpr: MPR121) -> None:
    # default configuration for registers as outlined by the original Mai2Touch for arduino
    writeToRegisterStopped(mpr, MPR121_MHDR, 0x1)
    writeToRegisterStopped(mpr, MPR121_NHDR, 0x8)
    writeToRegisterStopped(mpr, MPR121_NCLR, 0x1)
    writeToRegisterStopped(mpr, MPR121_FDLR, 0x0)
    writeToRegisterStopped(mpr, MPR121_MHDF, 0x1)
    writeToRegisterStopped(mpr, MPR121_NHDF, 0x1)
    writeToRegisterStopped(mpr, MPR121_NCLF, 0x10)
    writeToRegisterStopped(mpr, MPR121_FDLF, 0x2)
    writeToRegisterStopped(mpr, MPR121_NHDT, 0x0)
    writeToRegisterStopped(mpr, MPR121_NCLT, 0x0)
    writeToRegisterStopped(mpr, MPR121_FDLT, 0x0)
    setThresholds(mpr, 10, 10)
    writeToRegisterStopped(mpr, MPR121_DEBOUNCE, (4 << 4) | 0x2);
    writeToRegisterStopped(mpr, MPR121_CONFIG1, 0x10);
    writeToRegisterStopped(mpr, MPR121_CONFIG2, 1 << 5);
    writeToRegisterStopped(mpr, MPR121_AUTOCONFIG0, 0x0B)
    writeToRegisterStopped(mpr, MPR121_AUTOCONFIG1, (1 << 7));
    writeToRegisterStopped(mpr, MPR121_UPLIMIT, 202);
    writeToRegisterStopped(mpr, MPR121_TARGETLIMIT, 182);
    writeToRegisterStopped(mpr, MPR121_LOWLIMIT, 131);

def writeToRegisterStopped(mpr: MPR121, register: int, value: int) -> None: 
    # MPR121 MUST BE IN STOP STATE (ECR 0x0) TO WRITE TO MOST REGISTERS
    mpr._i2c.write(bytes([register, value]))

def setThresholds(mpr: MPR121, touch: int, release: int) -> None:
    # set thresholds for touch and release; not a method in the python library, ported from c arduino
    for i in range(12):
        writeToRegisterStopped(mpr, MPR121_TOUCHTH_0 + 2 * i, touch)
        writeToRegisterStopped(mpr, MPR121_RELEASETH_0 + 2 * i, release)

def setSpecificSensorThreshold(sensor: int, value: int, typ: str) -> None:
    # set type of threshold either release or touch (ratio or sens)
    if typ == 'r':
        thresholdType = MPR121_RELEASETH_0
    else: 
        thresholdType = MPR121_TOUCHTH_0
    # set sensor threshold but depends on which one is at which MPR out of the three
    if sensor < 0x41 or sensor > 0x62:  # sanity check
        return
    elif sensor < 0x4D: # for sensors A1 to B4, assigned to the 12 electrodes of the first MPR
        writeToRegisterStopped(mprA, thresholdType + 2 * (sensor - 0x41), value)
    elif sensor < 0x59: # for sensors B5 to D6 including C1 and C2, assigned to the 12 electrodes of the second MPR
        writeToRegisterStopped(mprB, thresholdType + 2 * (sensor - 0x4D), value)
    else: # for sensors D7 to E8, assigned to the 10 electrodes of the third MPR
        writeToRegisterStopped(mprC, thresholdType + 2 * (sensor - 0x59), value)


