# some source code from PerlinWarp pyomyo examples
# https://github.com/PerlinWarp/pyomyo/blob/main/examples/myo_imu_examp.py
# https://toptechboy.com/raspberry-pi-lesson-28-controlling-a-servo-on-raspberry-pi-with-python/

import multiprocessing
from pyomyo import Myo, emg_mode
import os
import sys, time
#from raspberrypy.control.myo import Myo

import RPi.GPIO as GPIO

upper = 0
lower = 0

#global vars
gquat = 0
gacc = 0
ggyro = 0

#full arm left and right
alpha = [-8700, 8700, 2800]

#vert motion about elbow
beta = [-1200, 11000, -1199]

# rotation of lower arm
lamb = [-5500, 4000, -1600]


def cls():
    # Clear the screen in a cross platform way
    # https://stackoverflow.com/questions/517970/how-to-clear-the-interpreter-console
    os.system('cls' if os.name == 'nt' else 'clear')

#------------- nomalizing inputs of myo --------

def normalize_myo_input(a_i, b_i, l_i):
    #alpha_norm = ((a_i - alpha[0])/(alpha[1]-alpha[0]))
    alpha_norm = ((a_i - alpha[1])*(180/(alpha[1]-alpha[0])))
    #beta_norm  = ((b_i - beta[0])/(beta[1]-beta[0]))
    beta_norm = ((b_i - beta[1]) * (180 / (beta[1] - beta[0])))
    #lamb_norm  = ((l_i - lamb[0]) / (lamb[1] - lamb[0]))
    lamb_norm = ((l_i - lamb[1])*(180/(lamb[1]-lamb[0])))
    return alpha_norm, beta_norm, lamb_norm

def normalize_color_output(a_i, b_i):
    try:
        a_color_norm = abs(((a_i - alpha[1])*(255/(alpha[1]-alpha[0]))))
        if a_color_norm > 255: a_color_norm = 255
        b_color_norm = abs(((b_i - beta[1]) * (255 / (beta[1] - beta[0]))))
        if b_color_norm > 255: b_color_norm = 255
    except:
        a_color_norm = 1.0
        b_color_norm = 1.0

    return a_color_norm, b_color_norm

def normalize_duty_cycle(a_n_duty, b_n_duty, l_n_duty):
    try:
        a_angle = abs(((a_n_duty + 179) % 360 + 360) % 360 - 179)/10

        if a_angle <= 1: a_angle = 1
        elif a_angle >= 18: a_angle = 17.9

        b_angle = abs(((b_n_duty + 179) % 360 + 360) % 360 - 179)/10

        if b_angle <= 1: b_angle = 1
        elif b_angle >= 18: b_angle = 17.9

        l_angle = abs(((l_n_duty + 179) % 360 + 360) % 360 - 179)/10

        if l_angle <= 1: l_angle = 1
        elif l_angle >= 18: l_angle = 17.9

    except:
        a_angle, b_angle, l_angle = 17.9
    #if a_n_duty <= 0: a_n_duty = 0
    #a_angle = abs(((a_n_duty - alpha[1])*(180/(alpha[1]-alpha[0]))))
    #if a_angle >= 180: a_angle = 179
    #if a_angle <= 0: a_angle = 1
    #a_angle = (1 / 18) * a_angle + 2


    #if b_n_duty <= 0: b_n_duty = 0
    #b_angle = abs(((b_n_duty - beta[1])*(180/(beta[1]-beta[0]))))
    #if b_angle >= 180: b_angle = 179
    #if b_angle <= 0: b_angle = 1
    #b_angle = (1 / 18) * b_angle + 2
    #b_angle = b_angle / 10

    #if l_n_duty <= 0: l_n_duty = 0
    #l_angle = abs(((l_n_duty - lamb[1])*(180/(lamb[1]-lamb[0]))))
    #if l_angle >= 180: l_angle = 179
    #if l_angle <= 0: l_angle = 1
    #l_angle = (1 / 18) * l_angle + 2
    #l_angle = l_angle / 10

    return float(a_angle), float(b_angle), float(l_angle)

def get_normalized_dc(desired_angle):
    try:
        a = float((1/18)*desired_angle+2)
    except:
        a = 11.0

    return int(a)

# ------------ Myo Setup ---------------
q = multiprocessing.Queue()
m = Myo(mode=emg_mode.FILTERED)

def worker(q):
    #m = Myo(mode=emg_mode.FILTERED)
    m.connect()

    def add_to_queue(quat, acc, gyro):
        imu_data = [quat, acc, gyro]
        q.put(imu_data)

    m.add_imu_handler(add_to_queue)
    m.set_leds([255, 0, 0], [255, 0, 0])
    # Vibrate to know we connected okay
    m.vibrate(1)

    """worker function"""
    while True:
        m.run()
    print("Worker Stopped")


# -------- Main Program Loop -----------
if __name__ == "__main__":
    print("Trying to start")


    print("setting pins")
    GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(21, GPIO.OUT)
    GPIO.setup(26, GPIO.OUT)
    upper = GPIO.PWM(26, 50)
    lower = GPIO.PWM(21, 50)

    u = int(sys.argv[1])
    l = int(sys.argv[2])

    upper.start(u)
    lower.start(l)

    for angle in range(4, 181):
        duty = float(angle) / 18 + 2
        print("Duty: " , duty, " | Angle: ", angle)

    #upperChange = 1/18 * (u) + 2
    #lowerChange = 1/18 * (l) + 2

        upper.ChangeDutyCycle(duty)
        lower.ChangeDutyCycle(duty)
    print("updated to starting positions")

    time.sleep(4)

    #upper.ChangeDutyCycle(upperChange)
    #lower.ChangeDutyCycle(lowerChange)

    upper.stop()
    lower.stop()
    GPIO.cleanup()
    print("Quitting")
    quit()