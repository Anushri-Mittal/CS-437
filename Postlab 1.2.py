from sense_hat import SenseHat
from time import sleep
import matplotlib.pyplot as plt
from datetime import datetime

sense=SenseHat()

#total_temperature = 0
#num_obs = 0

temperatures = []
rounded_temp = []
average_temp = []
times = []

for i in range(0,1000):
    temp = sense.get_temperature()
    temperatures.append(temp)
    rounded_temp.append(round(temp,1))
    average_temp.append(sum(temperatures)/len(temperatures))
    times.append(datetime.now())

#print(rounded_temp)
#print(average_temp)
#print(temperatures)

plt.plot(times, temperatures, color='r', label='Original temperature')
plt.plot(times, average_temp, color='g', label='Average temperature')
plt.xlabel('Time')
plt.ylabel('Temperature')
plt.title('Temperature vs. Time')
plt.legend()
plt.show()