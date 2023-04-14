from pyvisa import ResourceManager
# from gpib import GpibError
import logging
from pymeasure.instruments import Instrument
# log = logging.getLogger(__name__)


class Keithley6487(Instrument):
    """
    Keithley 6487 Picoammeter
    """
    def __init__(self, resource_name, **kwargs):
        super().__init__(
            resource_name,
            "Keithley 6487",
            **kwargs
        )

    def connect(self):
        # rm = ResourceManager('@py')
        # self. = rm.open_resource('GPIB0::{:d}::INSTR'.format(self.gpib_addr))
        device_id = self.ask('*idn?')
        # print('con')
        if '6487' in device_id:
            logging.info('Successfully connected: '
                             '{}'.format(device_id.strip('\r\n')))
            self.write_termination = '\n'
            return True
        else:
            logging.error('Error connecting to Keithley 6487 - device not found')
            return False

    def initialize(self, zero_check=True):
        self.write("*RST")  # Reset picoammeter

        if zero_check:
            self.write("SYST:ZCH ON")           # Enable zero check
            self.write("RANG 2e-9")             # Set range to 2nA
            # Wait for user to verify open connection
            input("Remove probes from DUT to perform zero-correction, "
                  "then press Enter to continue.")
            self.write("INIT")                  # Start measurement for zero correction
            self.write("SYST:ZCOR:ACQ")         # Use previous reading for zero correction
            self.write("SYST:ZCOR ON")          # Perform zero correction
            self.write("RANG:AUTO ON")          # Enable auto range

            # Wait for user to connect probes to DUT
            input("Zero-correction complete, "
                  "please connect probes to DUT for measurement, "
                  "then press enter to continue.")

        self.write("SYST:ZCH OFF")  # Disable zero check
        self.write("SENS:OHMS ON")  # Enable ohms measurement mode

    def configure_vsource(self, voltage=0, vrange=10, ilim=2.5e-3):
        # set voltage range, current limit
        if vrange in [10, 50, 500]:
            self.write("SOUR:VOLT:RANG {:d}".format(vrange))  # Set voltage range to 50V
        else:
            raise ValueError("Voltage range must be [10,50,500]")
        if abs(voltage) <= vrange:
            self.write("SOUR:VOLT {:0.2f}".format(voltage))  # Set voltage source to 1V
        else:
            raise ValueError("Voltage must be less within vrange")
        if ilim in [25e-6, 250e-6, 2.5e-3, 25e-3]:
            self.write("SOUR:VOLT:ILIM {:0.1e}".format(ilim))  # Set current limit to 25mA
        else:
            raise ValueError("Current limit must be [25e-6, 250e-6, 2.5e-3, 25e-3]")

    def vsource_enable(self):
        self.write('sour:volt:stat on')

    def vsource_disable(self):
        self.write('sour:volt:stat off')

    def read(self):
        result = self.ask("read?")
        return result

    def set_measure_count(self, n):
        self.write("TRIG:COUNT {:d}".format(n))

    def configure_filter(self, mode='rep', n=10, enable=True):
        self.write('aver:coun {:d}'.format(n))
        self.write('aver:tcon {:s}'.format(mode))
        if enable:
            self.write('aver on')
        else:
            self.write('aver off')

    def reset(self):
        self.write('*RST')

    @property
    def id(self):
        device_id = self.ask('*IDN?')
        return device_id

    @property
    def voltage(self):
        volt = self.ask('sour:volt?')
        return float(volt)

    @voltage.setter
    def voltage(self, v: float):
        self.write('sour:volt {:0.2f}'.format(v))



