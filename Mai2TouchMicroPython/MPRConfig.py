from adafruit_mpr121 import MPR121
from MPRAddresses import * # should be fine, only importing variables

def ResetMPR(sensor: MPR121) -> None:
    # write to reset register
    WriteToRegisterStopped(sensor, MPR121_SOFTRESET, 0x63)

def StopMPR(sensor: MPR121) -> None:
    # write to electrode configuration register to deactivate all 12 electrodes
    WriteToRegisterStopped(sensor, MPR121_ECR, 0x0)

def RunMPR(sensor: MPR121) -> None:
    # write to electrode configuration register to activate all 12 electrodes
    WriteToRegisterStopped(sensor, MPR121_ECR, 0x8f)

def ConfigMPR(sensor: MPR121) -> None:
    # default configuration for registers as outlined by the original Mai2Touch for arduino
    WriteToRegisterStopped(sensor, MPR121_MHDR, 0x1)
    WriteToRegisterStopped(sensor, MPR121_NHDR, 0x8)
    WriteToRegisterStopped(sensor, MPR121_NCLR, 0x1)
    WriteToRegisterStopped(sensor, MPR121_FDLR, 0x0)
    WriteToRegisterStopped(sensor, MPR121_MHDF, 0x1)
    WriteToRegisterStopped(sensor, MPR121_NHDF, 0x1)
    WriteToRegisterStopped(sensor, MPR121_NCLF, 0x10)
    WriteToRegisterStopped(sensor, MPR121_FDLF, 0x2)
    WriteToRegisterStopped(sensor, MPR121_NHDT, 0x0)
    WriteToRegisterStopped(sensor, MPR121_NCLT, 0x0)
    WriteToRegisterStopped(sensor, MPR121_FDLT, 0x0)
    setThresholds(sensor, 10, 10)
    WriteToRegisterStopped(sensor, MPR121_DEBOUNCE, (4 << 4) | 0x2);
    WriteToRegisterStopped(sensor, MPR121_CONFIG1, 0x10);
    WriteToRegisterStopped(sensor, MPR121_CONFIG2, 1 << 5);
    WriteToRegisterStopped(sensor, MPR121_AUTOCONFIG0, 0x0B)
    WriteToRegisterStopped(sensor, MPR121_AUTOCONFIG1, (1 << 7));
    WriteToRegisterStopped(sensor, MPR121_UPLIMIT, 202);
    WriteToRegisterStopped(sensor, MPR121_TARGETLIMIT, 182);
    WriteToRegisterStopped(sensor, MPR121_LOWLIMIT, 131);

def WriteToRegisterStopped(sensor: MPR121, register, value) -> None: 
    # MPR121 MUST BE IN STOP STATE (ECR 0x0) TO WRITE TO MOST REGISTERS
    sensor._i2c.write(bytes([register, value]))

def SetThresholds(sensor: MPR121, touch: int, release: int) -> None:
    # set thresholds for touch and release; not a method in the python library, ported from c arduino
    for i in range(12):
        WriteToRegisterStopped(sensor, MPR121_TOUCHTH_0 + 2 * i, touch)
        WriteToRegisterStopped(sensor, MPR121_RELEASETH_0 + 2 * i, release)

def SetSpecificSensorThreshold(sensor: int, value: int, mpr: MPR121) -> None:
    if sensor < 0x41 or sensor > 0x62:
        return
    elif sensor < 0x4D:

