from adafruit_mpr121 import MPR121
from MPRAddresses import * # should be fine, only importing variables

def resetMPR(sensor: MPR121) -> None:
    # write to reset register
    writeToRegisterStopped(sensor, MPR121_SOFTRESET, 0x63)

def stopMPR(sensor: MPR121) -> None:
    # write to electrode configuration register to deactivate all 12 electrodes
    writeToRegisterStopped(sensor, MPR121_ECR, 0x0)

def runMPR(sensor: MPR121) -> None:
    # write to electrode configuration register to activate all 12 electrodes
    writeToRegisterStopped(sensor, MPR121_ECR, 0x8f)

def configMPR(sensor: MPR121) -> None:
    # default configuration for registers as outlined by the original Mai2Touch for arduino
    writeToRegisterStopped(sensor, MPR121_MHDR, 0x1)
    writeToRegisterStopped(sensor, MPR121_NHDR, 0x8)
    writeToRegisterStopped(sensor, MPR121_NCLR, 0x1)
    writeToRegisterStopped(sensor, MPR121_FDLR, 0x0)
    writeToRegisterStopped(sensor, MPR121_MHDF, 0x1)
    writeToRegisterStopped(sensor, MPR121_NHDF, 0x1)
    writeToRegisterStopped(sensor, MPR121_NCLF, 0x10)
    writeToRegisterStopped(sensor, MPR121_FDLF, 0x2)
    writeToRegisterStopped(sensor, MPR121_NHDT, 0x0)
    writeToRegisterStopped(sensor, MPR121_NCLT, 0x0)
    writeToRegisterStopped(sensor, MPR121_FDLT, 0x0)
    setThresholds(sensor, 10, 10)
    writeToRegisterStopped(sensor, MPR121_DEBOUNCE, (4 << 4) | 0x2);
    writeToRegisterStopped(sensor, MPR121_CONFIG1, 0x10);
    writeToRegisterStopped(sensor, MPR121_CONFIG2, 1 << 5);
    writeToRegisterStopped(sensor, MPR121_AUTOCONFIG0, 0x0B)
    writeToRegisterStopped(sensor, MPR121_AUTOCONFIG1, (1 << 7));
    writeToRegisterStopped(sensor, MPR121_UPLIMIT, 202);
    writeToRegisterStopped(sensor, MPR121_TARGETLIMIT, 182);
    writeToRegisterStopped(sensor, MPR121_LOWLIMIT, 131);

def writeToRegisterStopped(sensor: MPR121, register, value) -> None: 
    # MPR121 MUST BE IN STOP STATE (ECR 0x0) TO WRITE TO MOST REGISTERS
    sensor._i2c.write(bytes([register, value]))

def setThresholds(sensor: MPR121, touch: int, release: int) -> None:
    # set thresholds for touch and release; not a method in the python library, ported from c arduino
    for i in range(12):
        writeToRegisterStopped(sensor, MPR121_TOUCHTH_0 + 2 * i, touch)
        writeToRegisterStopped(sensor, MPR121_RELEASETH_0 + 2 * i, release)

def setSpecificSensorThreshold(sensor: int, value: int, mpr: MPR121) -> None:
    if sensor < 0x41 or sensor > 0x62:
        return
    elif sensor < 0x4D:

