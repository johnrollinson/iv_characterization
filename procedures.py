import logging
import os

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

from pymeasure.experiment import Procedure, Worker, Results
from pymeasure.experiment import (
    BooleanParameter,
    IntegerParameter,
    FloatParameter,
    ListParameter,
    Parameter,
)
from pymeasure.adapters import VISAAdapter
from pymeasure.log import console_log
from time import sleep
import numpy as np
from keithley import Keithley6487
from agilent import E364A


class IVSweepProcedure(Procedure):

    # Number of sweeps to perform
    test_num = IntegerParameter("Sweep Number", default=1)
    start = FloatParameter("Start Voltage", minimum=0, units="V", default=0.0)
    stop = FloatParameter("Stop Voltage", minimum=0, units="V", default=2.0)
    step = FloatParameter(
        "Step Voltage", minimum=0.001, units="V", default=0.05
    )
    polarity = ListParameter(
        "Polarity", choices=["Anode", "Cathode"], default="Anode"
    )

    dev_num = Parameter("DUT")

    # Optional sweep config setting
    config_toggle = BooleanParameter("Sweep Config", default=False)
    delay = FloatParameter(
        "Trigger Delay", units="ms", default=10, group_by="config_toggle"
    )
    n_avg = IntegerParameter(
        "N Filter Averages", minimum=1, default=3, group_by="config_toggle"
    )
    nplc = IntegerParameter(
        "Integration Time",
        units="NPLC",
        maximum=10,
        minimum=0.1,
        default=1,
        group_by="config_toggle",
    )

    DATA_COLUMNS = ["Reverse Voltage", "Reverse Current", "Timestamp", "Status"]

    def __init__(self):
        super().__init__()
        self.picoammeter = None

    def startup(self):
        """
        Connect to source and configure voltage sweep
        :return:
        """
        log.info("Connecting and configuring the instrument ...")
        adapter = VISAAdapter(
            "GPIB0::22::INSTR", visa_library="@py", query_delay=0.1
        )
        self.picoammeter = Keithley6487(adapter)
        self.picoammeter.reset()
        self.picoammeter.configure_sweep(
            self.start,
            self.stop,
            self.step,
            self.n_avg,
            self.delay,
            self.nplc,
            self.polarity,
        )
        log.info("Configuration complete.")

    def execute(self):
        """
        Initiate an IV sweep on a Keithley 6487 Picoammeter
        :return:
        """
        log.info("Initiating sweep")
        self.picoammeter.start_sweep()
        log.info("Sweep started")
        in_progress = 1
        sleep(2)
        log.info("Waiting for sweep to complete")
        while in_progress:  # Check status of sweep every 100msec
            in_progress = self.picoammeter.sweep_state()
            # print(in_progress)
            # in_progress = 0
            if self.should_stop():
                self.picoammeter.write("SOUR:VOLT:SWE:ABOR")
                break
            sleep(1)
        log.info("Sweep completed, retrieving data")
        trace_data_dark = self.picoammeter.ask(":TRAC:DATA?").replace("A", "")
        n_samples = int(self.picoammeter.buffer_size)
        trace_data_dark = np.fromstring(trace_data_dark, sep=",").reshape(
            (n_samples, 4)
        )
        [
            self.emit(
                "results",
                {
                    "Reverse Voltage": abs(trace_data_dark[i, 3]),
                    "Reverse Current": abs(trace_data_dark[i, 0]),
                    "Timestamp": trace_data_dark[i, 1],
                    "Status": trace_data_dark[i, 2],
                },
            )
            for i in range(n_samples)
        ]
        log.info("Data emitted")


