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

## Common Issues

If the script is not connecting the VISA adapter or it is erroring on running an experiment, please double-check the USB connection to the VISA adapter and verify that the PC detects the adapter. Sometimes the USB hub that the adapter is plugged into can be spotty. If the kernel has recently been updated, you may need re-build the NI-VISA driver per the prior directions.
