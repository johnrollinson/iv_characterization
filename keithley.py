from pymeasure.instruments import Instrument
from time import sleep
import logging

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class Keithley6487(Instrument):
    """
    Keithley 6487 Picoammeter
    """

    ##############
    # Properties #
    ##############

    # sweep_state = Instrument.measurement(
    #     ":SOUR:VOLT:SWE:STAT?",
    #     """ Query if sweep running: 1 = sweep in progress. """
    # )
    buffer_size = Instrument.measurement(
        ":TRAC:POIN:ACT?",
        """ Returns number of readings actually stored in buffer. """,
    )

    ###########
    # Methods #
    ###########

    def __init__(self, adapter, **kwargs):
        super(Keithley6487, self).__init__(adapter, "Keithley 6487", **kwargs)

    def reset(self):
        self.write("*RST")

    def configure_sweep(self, start, stop, step, n_avg, delay, nplc, polarity):
        self.write("SYST:ZCH OFF")
        log.info("Zero-checking turned off")
        self.write("AVER:COUN {:d}".format(n_avg))
        self.write("AVER:TCON {:s}".format("rep"))
        self.write("AVER ON")
        self.write("SENS:CURR:NPLC {:0.2f}".format(nplc))
        self.write("SOUR:VOLT:SWE:STAR {:0.1f}".format(start))
        # self.write("CURR:RANG 2E-8")    # Set current range to 200nA
        log.info("Sweep start value set")
        if polarity == "Anode":
            self.write("SOUR:VOLT:SWE:STOP {:0.1f}".format(-stop))
        if polarity == "Cathode":
            self.write("SOUR:VOLT:SWE:STOP {:0.1f}".format(stop))
        self.write("SOUR:VOLT:SWE:STEP {:0.2f}".format(step))
        self.write("SOUR:VOLT:SWE:DEL {:0.3f}".format(delay / 1e3))
        self.write("FORM:ELEM ALL")  # Include all elements in the trace data
        self.write(
            "FORM:SREG ASC"
        )  # Set output format of status register to ascii (decimal)
        self.write("ARM:COUN {:d}".format(int(abs((stop - start) / step) + 1)))

    def start_sweep(self):
        self.write("SOUR:VOLT:SWE:INIT")
        self.write("INIT")

    def sweep_state(self):
        self.write("*CLS")
        try:
            resp = int(self.ask("*STB?"))
            resp = resp & 0x80
        except:
            resp = 1
        return resp


if __name__ == "__main__":
    from pymeasure.adapters import VISAAdapter

    adapter = VISAAdapter("GPIB0::22::INSTR", "@py")
    ammeter = Keithley6487(adapter)

    ammeter.reset()
