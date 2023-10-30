# some source code from PerlinWarp pyomyo examples
# https://github.com/PerlinWarp/pyomyo/blob/main/examples/myo_imu_examp.py
# https://toptechboy.com/raspberry-pi-lesson-28-controlling-a-servo-on-raspberry-pi-with-python/

import multiprocessing
from pyomyo import Myo, emg_mode
import os
import sys, time
#from raspberrypy.control.myo import Myo

import RPi.GPIO as GPIO


GPIO.setmode(GPIO.BCM)
GPIO.setup(21, GPIO.OUT)
GPIO.setup(26, GPIO.OUT)
upper = GPIO.PWM(26, 100)
lower = GPIO.PWM(21, 100)

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
    if a_color_norm > 255: a_color_norm = 255
    b_color_norm = abs(((b_i - beta[1]) * (255 / (beta[1] - beta[0]))))
    if b_color_norm > 255: b_color_norm = 255
    return a_color_norm, b_color_norm

def get_normalized_dc(desired_angle):
    return float((1/18)*desired_angle+2)

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
    p = multiprocessing.Process(target=worker, args=(q,))
    p.start()

    upper.start(50)
    lower.start(50)



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
                m.set_leds([int(a_color_norm), int(b_color_norm), int(a_color_norm)], [int(a_color_norm), int(b_color_norm), int(a_color_norm)])
                #print("Acceleration:", acc)
                #print("Gyroscope:", gyro)

                upper.ChangeDutyCycle(get_normalized_dc(int(a_norm)))
                lower.ChangeDutyCycle(get_normalized_dc(int(b_norm)))

                cls()

    except KeyboardInterrupt:
        upper.stop()
        lower.stop()
        GPIO.cleanup()
        print("Quitting")
        quit()