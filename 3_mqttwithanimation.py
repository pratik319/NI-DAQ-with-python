#This code is for data aquisition of 3-axis accelerometer with NI_DAQ & Chasis 
#DAQmx configuration is needed. For that, You need to install NI-DAQmx and configure your system.
#Threading is used for smooth data printing.
#Matplotlib, PAHO MQTT, Numpy are required.
# Only one axis used in this code.

import nidaqmx
import threading
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import deque
import paho.mqtt.client as mqtt
import queue

# Define the acquisition parameters
sample_rate = 100  # Set the desired sample rate in samples per second
buffer_size = 1000  # Number of points to display in the animation

# Initialize data buffers
time_buffer = deque(maxlen=buffer_size)
acceleration_buffer = deque(maxlen=buffer_size)

# MQTT broker settings
broker_address = 'localhost'  # Replace with your MQTT broker address
broker_port = 1883  # Replace with your MQTT broker port
username = 'Admin'  # Replace with your MQTT broker username
password = 'admin123'  # Replace with your MQTT broker password
topic = 'Acceleration'

# Function to continuously read data
def read_acceleration(task, data_queue):
    try:
        while True:
            data = task.read(number_of_samples_per_channel=1)
            time_buffer.append(time_buffer[-1] + 1 / sample_rate if time_buffer else 0)
            acceleration_buffer.append(data[0])
            data_queue.put(data[0])
    except KeyboardInterrupt:
        print('Data acquisition stopped by user.')

# Function to update the animation
def update_animation(frame):
    line.set_data(time_buffer, acceleration_buffer)
    current_time = time_buffer[-1] if time_buffer else 0
    ax.set_xlim(current_time - buffer_size / sample_rate, current_time)

    # Update x-axis tick labels
    ax.set_xticks(np.arange(current_time - buffer_size / sample_rate, current_time, step=1))
    ax.set_xticklabels([f'{t:.1f}' for t in np.arange(current_time - buffer_size / sample_rate, current_time, step=1)])

    return line,

# MQTT on_connect callback
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print('Connected to MQTT broker.')
    else:
        print(f'Connection to MQTT broker failed with code {rc}.')

# MQTT send_data function
def send_data(client, data_queue):
    client.username_pw_set(username, password)
    client.connect(broker_address, broker_port)
    client.loop_start()

    try:
        while True:
            acceleration = data_queue.get()
            client.publish(topic, acceleration)
    except KeyboardInterrupt:
        print('Data sending stopped by user.')
    finally:
        client.disconnect()
        client.loop_stop()

# Create a data acquisition task
with nidaqmx.Task() as task:
    task.ai_channels.add_ai_voltage_chan("SPMod1/ai0")

    # Configure the sample clock to run continuously
    task.timing.cfg_samp_clk_timing(rate=sample_rate, sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)

    # Start the data acquisition in a separate thread
    data_queue = queue.Queue()
    acquisition_thread = threading.Thread(target=read_acceleration, args=(task, data_queue))
    acquisition_thread.start()

    # Set up the plot for animation
    fig, ax = plt.subplots()
    line, = ax.plot([], [])
    ax.set_ylim(-10, 10)
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Acceleration (m/s^2)')

    def start_animation():
        anim = FuncAnimation(fig, update_animation, frames=10000, interval=1000 / sample_rate, blit=True)
        plt.show()

    # Start the MQTT client for sending data
    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_connect
    send_data_thread = threading.Thread(target=send_data, args=(mqtt_client, data_queue))
    send_data_thread.start()

    try:
        # Run the animation directly in the main thread
        start_animation()

        # Wait for user input to stop the acquisition
        input("Press Enter to stop the acquisition...\n")

    finally:
        # Stop the task and the acquisition thread
        task.stop()
        acquisition_thread.join()

        # Stop the MQTT data sending thread
        mqtt_client.disconnect()
        mqtt_client.loop_stop()
        send_data_thread.join()

print("Acquisition stopped.")