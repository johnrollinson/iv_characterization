"""
This is an old iteration from before I was using the PyMeasure module
"""

from keithley import K6487
import numpy as np
import time
# import matplotlib.pyplot as plt

# Test setup parameters ###################################################################
polarity = 'anode'      # i.e. which contact is the voltage source connected to
device_name = 'DUT7'    # A unique device identifier
pd_type = 'APD'         # Either APD or PIN
pd_len = '10um'         # 10um, 100um, or 500um
cover = 'nocover'       # Either M1cover or nocover
special = 'test1'       # Any other comments
current_compliance = 1e-6  # Max current limit
###########################################################################################

inst = K6487()
inst.connect()
# inst.initialize(zero_check=True)

inst.configure_vsource(vrange=50)
inst.configure_filter(n=10)
inst.dev.write("curr:nplc 1")           # Set integration time (no. power line cycles)
inst.dev.write("trig:delay:auto on")    # Enable automatic trigger delay (improve accuracy)

inst.dev.write("syst:zch off")
inst.dev.write("sens:ohms on")
inst.vsource_enable()

###########################################################################################
# Reverse Bias Current Measurement
###########################################################################################
for i in range(1):
    # special = 'test' + str(1+i)
    special = '305mA'
    vstop = 0
    if i//5 == 0:
        # current_compliance = 10e-6
        vstop = 8
    elif i//5 == 1:
        # current_compliance = 100e-6
        vstop = 3
    elif i//5 == 2:
        # current_compliance = 1e-3
        vstop = 6
    elif i//5 == 3:
        # current_compliance = 1e-3
        vstop = 8

    if polarity == 'anode':
        start = 0.00
        stop = -vstop
        step = -0.1
    elif polarity == 'cathode':
        start = 0.00
        stop = vstop
        step = 0.1
    else:
        raise ValueError("Polarity must be either 'anode' or 'cathode'")

    vrange = np.arange(start, stop+step, step)
    data = []

    for voltage in vrange:
        inst.voltage = voltage
        meas = inst.read()

        meas = meas.split(',')
        result = float(meas[0].strip("OHMS"))
        curr = voltage/result
        print(voltage, curr)

        if not np.isnan(curr):
            data.append([abs(voltage), abs(curr)])
            if abs(curr) > current_compliance:
                print('Current limit reached - stopping')
                break

    inst.voltage = 0

    data = np.array(data).T
    # plt.figure(1)
    # plt.plot(abs(data[0]), abs(data[1]))
    # plt.yscale('log')
    # plt.title('Reverse Current')
    # plt.show()

    comment = """{:s}
    Start voltage: {:0.2f}
    Stop voltage: {:0.2f}
    Step size: {:0.2f} 
    Reverse Voltage [V], Reverse Current [A]""".format(time.strftime("%b %d %Y %I:%M%p"),
                                                       start, stop, step)

    # fname = input("Enter file name for saving: ")
    fname = '_'.join([device_name, 'dark', 'rev', pd_type, pd_len, cover])
    if special:
        fname += '_{:s}'.format(special)
    timestr = time.strftime("%Y%m%d_%H%M%S")
    np.savetxt('photo_current_940nm/{:s}_{:s}/{:s}_{:s}'.format(pd_type, pd_len,
                                                                fname, timestr), data.T, header=comment)
    # time.sleep(60)

    ###########################################################################################
    # Forward Bias Current Measurement
    ###########################################################################################
    # if polarity == 'anode':
    #     start = 0.00
    #     stop = 0.5
    #     step = 0.01
    # elif polarity == 'cathode':
    #     start = 0.00
    #     stop = -0.5
    #     step = -0.01
    # else:
    #     raise ValueError("Polarity must be either 'anode' or 'cathode'")
    #
    # vrange = np.arange(start, stop+step, step)
    # data = []
    #
    # for voltage in vrange:
    #     inst.voltage = voltage
    #     meas = inst.read()
    #
    #     meas = meas.split(',')
    #     result = float(meas[0].strip("OHMS"))
    #     curr = voltage/result
    #     print(voltage, curr)
    #
    #     if not np.isnan(curr):
    #         data.append([abs(voltage), abs(curr)])
    #         if abs(curr) > current_compliance:
    #             print('Current limit reached - stopping')
    #             break
    #
    # inst.voltage = 0
    #
    # data = np.array(data).T
    # # plt.figure(2)
    # # plt.plot(abs(data[0]), abs(data[1]))
    # # plt.yscale('log')
    # # plt.title('Forward Current')
    #
    # comment = """{:s}
    # Start voltage: {:0.2f}
    # Stop voltage: {:0.2f}
    # Step size: {:0.2f}
    # Forward Voltage [V], Forward Current [A]""".format(time.strftime("%b %d %Y %I:%M%p"),
    #                                                    start, stop, step)
    #
    # # fname = input("Enter file name for saving: ")
    # fname = '_'.join([device_name, 'dark', 'fwd', pd_type, pd_len, cover])
    # if special:
    #     fname += '_{:s}'.format(special)
    # timestr = time.strftime("%Y%m%d_%H%M%S")
    # np.savetxt('voltage_limiting/PIN_500um/{:s}_{:s}'.format(fname, timestr), data.T, header=comment)
    # time.sleep(60)
