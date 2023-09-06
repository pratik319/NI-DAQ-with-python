#This code is for data aquisition of 3-axis accelerometer with NI_DAQ & Chasis 
#DAQmx configuration is needed. For that, You need to install NI-DAQmx and configure your system.
#Threading is used for smooth data printing.

import nidaqmx
import threading
import queue  # Import the queue module

# Define the acquisition parameters
sample_rate = 100  # Set the desired sample rate in samples per second

# Function to continuously read data
def read_data(task):
    try:
        while True:
            data = task.read(number_of_samples_per_channel=1)
            data_queue.put(data)  # Put acquired data into the queue
    except KeyboardInterrupt:
        print('Data acquisition stopped by user.')

# Function to continuously print acquired data
def print_data():
    while True:
        data = data_queue.get()  # Get acquired data from the queue
        print("Channel 0:", data[0])
        print("Channel 1:", data[1])
        print("Channel 2:", data[2])

# Create a data acquisition task
with nidaqmx.Task() as task:
    task.ai_channels.add_ai_voltage_chan("SPMod1/ai0") #Channel0 : SPMod1 is just for an example.
    task.ai_channels.add_ai_voltage_chan("SPMod1/ai1") #Channel1
    task.ai_channels.add_ai_voltage_chan("SPMod1/ai2") #Channel2
   
    # Configure the sample clock to run continuously
    task.timing.cfg_samp_clk_timing(rate=sample_rate, sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)

    # Create a thread for data acquisition
    data_queue = queue.Queue()
    acquisition_thread = threading.Thread(target=read_data, args=(task,))
    acquisition_thread.start()

    # Create a thread for printing acquired data
    print_thread = threading.Thread(target=print_data)
    print_thread.start()

    # Wait for user input to stop the acquisition
    input("Press Enter to stop the acquisition...\n")

    # Stop the acquisition and print threads
    acquisition_thread.join()
    print_thread.join()

print("Acquisition stopped.")