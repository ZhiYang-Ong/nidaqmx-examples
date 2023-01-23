import numpy
from datetime import datetime, timedelta
import os

import nidaqmx
from nidaqmx.constants import AcquisitionType, LoggingMode, LoggingOperation
from nidaqmx.stream_readers import AnalogMultiChannelReader

task_name = 'VoltageInput'
with nidaqmx.Task(task_name) as task:
    # Timing settings
    sample_rate = 50
    dt = 1/sample_rate
    number_of_samples_per_channel = 50

    # Trigger settings
    analog_trig_source = "Dev1/ai0"

    # Logging settings
    enable_logging = True
    file_path = os.getcwd() + '\data.tdms'

    chan = task.ai_channels.add_ai_voltage_chan("Dev1/ai0:3")
    channels_name = task.channel_names
    number_of_channels = task.number_of_channels
    task.timing.cfg_samp_clk_timing(
    sample_rate, sample_mode=AcquisitionType.CONTINUOUS)
    task.triggers.start_trigger.cfg_anlg_edge_start_trig(analog_trig_source)

    if enable_logging == True:
        # LOG mode provides the best performance, 
        # remove ChannelReader if you are using LOG mode
        task.in_stream.configure_logging(file_path, LoggingMode.LOG_AND_READ, operation=LoggingOperation.CREATE_OR_REPLACE)

    stream = AnalogMultiChannelReader(task.in_stream)
    dataStream = numpy.zeros((number_of_channels, number_of_samples_per_channel), dtype=numpy.float64)
    dataPrint = numpy.zeros((number_of_samples_per_channel, number_of_channels), dtype=numpy.float64)

    task.start()
    # NI-DAQmx Python does not support t0 from the first sample of waveform, use current start time as t0 instead
    # You can get the actual t0 values from TDMS file.
    t0 = datetime.now()

    try:
        print("Press Ctrl+C to stop")
        print(f'Voltage Data:')
        header = 'Time\t\t\t\t'+'\t'.join([x for x in channels_name])
        print(header)
        while True:
            stream.read_many_sample(dataStream, number_of_samples_per_channel)
            dataPrint = numpy.transpose(dataStream)
            
            output = ''
            for i in range(0,dataPrint.shape[0]):
                output += str(t0)+'\t'+'\t\t'.join(['%0.3f' %x for x in dataPrint[i,:]])+'\n'
                t0 += timedelta(seconds=dt)
            print(output)

    except KeyboardInterrupt:
        pass

    task.stop()