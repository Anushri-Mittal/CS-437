from scapy.all import *
import binascii

previous_time = 0
packet_count = 0
initial_time = 0
idx = 0
for packet in PcapReader('/home/pi/packet_capture3.pcap'):
    if idx == 0:
        initial_time = packet.time
    if packet.haslayer(UDP):
        print(packet.time - initial_time,bytes(packet[UDP].payload))
        byte_to_string = bytes(packet[UDP].payload)
        is_alert = True
        # alert = b'\x4d\6f\x74\x69\x6f\x6e\x20\x44\x65\x74\x65\x63\x74\x65\x64\x21'
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
        # print(is_alert)
        if is_alert == True:
            print("Spy camera detected!")
            break
            #if (packet.time - initial_time - previous_time) > 2:
                #packet_count = 0
                #previous_time = packet.time - initial_time
            #else:
                #packet_count += 1
    idx += 1
