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
(NOT TESTED!)
* python3 PicoGui.py -k [--options]

## Operation
* this program always uses rapid block mode as in the presumed operations there is no need for slow data taking
* this program always requires a trigger condition
* make sure that you see the terminal output during operation and check all errors!
* make sure that one set of captures takes at least 1 sec. Then the time uncertainty is < 1%. This issue arises from the time interval in which the app checks if the picoscope is done with getting the set of captures. It is set to 0.1 millisecond. Our investigation shows that a modern pc should be very accurate down to 10 microsecond, but this seems to busy for this app.
* the deadtime of the 3406D seems to be around 2.2 microseconds, see below. This means that you cannot take rate measurements for > TODO Hz. 
* data is not automatically directly saved. The user can decide when stopping the measurement. However, after 1 hour the data is saved hourly automatically. Per measurement a new directory is created and data and figures are saved there.
* you can choose to terminate measurement after a certain number of minutes. If you choose 0 min, the measurement will continue until you manually stop
* all values of the tab "Display" can be changed live during a run, so all values can be checked live
* user log entries can be entered anytime in the text input above the start/stop button

# How to add external hardware 

In order to measure with external sensors, apart from the picoscope, within the same program and display the results on the same time axis, you need to provide a script which outputs the values once executed. 
Search in the code for the string ”HWT" to find all locations where you need to add special code in order to add your external sensors.

# How to measure deadtime
* TODO

# How to support for add other picoscopes
* copy picoscopeXXXX.py to picoscopeNNNN.py where XXXX is one of the existing scripts and NNNN is the new name
* replaced all psXXXX with psNNNN
* check and possibly add or remove functionality (e.g. DC50 coupling)
* change numbers in timebase functions according to values in the picoscope programmers guide

# Major changes from previous version
This is the previous version: https://github.com/Annalein214/picogui
It grow to large and was hard to maintain. New version should be simpler with even more features.
* sleeptime for a run is set to 0.1ms instead of 1ms in order to improve accuracy for the rate measurement
* time is exchanged by time_ns in order to improve accuracy for the rate measurement

# Missing features (please contect me for more items)
* Digital Ports on ps3000a not working yet
* this program does not include signal generator functionality

# Todo list (please contect me for more items)
* test konsole mode
* check 3000 properties
* combine picoscope types to one class with sub-classes implementing the changes
* plots live verändern möglich machen
* fft currently disabled
* check pyqtgraph, could be nicer




