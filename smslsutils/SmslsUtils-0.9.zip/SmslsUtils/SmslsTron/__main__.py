from . import SmslsTron 
import time
import math
import string
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation


device = SmslsTron()

loop_iter = 0

def update_actuators():
    global device, loop_iter

    device.update()

    # update laser bits
    if (loop_iter % 10 == 0):
        device.laser_state_tar = not device.laser_state_tar 

    print("Laser state > target: {0}, current: {1}".format(device.laser_state_tar, device.laser_state_curr))

        
    # set new servo position once current target is reached
    servo_pos_reached = abs(device.servo_pos_curr - device.servo_pos_tar) < 1
    if servo_pos_reached or loop_iter == 0:
        device.servo_pos_tar = 15 if device.servo_pos_tar > 90 else 165

    print("Servo Position > target: {0:0.1f} deg, current: {1:0.1f} deg ".format(device.servo_pos_tar, device.servo_pos_curr))


    # set new stirring speed once current target is reached
    stirring_speed_reached = abs(device.stirring_speed_tar - device.stirring_speed_cur) < 1
    if stirring_speed_reached or loop_iter == 0:
        device.stirring_speed_tar = -2000 if device.stirring_speed_tar > 0 else 2000;
    
    print("Stirring Speed > target: {0:0.1f} rpm, current: {1:0.1f} rpm, Run: {2} ".format(device.stirring_speed_tar, device.stirring_speed_cur, device.stirring_is_running))


    # set new temperature values once current target is reached
    temp_dev = abs(device.temper_cur - device.temper_tar);
    temp_thresh = device.temper_tar * 0.05 #(device.temper_tar * 0.02)
    temp_reached = (temp_dev < temp_thresh)
    if  temp_reached: # or loop_iter == 0:
        device.temper_tar = 30 if device.temper_tar > 40 else 50
    
    print("Temp > target: {0:0.3f}, current: {1:0.3f} C, Heat: {2}, Cool: {3}".format(device.temper_tar, device.temper_cur, device.heater_is_running, device.cooler_is_running))
    loop_iter += 1
    


fig, ax = plt.subplots()
line, = ax.plot([], [], lw=2)
ax.grid()
xdata, ydata = [], []

def init_plot():
    ax.set_ylim(10, 45)
    ax.set_xlim(0, 30)
    ax.set_xlabel("Elapsed Time (sec)", fontsize=20)
    ax.set_ylabel("Temperature (C)", fontsize=20)
    ax.set_title("Real-Time Temperature Graph", fontsize=24)
    del xdata[:]
    del ydata[:]
    line.set_data(xdata, ydata)
    return line,

def get_data(t=0):
    while True:
        t += 0.1
        update_actuators()
        y = float(device.temper_cur)
        yield t, y


def run(data):
    # update the plot data
    t, y = data
    xdata.append(t)
    ydata.append(y)

    if (t > 30):
        xdata.pop(0)
        ydata.pop(0)

    ax.set_xlim(xdata[0], xdata[-1])
    ax.figure.canvas.draw()
    line.set_data(xdata, ydata)

    return line,


if __name__ == "__main__":

    print("Starting SmslsTron demo...");
    device.initialize()
    
    ani = animation.FuncAnimation(fig, run, get_data, blit=False, interval=100, repeat=False, init_func=init_plot)
    plt.show()

    device.close()
    print("Finished SmslsTron demo.");
