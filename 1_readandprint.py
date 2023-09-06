#This code is for data aquisition of 3-axis accelerometer with NI_DAQ & Chasis 
#DAQmx configuration is needed. For that, You need to install NI-DAQmx and configure your system.
#Threading is used for smooth data printing.

import nidaqmx
import threading

# Define the acquisition parameters
sample_rate = 100  # Set the desired sample rate in samples per second

# Function to continuously read and display data
def read_and_display_data(task):
    try:  
        while True:
            data = task.read(number_of_samples_per_channel=1)
            print("Channel 0:", data[0])
            print("Channel 1:", data[1])
            print("Channel 2:", data[2])
    except KeyboardInterrupt:
        print('Data acquisition stopped by user.')

# Create a data acquisition task
with nidaqmx.Task() as task:
    task.ai_channels.add_ai_voltage_chan("SPMod1/ai0") #Channel0 : SPMod1 is just for an example.
    task.ai_channels.add_ai_voltage_chan("******/ai1") #Channel1
    task.ai_channels.add_ai_voltage_chan("******/ai2") #Channel2
   
    # Configure the sample clock to run continuously
    task.timing.cfg_samp_clk_timing(rate=sample_rate, sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)

    # Start the data acquisition thread for printing data
    print_thread = threading.Thread(target=read_and_display_data, args=(task,))
    print_thread.start()

    # Wait for user input to stop the acquisition
    input("Press Enter to stop the acquisition...\n")

    # Stop the print thread
    print_thread.join()

print("Acquisition stopped.")