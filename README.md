# PicoPyGui
Python GUI for Picoscope to do live analyses or long duration measurements


# Requirements
Hardware
* PC with Linux, Mac, Windows
* Picoscope 3xxxD or 6xxx (probably easy to add further scopes)

Software
* Python3 with the following libraries: matplotlib, numpy
* picoscope SDK from picotech website
* QT5
* PyQT5 (for GUI and threading, it is possible to run without GUI with limited functionality)

# Usage

## Start
With GUI: Start in the Terminal with 
* python3 PicoGui.py [--options]

Without GUI: Change the settings in settings.cfg according to your needs. 
Then start in the Terminal with 
* python3 PicoGui.py -k [--options]

## Operation
* this program always uses rapid block mode as in the presumed operations there is no need for slow data taking
* this program always requires a trigger condition
* Make sure that you see the terminal output during operation and check all errors!


# How to support for add other picoscopes
* copy picoscopeXXXX.py to picoscopeNNNN.py where XXXX is one of the existing scripts and NNNN is the new name
* replaced all psXXXX with psNNNN
* check and possibly add or remove functionality (e.g. DC50 coupling)
* change numbers in timebase functions according to values in the picoscope programmers guide

# Missing features
* Digital Ports on ps3000a not working yet
* this program does not include signal generator functionality

# TODO
* check the min window sizes!
* check 3000 properties
* trigger delay -> understand it
* combine picoscope types to one class with sub-classes implementing the changes

# Currently working on
* check if GUI and threads can be handled better! Implement the main gui file next