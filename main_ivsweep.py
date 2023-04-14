import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

import sys
import os
from procedures import IVSweepProcedure
from pymeasure.experiment import Results, Worker
from pymeasure.display.Qt import QtGui
from pymeasure.display.windows import ManagedWindow
from pymeasure.experiment.results import unique_filename


class MainWindow(ManagedWindow):

    def __init__(self):
        super(MainWindow, self).__init__(
            procedure_class=IVSweepProcedure,
            inputs=['dev_num', 'pd_type', 'pd_size', 'start', 'stop', 'step', 'delay', 'nplc', 'polarity'],
            displays=['test_num', 'start', 'stop', 'step', 'delay', 'polarity'],
            x_axis='Reverse Voltage',
            y_axis='Reverse Current',
            sequencer=True,
            sequencer_inputs=['test_num'],
            directory_input=True,
        )
        self.setWindowTitle('Reverse Bias IV Sweep')

    def queue(self, *, procedure=None):
        directory = os.getcwd() + '/' + self.directory

        if procedure is None:
            procedure = self.make_procedure()

        # prefix = 'DUT{:s}_{:s}_{:s}_{:s}'.format(
        #     procedure.dev_num.value,
        #     procedure.pd_type.value,
        #     procedure.pd_size.value
        # )
        prefix = str(procedure.dev_num)
        filename = unique_filename(
            directory,
            prefix=prefix+"_",
            # suffix=suffix,
            datetimeformat="%Y%m%d_%H%M%S"
        )

        results = Results(procedure, filename)
        experiment = self.new_experiment(results)

        self.manager.queue(experiment)

    def setup_plot(self, plot):
        # use logarithmic x-axis (e.g. for frequency sweeps)
        plot.setLogMode(y=True)
        plot.showGrid(x=True, y=True)


if __name__ == "__main__":
    # Test setup parameters ###################################################################
    device_name = 'DUT7'    # A unique device identifier
    pd_type = 'APD'         # Either APD or PIN
    pd_len = '10um'         # 10um, 100um, or 500um
    cover = 'nocover'       # Either M1cover or nocover
    special = 'test1'       # Any other comments
    current_compliance = 1e-6  # Max current limit
    ###########################################################################################

    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
