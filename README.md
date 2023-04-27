# Photodetector IV Sweep Automation

A set of Python GUI's for running IV sweep characterization on photodiodes using a Keithley 6487 Picoammeter.

## Requirements

**NI-VISA Driver**
* Linux: [Linux GPIB Driver](https://linux-gpib.sourceforge.io)

For detailed instructions on installing/updating Linux GPIB driver, see: [National Instruments GPIB-USB-HS + PYVISA on Ubuntu](https://gist.github.com/ochococo/8362414fff28fa593bc8f368ba94d46a)

**Python Dependencies**
* `Python 3.x`
* `pyvisa`
* `pymeasure`
* `numpy`

**To-Do**
* Wrap all of the procedures together in a single interface with the option to
  select which one to launch