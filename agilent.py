import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_range, strict_discrete_set


class E364A(Instrument):
    """
    Agilent E3648A Dual Output DC Power Supply
    """
    ##############
    # Properties #
    ##############
    voltage = Instrument.control(
        ":VOLT?", ":VOLT %0.2f",
        """ Voltage output of the power supply """,
        validator=strict_range,
        values=[0, 20.0]
    )
    current = Instrument.control(
        ":CURR?", ":CURR %0.2f",
        """ Current output of the power supply """,
        validator=strict_range,
        values=[0, 5.0]
    )
    output = Instrument.control(
        "INST:SEL?", "INST:SEL $s",
        """ Which power supply output is to be used (OUTP1 or OUTP2) """,
        validator=strict_discrete_set,
        values=["OUTP1", "OUTP2"]
    )
    enabled = Instrument.control(
        "OUTP?", "OUTP %s",
        """ Enable or disable power supply output """,
        validator=strict_discrete_set,
        values=["ON", "OFF"]
    )

    ###########
    # Methods #
    ###########
    def __init__(self, adapter, **kwargs):
        super(E364A, self).__init__(
            adapter, "Agilent E3648", **kwargs
        )

    def reset(self):
        self.write("*RST")

    def apply(self, voltage, current):
        self.write("APPL {:0.2f}, {:0.2f}".format(voltage, current))

    def trigger(self):
        self.write("TRIG:SOUR IMM")
        self.write("INIT")

    # def __del__(self):
    #     try:
    #         self.dev.close()
    #     except GpibError as m:
    #         print("caught")



# if __name__ == "__main__":
#
