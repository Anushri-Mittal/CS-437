from sense_hat import SenseHat

sense=SenseHat()
x = 2
y = 4

sense.clear()

sense.set_pixel(x, y, (0, 128, 128))

while True:
    for event in sense.stick.get_events():
        if event.action == 'pressed' and event.direction == 'up':
            if y > 0:
                y -= 1
        if event.action == 'pressed' and event.direction == 'down':
            if y < 7:
                y += 1
        if event.action == 'pressed' and event.direction == 'right':
            if x < 7:
                x += 1
        if event.action == 'pressed' and event.direction == 'left':
            if x > 0:
                x -= 1
        if event.action == 'pressed' and event.direction == 'middle':
            sense.clear()
            exit(0)
        sense.clear()
        sense.set_pixel(x, y, (0, 128, 128))