# PicoPyGui
Python GUI for Picoscope to do live analyses or long duration measurements


# Requirements
Hardware
* PC with Linux, Mac, Windows
* Picoscope 3xxxD or 6xxx (probably easy to add further scopes)

Software
* Python3 with the following libraries: matplotlib, numpy
* picoscope SDK from picotech website
* PyQT5 (for GUI)

# How to support for add other picoscopes
* copy picoscopeXXXX.py to picoscopeNNNN.py where XXXX is one of the existing scripts and NNNN is the new name
* replaced all psXXXX with psNNNN
* check and possibly add or remove functionality (e.g. DC50 coupling)
* change numbers in timebase functions according to values in the picoscope programmers guide

# Missing features
* Digital Ports on ps3000a not working yet
* this program does not include signal generator functionality

# TODO
* combine picoscope types to one class with sub-classes implementing the changes

# Currently working on
* check if GUI and threads can be handled better! Implement the main gui file next