class PhotoCurrentSweepProcedure(Procedure):

    # Number of sweeps to perform
    test_num = IntegerParameter("Sweep Number", default=1)
    start = FloatParameter("Start Voltage", minimum=0, units="V", default=0.0)
    stop = FloatParameter("Stop Voltage", minimum=0, units="V", default=2.0)
    step = FloatParameter(
        "Step Voltage", minimum=0.001, units="V", default=0.05
    )
    polarity = ListParameter(
        "Polarity", choices=["Anode", "Cathode"], default="Cathode"
    )

    dev_num = Parameter("DUT")

    # Optional sweep config setting
    config_toggle = BooleanParameter("Sweep Config", default=True)
    delay = FloatParameter(
        "Trigger Delay", units="ms", default=10, group_by="config_toggle"
    )
    n_avg = IntegerParameter(
        "N Filter Averages", minimum=1, default=3, group_by="config_toggle"
    )
    nplc = IntegerParameter(
        "Integration Time",
        units="NPLC",
        maximum=10,
        minimum=0.1,
        default=1,
        group_by="config_toggle",
    )

    source_current = FloatParameter(
        "Optical Source Current", units="mA", maximum=300
    )

    DATA_COLUMNS = [
        "Reverse Voltage Dark",
        "Reverse Current Dark",
        "Timestamp Dark",
        "Status Dark",
        "Reverse Voltage Light",
        "Reverse Current Light",
        "Timestamp Light",
        "Status Light",
    ]

    def __init__(self):
        super().__init__()
        self.picoammeter = None
        self.power_supply = None

    def startup(self):
        """
        Connect to source and configure voltage sweep
        :return:
        """
        log.info("Connecting and configuring the picoammeter ...")
        adapter = VISAAdapter(
            "GPIB0::22::INSTR", visa_library="@py", query_delay=0.1
        )
        self.picoammeter = Keithley6487(adapter)
        self.picoammeter.reset()
        self.picoammeter.configure_sweep(
            start=self.start,
            stop=self.stop,
            step=self.step,
            n_avg=self.n_avg,
            delay=self.delay,
            nplc=self.nplc,
            polarity=self.polarity,
        )
        log.info("Picoammeter configuration complete.")
        log.info("Connecting to power supply and configuring")
        adapter = VISAAdapter("GPIB0::5::INSTR", visa_library="@py")
        self.power_supply = E364A(adapter)
        self.power_supply.reset()
        self.power_supply.apply(5, self.source_current / 1e3)
        self.power_supply.enabled = "OFF"

    def execute(self):
        """
        Initiate an IV sweep on a Keithley 6487 Picoammeter
        :return:
        """
        log.info("Initiating dark current sweep")
        self.picoammeter.start_sweep()
        log.info("Sweep started")
        in_progress = 1
        sleep(2)
        log.info("Waiting for sweep to complete")
        while in_progress:  # Check status of sweep every 100msec
            in_progress = self.picoammeter.sweep_state()
            if self.should_stop():
                self.picoammeter.write("SOUR:VOLT:SWE:ABOR")
                break
            sleep(1)
        log.info("Dark current sweep completed, retrieving data")
        trace_data_dark = self.picoammeter.ask(":TRAC:DATA?").replace("A", "")
        n_samples = int(self.picoammeter.buffer_size)
        trace_data_dark = np.fromstring(trace_data_dark, sep=",").reshape(
            (n_samples, 4)
        )
        log.debug(trace_data_dark)

        # Enable light source and wait for it to warm up
        log.info("Enabling and triggering power supply")
        self.power_supply.enabled = "ON"
        self.power_supply.trigger()
        warm_up = 1
        while (
            warm_up
        ):  # Allow light source to warm up for 30sec, triggering every sec to update voltage
            sleep(1)
            self.power_supply.trigger()
            warm_up += 1
            if warm_up > 30:
                warm_up = 0

        # Perform photo current sweep
        log.info("Initiating photo current sweep")
        self.picoammeter.start_sweep()
        log.info("Sweep started")
        in_progress = 1
        sleep(2)
        log.info("Waiting for sweep to complete")
        while in_progress:  # Check status of sweep every 1sec
            in_progress = self.picoammeter.sweep_state()
            if self.should_stop():
                self.picoammeter.write("SOUR:VOLT:SWE:ABOR")
                break
            sleep(1)
        log.info("Photo current sweep completed, retrieving data")
        trace_data_light = self.picoammeter.ask(":TRAC:DATA?").replace("A", "")
        n_samples = int(self.picoammeter.buffer_size)
        trace_data_light = np.fromstring(trace_data_light, sep=",").reshape(
            (n_samples, 4)
        )
        log.debug(trace_data_light)
        [
            self.emit(
                "results",
                {
                    "Reverse Voltage Dark": abs(trace_data_dark[i, 3]),
                    "Reverse Current Dark": abs(trace_data_dark[i, 0]),
                    "Timestamp Dark": trace_data_dark[i, 1],
                    "Status Dark": trace_data_dark[i, 2],
                    "Reverse Voltage Light": abs(trace_data_light[i, 3]),
                    "Reverse Current Light": abs(trace_data_light[i, 0]),
                    "Timestamp Light": trace_data_light[i, 1],
                    "Status Light": trace_data_light[i, 2],
                },
            )
            for i in range(n_samples)
        ]
        log.info("Current data emitted")
        log.info("Turning off light source")
        self.power_supply.enabled = "OFF"

        os.system("play -nq -t alsa synth {} sine {}".format(0.25, 400))


if __name__ == "__main__":
    console_log(log, level=logging.DEBUG)

    procedure = IVSweepProcedure()
    procedure.polarity = "Anode"
    # procedure.step = 1

    data_filename = "example.csv"
    results = Results(procedure, data_filename)

    worker = Worker(results)
    worker.start()

    worker.join(timeout=3600)  # wait at most 1 hr (3600 sec)
