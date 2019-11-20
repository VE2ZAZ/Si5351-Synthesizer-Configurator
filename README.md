# VE2ZAZ's Si5351 Synthesizer Board Software and Firmware
Software and firmware required to configure the Si5351 chip via an Arduino Nano on the VE2ZAZ Si5351 Synthesizer board

Please see the [About.html]( http://htmlpreview.github.com/?https://github.com/VE2ZAZ/Si5351_Synthesizer_Configurator/About.html) and the [About_Raw.html]( http://htmlpreview.github.com/?https://github.com/VE2ZAZ/Si5351_Synthesizer_Configurator/About_Raw.html) files for all the details on this software package.

Please visit [VE2ZAZ's Website]( http://ve2zaz.net/Si5351_Synth/index.htm) for more information on the VE2ZAZ Si5351 Synthesizer board hardware.

The software allows to configure the Si5351A/C Synthesizer chip when supervised by the Arduino Nano. Once the Arduino has received a configuration from this software, it will re-load the Si5351 chip with that same configuration at every power up or reset. The Arduino (properly configured by this software) is required as the Si5351 chip does not retain its configuration when power is removed; it must be re-configured at power up.

## Computer software (python scripts)
The software is written in Python 2.7 programming language. Thus it is fully compatible with the Linux and Windows (7, 8, 10) operating systems. Although it has not been tested, the software should also run properly on the Mac OS.

The software covers a superset of features offered by the Si5351 family of chips. The user must understand the limits imposed by the Si5351 model (A or C version), such as the number of channels available or the support for an external reference input. A good comprehension of the Silicon Labs' Si5351 Datasheet document is recommended.

The software is actually made of two python scrips. The "Si5351 Synthesizer Configuration" script was designed with the objective of exploiting the most common Si5351 features. Thus, it allows to configure the chip for most applications, but not all of them. Examples of features that are not implemented are VCXO support (the Si5351B chip), phase adjustment (other than simple inversion) and support for output channels 6 and 7. In an application where one or more of the missing features is required, the user can still use this hardware by programming the Arduino Nano using another python script, the "Si5351 Raw data Transfer" program. That Python script is also included in the package. In such case, various Si5351 registers will need to be programmed separately, which is more tedious.

Obviously, the accompanying Arduino firmware (sketch) must be used in conjunction with this software, otherwise the latter will not function. The sketch is designed to interact with both versions of computer python scrips described here.

Access must be granted to the computer's virtual serial port associated with the Arduino's serial-USB adapter, otherwise an error message will be displayed.

This software is “Free software” (as defined by the Free Software Foundation), which means it respects users' freedom and community. The users have the freedom to run, copy, distribute, study, change and improve this software. When modifying the software, a mention of the original author, namely Bert-VE2ZAZ, would be a gracious consideration.

## Arduino firmware (sketch)
The Arduino firmware (a.k.a. the sketch) is written to be compiled in the Arduino IDE environment. The Arduino sketch uses Jason Mildrum's Etherkit Si5351Arduino library (https://github.com/etherkit/Si5351Arduino). That library must be installed in the Arduino IDE via the Library Manager (Menu: Sketch -> Include Library -> Manage Libraries...) prior to compiling the sketch.

The Arduino must be sent an Si5351 configuration from the software described below, otherwise the synthesizer board will not operate.
