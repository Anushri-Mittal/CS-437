from scapy.all import *
import matplotlib.pyplot as plt

initial_packet = 0
packets = []
times = []
idx = 0
for packet in PcapReader('/home/pi/packet_capture2.pcap'):
    if idx == 0:
        initial_packet = packet
        idx += 1
    if packet.haslayer(UDP):
        byte_to_string = bytes(packet[UDP].payload)
        is_alert = True
        alert = b'Motion Detected!'
        j = len(alert)-1
        for i in range(len(byte_to_string)-1, -1, -1):
            if j < 0:
                break
            if alert[j] == byte_to_string[i]:
                j-=1
                continue
            else:
                is_alert = False
                break
        if is_alert == True:
            packets.append(1)
            times.append(packet.time - initial_packet.time)
    # print(packet)

plt.scatter(times, packets)
plt.ylim(0, 1.2)
for i in range(len(packets)):
    plt.axvline(x = times[i], ymin = 0, ymax = 0.83)
plt.xlabel('Timestamp [seconds]')
plt.ylabel('Is motion detected?')
plt.title('Motion Detection Timeline')
plt.show()
    
# subtract first packet time from every packet time