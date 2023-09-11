from sense_hat import SenseHat
from time import sleep
import socket

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't even have to be reachable
        s.connect(('10.254.254.254', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

sense=SenseHat()

sense.clear()
sleep(30)

for i in range(0,2):
    sense.show_message(get_ip())

sense.clear()