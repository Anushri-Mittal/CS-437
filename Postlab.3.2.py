from sense_hat import SenseHat
import numpy as np
import time
import scipy.signal as signal
from datetime import datetime,date
import matplotlib.pyplot as plt
import pandas as pd
import scipy

import json


import seaborn as sns # visualization


import scipy.integrate as integrate
path="/home/pi/Desktop/IMU/newData/"
sense=SenseHat()

timestamp_fname=datetime.now().strftime("%H:%M:%S")
sense.set_imu_config(True,True,True) ## Config the Gyroscope, Accelerometer, Magnetometer
# filename=path+timestamp_fname+".csv"'
filename = "/home/pi/Downloads/postlab-3.2.csv"

# store timestamp and direction change
try:
    with open('/home/pi/Downloads/postlab-3.2.json') as file:
        change_path = json.load(file)
except json.decoder.JSONDecodeError:
    change_path = {}

## CSV file template:
# time in seconds, timestamp (H:M:S), X-Acceleration, Y-Acceleration, Z-Acceleration



df =pd.read_csv(filename, header=None)
df=df.dropna()

timestamp = df[0]
x_axis=df[2]
y_axis=df[3]
z_axis=df[4]

## Visualize your Accelerometer Values
plt.plot(x_axis)
plt.plot(y_axis)
plt.plot(z_axis)
plt.show()



## CALIBERATION
# caliberate x,y,z to reduce the bias in accelerometer readings. Subtracting it from the mean means that in the absence of motion, the accelerometer reading is centered around zero to reduce the effect of integrigation drift or error.
# change the upper and lower bounds for computing the mean where the RPi is in static position at the begining of the experiment (i.

x_calib_mean = np.mean(x_axis[10:800])
x_calib = x_axis - x_calib_mean
x_calib = x_calib[:]
timestamp = timestamp[:]

y_calib_mean = np.mean(y_axis[10:800])
y_calib = y_axis - y_calib_mean
y_calib = y_calib[:]
timestamp = timestamp[:]

z_calib_mean = np.mean(z_axis[0:1])
z_calib = z_axis - z_calib_mean
z_calib = z_calib[:]
timestamp = timestamp[:]

plt.plot(x_calib)
plt.plot(y_calib[10:])
plt.plot(z_axis)

plt.show()

accel_raw = np.linalg.norm(np.array([x_calib, y_calib, z_calib]), axis=0)
accel = scipy.signal.savgol_filter(accel_raw, window_length=11, polyorder=4) ## Same as rolling average --> Savitzky-Golay smoothing
## change the window size as it seems fit. If you keep window size too high it will not capture the relevant peaks/steps

# Plot the original and smoothed data
plt.figure(figsize=(10, 6))
plt.subplot(2, 1, 1)
plt.plot(accel_raw)
plt.title("Original Data")
plt.subplot(2, 1, 2)
plt.plot(accel)
plt.title("Smoothed Data")
plt.show()


## Step Detection: The instantaneous peaks in the accelerometer readings correspond to the steps. We use thresholding technique to decide the range of peak values for step detection
# Set a minimum threshold (e.g., 1.0) for peak detection

# = 0.16
min_threshold = 0.2  ## Change the threshold (if needed) based on the peak accelerometer values that you observe in your plot above

# Calculate the upper threshold for peak detection as the maximum value in the data
upper_threshold = np.max(accel)

# Define the range for peak detection
my_range = (min_threshold, upper_threshold)

# print("range of Accel. values  for peak detection",my_range)
## Visualize the detected peaks in the accelerometer readings based on the selected range
plt.plot(accel)
peak_array, _ = signal.find_peaks(accel, height=my_range, distance=5)
plt.plot(peak_array, accel[peak_array], "x", color="r")
plt.show()

print("Accel values at high peaks-->", accel[peak_array])

print("Peak array indices are", peak_array)

# Extract  the timestamps corresponding to detected peaks
# timestamp_for_peaks = df[0][peak_array]
# rssi_for_peaks = df[5][peak_array]

timestamp_for_peaks = []
rssi_for_peaks = []

for i in range(len(peak_array)):
    timestamp_for_peaks.append(df.iloc[peak_array[i],0])
    rssi_for_peaks.append(df.iloc[peak_array[i],5])

# Create a new DataFrame with timestamp and peak values
peaks_df = pd.DataFrame({'Timestamp': timestamp_for_peaks, 'PeakValue': accel[peak_array], 'RSSI':rssi_for_peaks})
print("Peaks_df is", peaks_df)

# Set the orientation/direction of motion (walking direction).
# walking_direction is an angle in degrees with global frame x-axis. It can be from 0 degrees to 360 degrees.
# for e.g. if walking direction is 90 degrees, user is walking in the positive y-axis direction.
# Assuming you are moving along the +X-axis with minor deviations/drifts in Y, we set the orientation to 5 (ideally it should be 0 but to take into account the drifts we keep 5)
# Additionally, we assume that the walking direction will be the same throught the trajectory that you capture in this exercise.
walking_dir = np.deg2rad(1) ## deg to radians





# To compute the step length, we estimate it to be propertional to the height of the user.
height=1.57 # in meters
step_length= 0.53 # in meters

# Convert walking direction into a 2D unit vector representing motion in X, Y axis:
angle = np.array([np.cos(walking_dir), np.sin(walking_dir)])


## Start position of the user i.e. (0,0)
cur_position = np.array([0.0, 0.0], dtype=float)
t = []

time_idx = 0
curr_dir = "straight"
walking_dir = np.deg2rad(0)
angle = np.array([np.cos(walking_dir), np.sin(walking_dir)])

# print(change_path)

max_rssi = -1*np.inf
best_pos = 0

for i in range(len(peaks_df)):
    # print(cur_position, angle)
    t.append([cur_position,peaks_df.iloc[i,2]])
    
    # last turn
    if time_idx < len(change_path)-1:
        if peaks_df.iloc[i,0] > list(change_path.keys())[time_idx+1]:
            time_idx += 1
            curr_dir = change_path[list(change_path.keys())[time_idx]]
    
    if curr_dir == "straight":
        walking_dir = np.deg2rad(0)
        angle = np.array([np.cos(walking_dir), np.sin(walking_dir)])
        cur_position = cur_position + step_length * angle
    elif curr_dir == "right":
        walking_dir = np.deg2rad(270)
        angle = np.array([np.cos(walking_dir), np.sin(walking_dir)])
        cur_position = cur_position + step_length * angle
    elif curr_dir == "left":
        walking_dir = np.deg2rad(90)
        angle = np.array([np.cos(walking_dir), np.sin(walking_dir)])
        cur_position = cur_position + step_length * angle
    elif curr_dir == "back":
        walking_dir = np.deg2rad(180)
        angle = np.array([np.cos(walking_dir), np.sin(walking_dir)])
        cur_position = cur_position + step_length * angle
    
    if peaks_df.iloc[i,2] > max_rssi:
        max_rssi = peaks_df.iloc[i,2]
        best_pos = cur_position

#t = np.array(t)
print("Trajectory positions are---------------------------->", t)
print(max_rssi, best_pos)

plt.scatter(4.24,0.53,color="green",label="Actual location")
plt.scatter(t[-1][0][0],t[-1][0][1],color="red",label="Estimated location")
plt.xlim(0,t[-1][0][0]+1)
plt.ylim(0,t[-1][0][1]+1)
plt.legend()
plt.show()

        



