## data packet format
the following data packets are represented by ASCII, and the values are in hexadecimal.

the data packet sent by the host starts with `{` and ends with `}`
the data packet replied by the device starts with `(` and ends with `)`
`>>>` is the data packet sent by the host, `<<<` is the data packet returned by the controller

it seems the data sent can be either length 6 for commands or length 9 for touch data

example:
{from host machine} `7b 4c 42 72 32 7d`
ASCII value: `{LBr2}`
(towards host machine) `28 4c 42 72 32 29`
ASCII Value: `(LBr2)`

## commands and controller initialisation
```c
enum {
  commandRSET  = 0x45,//E
  commandHALT  = 0x4C,//L
  commandSTAT  = 0x41,//A
  commandRatio = 0x72,//r
  commandSens  = 0x6B,//k
};
```

### Reset command (RSET):
```
>>> 7b 52 53 45 54 7d
// ASCII: {RSET}
```
sent from host machine / game, no reply needed. will trigger a reset command to the MPR121:
```c
void cmd_RSET() { // Reset
  MprReset(mprA);
  MprReset(mprB);
  MprReset(mprC);
}

void MprReset(Adafruit_MPR121 cap) {
  cap.writeRegister(MPR121_SOFTRESET, 0x63);
}
```
assumedly this command is to initialize the touchscreen on startup

### Conditioning mode command (HALT)
```
>>> 7b 48 41 4c 54 7d
// ASCII：{HALT}
```
sent from host machine / game, no reply needed. will trigger stop command to the MPR121, and then trigger configuration for the touch sensors (will write sensitivity settings etc)

controller will stay in this mode until STAT command is triggered, and in this mode changing sensor settings is possible (explained more below)
```c
void cmd_HALT() { // Conditioning Mode
  MprStop(mprA);
  MprStop(mprB);
  MprStop(mprC);
  MprConfig(mprA);
  MprConfig(mprB);
  MprConfig(mprC);
  Conditioning = true;
}

void MprStop(Adafruit_MPR121 cap) {
  cap.writeRegister(MPR121_ECR, 0x0);
}

void MprConfig(Adafruit_MPR121 cap) {
  cap.writeRegister(MPR121_MHDR, 1);
  cap.writeRegister(MPR121_NHDR, 8);
  cap.writeRegister(MPR121_NCLR, 1);
  cap.writeRegister(MPR121_FDLR, 0);
  cap.writeRegister(MPR121_MHDF, 1);
  cap.writeRegister(MPR121_NHDF, 1);
  cap.writeRegister(MPR121_NCLF, 16);
  cap.writeRegister(MPR121_FDLF, 2);
  cap.writeRegister(MPR121_NHDT, 0);
  cap.writeRegister(MPR121_NCLT, 0);
  cap.writeRegister(MPR121_FDLT, 0);
  cap.setThresholds(10, 10); // 默认敏感度，会被 MprSetTouch 和 MprSetRelease 修改
  cap.writeRegister(MPR121_DEBOUNCE, (4 << 4) | 2);
  cap.writeRegister(MPR121_CONFIG1, 16);
  cap.writeRegister(MPR121_CONFIG2, 1 << 5);
  cap.writeRegister(MPR121_AUTOCONFIG0, 0x0B);
  cap.writeRegister(MPR121_AUTOCONFIG1, (1 << 7));
  cap.writeRegister(MPR121_UPLIMIT, 202);
  cap.writeRegister(MPR121_TARGETLIMIT, 182);
  cap.writeRegister(MPR121_LOWLIMIT, 131);
}
```

### Touch panel ratio setting 
```c
>>> {[L/R] [sensor] r [ratio]}
>>> 7b 4c 41 72 32 7d
// ASCII：{LAr2}
```

sent from host machine / game. 

`L`: stands for P1 or P2, P1 = L and P2 = R

`sensor`: Sensor being currently set from A1 to E8, refer to the sensor table for ascii representation

`r`: value fixed to hex ascii r, not sure what this means from the original chinese doc

`ratio`: ratio value of each sensor (refer to the sensor sensitivity value table), not exactly sure what this value means with regards to a real controller

with regards to the actual MPR121 itself, the ratio sets the touch sensitivity:

