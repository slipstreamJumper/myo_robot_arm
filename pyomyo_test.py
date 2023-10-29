# some source code from PerlinWarp pyomyo examples
# https://github.com/PerlinWarp/pyomyo/blob/main/examples/myo_imu_examp.py

import multiprocessing
from pyomyo import Myo, emg_mode
import os
import sys, time
#from raspberrypy.control.myo import Myo

import RPi.GPIO as GPIO


GPIO.setmode(GPIO.BOARD)
GPIO.setup(7, GPIO.OUT)
GPIO.setup(11, GPIO.OUT)
upper = GPIO.PWM(7, 50)
lower = GPIO.PWM(11, 50)

#global vars
gquat = 0
gacc = 0
ggyro = 0

alpha = [-8700, 8700, 2800]
beta = [-3300, 6400, -3250]



def cls():
    # Clear the screen in a cross platform way
    # https://stackoverflow.com/questions/517970/how-to-clear-the-interpreter-console
    os.system('cls' if os.name == 'nt' else 'clear')

#------------- nomalizing inputs of myo --------

def normalize_myo_input(a_i, b_i):
    alpha_norm = ((a_i - alpha[0])/(alpha[1]-alpha[0]))
    beta_norm =  ((b_i - beta[0])/(beta[1]-beta[0]))
    return alpha_norm, beta_norm

def normalize_color_output(a_i, b_i):
    a_color_norm = abs(((a_i - alpha[1])*(255/(alpha[1]-alpha[0]))))
    b_color_norm = abs(((b_i - beta[1]) * (255 / (beta[1] - beta[0]))))
    return a_color_norm, b_color_norm

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

    # Orange logo and bar LEDs
    m.set_leds([255, 0, 0], [255, 0, 0])
    # Vibrate to know we connected okay
    m.vibrate(1)

    """worker function"""
    while True:
        m.run()
    print("Worker Stopped")


# -------- Main Program Loop -----------
if __name__ == "__main__":
    p = multiprocessing.Process(target=worker, args=(q,))
    p.start()

    upper.start(7.5)
    lower.start(7.5)

    try:
        while True:
            while not (q.empty()):
                imu = list(q.get())

                quat, acc, gyro = imu
                if gquat == 0: gquat = quat
                else:
                    print("Global Quat:", gquat)


                print("Quaternions:", quat)
                a_norm, b_norm = normalize_myo_input(quat[0], quat[1])
                print("Normalized: ", a_norm, b_norm)
                a_color_norm, b_color_norm = normalize_color_output(quat[0], quat[1])
                print("Color Norm: ", a_color_norm, b_color_norm)
                m.set_leds([a_color_norm, b_color_norm, 0], [a_color_norm, b_color_norm, 0])
                #print("Acceleration:", acc)
                #print("Gyroscope:", gyro)
                cls()

    except KeyboardInterrupt:
        print("Quitting")
        quit()