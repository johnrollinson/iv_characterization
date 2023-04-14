import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

import sys
import os
from procedures import PhotoCurrentSweepProcedure
from pymeasure.experiment import Results
from pymeasure.display.Qt import QtGui
from pymeasure.display.windows import ManagedWindow
from pymeasure.experiment.results import unique_filename


class MainWindow(ManagedWindow):

    def __init__(self):
        super(MainWindow, self).__init__(
            procedure_class=PhotoCurrentSweepProcedure,
            inputs=[
                'dev_num', 'pd_type', 'pd_size', 'start', 'stop', 'step', 'polarity', 'source_current'
            ],
            displays=['test_num', 'start', 'stop', 'step', 'polarity', 'source_current'],
            x_axis='Reverse Voltage Dark',
            y_axis='Reverse Current Dark',
            sequencer=True,
            sequencer_inputs=['test_num', 'source_current'],
            directory_input=True,
        )
        self.setWindowTitle('Photo Current Sweep')

    def queue(self, *, procedure=None):
        directory = os.getcwd() + '/' + self.directory

        if procedure is None:
            procedure = self.make_procedure()

        prefix = str(procedure.dev_num)
        filename = unique_filename(
            directory,
            prefix=prefix + "_",
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
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
