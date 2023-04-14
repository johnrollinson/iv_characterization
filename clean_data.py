import numpy as np
from os import listdir

# This script is for removing the negative voltage/current values depending on how the DUT was biases

for fname in listdir('nov2020_v2_data/reverse_dark_current'):
    dname = fname.split('_')
    if 'DUT2' in dname:
        data = np.loadtxt('reverse_dark_current/{:s}'.format(fname))
        with open('reverse_dark_current/{:s}'.format(fname)) as infile:
            header = infile.readlines()
            for i in range(len(header)):
                if not header[i].startswith('#'):
                    del header[i:]
                    break
            header = [line.strip('# ') for line in header]
            header.append('Reverse Voltage [V], Reverse Current [A]')
        header = ''.join(header)
        data = abs(data)
        np.savetxt('reverse_dark_current/{:s}'.format(fname), data, header=header)