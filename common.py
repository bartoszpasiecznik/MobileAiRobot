import numpy as np
from PIL import Image
import tflite_runtime.interpreter as tflite
import platform
import time
import os
import re
import collections

def time_elapsed(start_time, event):
    time_now = time.time()
    duration = (time_now - start_time) * 1000
    duration = round(duration, 2)
    print(">>> ", duration, " ms (", event, ")")
    