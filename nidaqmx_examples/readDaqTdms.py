# Dependencies: https://pypi.org/project/npTDMS/

import os
import numpy as np
from nptdms import TdmsFile
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

task_name = 'VoltageInput'
printToConsole = True
plot = True

with TdmsFile.open(os.getcwd() + '\data.tdms') as tdms_file:
    if plot == True:
        mdates.set_epoch('1970-01-01T00:00:00') # new epoch
        fig, ax = plt.subplots()
        fig.autofmt_xdate()

    group = tdms_file[task_name]
    all_group_channels = group.channels()

    for channel in all_group_channels:
        name = channel.name
        length = len(channel)
        t0 = channel.properties['wf_start_time']
        dt = channel.properties['wf_increment']
        dt_us = np.int32(dt*1000000)
        data = channel[:]

        if printToConsole == True:
            print(name)
            print('Timestmap\t\t\tdata')

        # Build timestamp array for x-axis
        times = np.zeros(length, dtype='datetime64[us]')
        for i in range(length):
            times[i] = t0
            t0 += np.timedelta64(dt_us,'us')

            if printToConsole == True:
                output = ''
                output += str(t0)+'\t'+str(data[i])
                print(output)

        if plot == True:
            ax.plot(times, data, label=name)

    if plot == True:
        xfmt = mdates.DateFormatter('%y-%m-%d %H:%M:%S.%f')
        ax.xaxis.set_major_formatter(xfmt)
        plt.legend()
        plt.show()