```c
void cmd_Ratio() { // Set Touch Panel Ratio
  MprSetTouch(packet[2], packet[4]); // 敏感度修改，仅作示例，需要根据实际情况修改
  SerialDevice.write('(');
  SerialDevice.write(packet[1]); //L,R
  SerialDevice.write(packet[2]); //sensor
  SerialDevice.write('r');
  SerialDevice.write(packet[4]); // Ratio
  SerialDevice.write(')');
}

void MprSetTouch(uint8_t sensor, uint8_t value) {
  if (sensor < 0x41 | sensor > 0x62) {
    return;
  } else if (sensor < 0x4D) { // A1 ~ B4
    mprA.writeRegister(MPR121_TOUCHTH_0 + 2 * (sensor - 0x41), value);
  } else if (sensor < 0x59) { // B5 ~ D6
    mprB.writeRegister(MPR121_TOUCHTH_0 + 2 * (sensor - 0x4D), value);
  } else { // D7 ~ E8
    mprC.writeRegister(MPR121_TOUCHTH_0 + 2 * (sensor - 0x59), value);
  }
}
```

`MprSetTouch()` sends the new touch sens values to be set to the MPR121, which it gets from the packet that it receives from the controller (referring to the arguments `packet[2]` and `packet[4]`) which is presumably inputted from the sensor menu in the service menu from the game (?)

will reply the same as has just been set in a smooth bracket data packet

### Touch panel sensitivity setting
```c
>>> {[L/R] [sensor] k [sens]}
>>> 7b 4c 41 6b 1e 7d
/// ASCII: {LAk.}
```
Sent from host machine / game. Similar to ratio setting from above

`L`: stands for P1 or P2, P1 = L and P2 = R

`sensor`: Sensor being currently set from A1 to E8, refer to the sensor table for ascii representation

`k`: value fixed to hex ascii k, not sure what this means from the original chinese doc

`sens`: sensitivity value of each sensor (refer to the sensor sensitivity value table), not exactly sure what this value means with regards to a real controller

```c
void cmd_Sens() { // Set Touch Panel Sensitivity
  MprSetRelease(packet[2], packet[4]); // 敏感度修改，仅作示例，需要根据实际情况修改
  SerialDevice.write('(');
  SerialDevice.write(packet[1]); // L,R
  SerialDevice.write(packet[2]); // sensor
  SerialDevice.write('k');
  SerialDevice.write(packet[4]); // Sensitivity
  SerialDevice.write(')');
}

void MprSetRelease(uint8_t sensor, uint8_t value) {
  if (sensor < 0x41 | sensor > 0x62) {
    return;
  } else if (sensor < 0x4D) { // A1 ~ B4
    mprA.writeRegister(MPR121_RELEASETH_0 + 2 * (sensor - 0x41), value);
  } else if (sensor < 0x59) { // B5 ~ D6
    mprB.writeRegister(MPR121_RELEASETH_0 + 2 * (sensor - 0x4D), value);
  } else { // D7 ~ E8
    mprC.writeRegister(MPR121_RELEASETH_0 + 2 * (sensor - 0x59), value);
  }
}
```

exactly the same as touch panel ratio setting

### end conditioning mode
```c
>>> 7b 53 54 41 54 7d
// ASCII: {STAT}
```
exit configuration mode. no reply required, can start sending touch data

## touch data

touch data sent by the controller to the host, will only start sending once the controller receives a STAT command. will stop sending if the controller receives HALT

```c
>>> 28 1f 1f 1f 1f 1f 1f 1f 29
// ASCII: (.......)
```
the touch data lives in the middle 7 bytes of this data packet where each bit in the byte (each byte value uses binary low 5 bit storage) represents the sensor you touched, and the bit value will flip to 1 
example for touching sensor A1:
```c
<<< 28 00 00 00 00 00 00 01 29
// Binary data: 00000000 00000000 00000000 00000000 00000000 00000000 00000001
```


## sensor table
(letters do not refer to keys, only translated to ascii for readability between host and device)
A1=0x41 ~ A8=0x48 (a b c d e f g h)
B1=0x49 ~ B8=0x50 (i j k l m n o p)
C1=0x51   C2=0x52 (q r)
D1=0x53 ~ D8=0x5A (s t u v w x y z)
E1=0x5B ~ E8=0x62 (lwin rwin menu reserved(?) sleep num0 num1 num2)

## sensor sensitivity value table
sens of A1-A8 touch points value, sens value of B1-E8
-5 = 32,5a,46
-4 = 32,50,3c
-3 = 32,46,32
-2 = 32,3c,28
-1 = 32,32,1e
0 = 32,28,14
+1 = 32,1e,0f
+2 = 32,1a,0a
+3 = 32,17,05
+4 = 32,14,01
+5 = 32,0a,01
original chinese doc says that both ratio and sens values (under MPR121 terms ratio = touch threshold and sens = release threshold) use this same table