import common as cm
import movement as mv
import cv2
import numpy as np
from PIL import Image
import time
from threading import Thread
import sys
import serial
import hailo


# from flask import Flask, Response
# from flask import render_template


USB_PORT = "/dev/ttyAMA0"



try:
        usb = serial.Serial(USB_PORT, 9600, timeout= 2)
except:
    print("ERROR - could not open USB serial port. Please check your port name and permissions.")
    print("Exiting program.")
    exit()

