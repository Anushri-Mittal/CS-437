from sense_hat import SenseHat
import numpy as np
import time
import scipy.signal as signal
from datetime import datetime,date
import matplotlib.pyplot as plt
import pandas as pd
import scipy

import json
import csv
from scapy.all import *


import scipy.integrate as integrate
path="/home/pi/Desktop/IMU/newData/"
sense=SenseHat()

timestamp_fname=datetime.now().strftime("%H:%M:%S")
sense.set_imu_config(True,True,True) ## Config the Gyroscope, Accelerometer, Magnetometer
# filename=path+timestamp_fname+".csv"'
filename = "/home/pi/Downloads/postlab-3.2.csv"

dev_mac = "e4:5f:01:d4:9c:b1"  # Assigned transmitter MAC
iface_n = "wlan1"  # Interface for network adapter
duration = 65  # Number of seconds to sniff for

# store timestamp and direction change
try:
    with open('postlab-3.2.json') as file:
        change_path = json.load(file)
except json.decoder.JSONDecodeError:
    change_path = {}

def captured_packet_callback(pkt):
    with open(filename,"a") as f:
        initial_time = 0
        accel=sense.get_accelerometer_raw()  ## returns float values representing acceleration intensity in Gs
        gyro=sense.get_gyroscope_raw()  ## returns float values representing rotational intensity of the axis in radians per second
        mag=sense.get_compass_raw()  ## returns float values representing magnetic intensity of the ais in microTeslas
    
        x=accel['x']
        y=accel['y']
        z=accel['z']
        timestamp=datetime.now().strftime("%H:%M:%S")
        if initial_time == 0:
            initial_time = time.time()
            change_path[timestamp] = "straight"
                
        cur_dict = {}
        try:
            cur_dict["mac_1"] = pkt.addr1
            cur_dict["mac_2"] = pkt.addr2
            cur_dict["rssi"] = pkt.dBm_AntSignal
        except AttributeError:
            return  # Packet formatting error
        
        if pkt.addr2 == dev_mac:
            cur_dict["rssi"] = -1*np.inf
        entry= timestamp+","+str(time)+","+str(x)+","+str(y)+","+str(z)+ ","+ str(cur_dict["rssi"]) +"\n"
        f.write(entry)
        
        for event in sense.stick.get_events():
            if event.action =="pressed":  ## check if the joystick was pressed
                if event.direction=="right":   ## to check for other directions use "up", "down", "left", "right"
                    change_path[timestamp] = "right"
                elif event.direction=="left":
                    change_path[timestamp] = "left"
                elif event.direction=="up":
                    change_path[timestamp] = "straight"
                elif event.direction=="down":
                    change_path[timestamp] = "back"
   
        
    f.close()
    with open('postlab-3.2.json', 'w') as file:
        json.dump(change_path, file)
        

if __name__ == "__main__":
    
    t = AsyncSniffer(iface=iface_n, prn=captured_packet_callback, store=0)
    t.daemon = True
    t.start()
    
    start_date_time = datetime.now().strftime("%d/%m/%Y,%H:%M:%S.%f") #Get current date and time

    time.sleep(duration)
    t.stop()

    print("Start Time: ", start_date_time)