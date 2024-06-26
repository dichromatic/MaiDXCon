# Maimai DX Controller
Adapted from https://github.com/Sucareto/Mai2Touch for CircuitPython based microcontrollers

Changes are to adapt to the Adafruit CircuitPython libraries.

## DTR setting for C# programs
Unfortunately Maimai does not set the DTR to true for serial communication, so it does not work out of the box with some certain microcontroller serial device implementations such as circuitpython. I have shipped a MelonLoader mod for the game to enable the DTR flag and this makes sure that it will work with any serial device implementation on any microcontroller. Make sure to install MelonLoader on the game executable and then drop the mod .dll into the Mods folder.
